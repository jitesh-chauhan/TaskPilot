from typing import Any, Dict, Optional
import logging

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


async def api_handler(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> Any:
    base_url = "http://127.0.0.1:8003/api/v1"

    url = f"{base_url}/{endpoint.lstrip('/')}"
    headers = {}

    if token:
        headers[settings.JWT_SECRET_KEY] = token

    logger.info(
        "API request started | method=%s url=%s params=%s",
        method.upper(),
        url,
        params,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method.upper(),
                url=url,
                params=params,
                headers=headers,
                json=body,
                timeout=10.0,
            )

            logger.info(
                "API response received | status=%s url=%s",
                response.status_code,
                url,
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.warning(
                "API error response | status=%s url=%s response=%s",
                e.response.status_code,
                url,
                e.response.text,
            )
            return e.response.json()

        except Exception as e:
            logger.error(
                "API connection error | url=%s error=%s",
                url,
                str(e),
                exc_info=True,
            )
            return {"data": [], "message": str(e), "status": "failed"}
