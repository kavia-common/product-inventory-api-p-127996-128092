import hashlib
import hmac
import json
import logging
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.db import get_db
from ..core.security import require_roles
from ..models.webhook import Webhook
from ..schemas.webhook import WebhookCreate, WebhookUpdate, WebhookOut

logger = logging.getLogger(__name__)
router = APIRouter()


def _sign(payload: dict, secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


# PUBLIC_INTERFACE
@router.post("", summary="Create webhook", response_model=WebhookOut, dependencies=[Depends(require_roles("admin", "manager"))])
def create_webhook(payload: WebhookCreate, db: Session = Depends(get_db)):
    """This is a public function."""
    wh = Webhook(**payload.model_dump())
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh


# PUBLIC_INTERFACE
@router.get("", summary="List webhooks", response_model=List[WebhookOut], dependencies=[Depends(require_roles("admin", "manager", "viewer"))])
def list_webhooks(db: Session = Depends(get_db)):
    """This is a public function."""
    return db.query(Webhook).all()


# PUBLIC_INTERFACE
@router.patch("/{webhook_id}", summary="Update webhook", response_model=WebhookOut, dependencies=[Depends(require_roles("admin", "manager"))])
def update_webhook(webhook_id: int, payload: WebhookUpdate, db: Session = Depends(get_db)):
    """This is a public function."""
    wh = db.get(Webhook, webhook_id)
    if not wh:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(wh, k, v)
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh


# PUBLIC_INTERFACE
@router.delete("/{webhook_id}", summary="Delete webhook", dependencies=[Depends(require_roles("admin"))])
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """This is a public function."""
    wh = db.get(Webhook, webhook_id)
    if not wh:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(wh)
    db.commit()
    return {"message": "deleted"}


# PUBLIC_INTERFACE
@router.post("/{webhook_id}/trigger", summary="Trigger webhook manually", dependencies=[Depends(require_roles("admin", "manager"))])
def trigger_webhook(webhook_id: int, event: str, db: Session = Depends(get_db)):
    """This is a public function."""
    wh = db.get(Webhook, webhook_id)
    if not wh or not wh.is_active:
        raise HTTPException(status_code=404, detail="Webhook not found or inactive")
    payload = {"event": event}
    headers = {}
    settings = get_settings()
    secret = wh.secret or settings.WEBHOOK_SIGNATURE_SECRET
    headers["X-Signature"] = _sign(payload, secret)
    with httpx.Client(timeout=5.0) as client:
        try:
            resp = client.post(wh.url, json=payload, headers=headers)
            logger.info("Webhook %s triggered: status=%s", wh.name, resp.status_code)
            return {"status_code": resp.status_code}
        except Exception as e:
            logger.exception("Failed to trigger webhook %s: %s", wh.name, e)
            raise HTTPException(status_code=502, detail="Failed to call webhook")
