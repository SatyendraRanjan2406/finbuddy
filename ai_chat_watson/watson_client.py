import json
import logging
from typing import Dict, List, Optional, Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_config() -> Dict[str, str]:
    return {
        "api_key": getattr(settings, "WATSON_ORCHESTRATION_API_KEY", None),
        "base_url": getattr(settings, "WATSON_ORCHESTRATION_URL", None),
        "project_id": getattr(settings, "WATSON_ORCHESTRATION_PROJECT_ID", None),
        "agent_id": getattr(settings, "WATSON_ORCHESTRATION_AGENT_ID", None),
    }


def send_watson_chat(
    messages: List[Dict[str, str]],
    context: Optional[Dict[str, Any]] = None,
    temperature: float = 0.2,
) -> str:
    """
    Call IBM Watson AI Orchestration to get a chat reply.
    The payload is kept generic; adjust `base_url` and fields to match the deployed agent spec.
    """
    cfg = _get_config()
    missing = [k for k, v in cfg.items() if not v]
    if missing:
        raise RuntimeError(f"Missing Watson orchestration settings: {', '.join(missing)}")

    url = f"{cfg['base_url'].rstrip('/')}/v1/responses"
    payload = {
        "project_id": cfg["project_id"],
        "agent_id": cfg["agent_id"],
        "input": {"messages": messages},
        "context": context or {},
        "config": {"temperature": temperature},
    }
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }

    logger.info("Calling Watson orchestration agent")
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Try common response shapes; keep fallback to raw JSON.
    text = (
        data.get("output_text")
        or data.get("result")
        or data.get("output", {}).get("text")
        or data.get("answer")
    )
    if text:
        return text

    logger.warning("Unexpected Watson response shape; returning raw JSON")
    return json.dumps(data)

