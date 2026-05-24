from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_bearer_token
from app.db.session import get_session
from app.mcp.tools import TOOL_DEFINITIONS, call_tool

router = APIRouter(dependencies=[Depends(require_bearer_token)])


def _result(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


@router.post("/mcp")
async def mcp_endpoint(request: Request, session: AsyncSession = Depends(get_session)):
    payload = await request.json()
    response = await _handle_json_rpc(payload, session)
    return JSONResponse(response, media_type="application/json")


async def _handle_json_rpc(payload: dict | list, session: AsyncSession):
    if isinstance(payload, list):
        return [await _handle_json_rpc(item, session) for item in payload]
    method = payload.get("method")
    request_id = payload.get("id")
    params = payload.get("params") or {}

    try:
        if method == "initialize":
            return _result(
                request_id,
                {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "yorumla-mcp", "version": "0.1.0"},
                },
            )
        if method == "notifications/initialized":
            return _result(request_id, {})
        if method == "tools/list":
            return _result(request_id, {"tools": TOOL_DEFINITIONS})
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments") or {}
            content = await call_tool(tool_name, arguments, session)
            return _result(request_id, {"content": [{"type": "text", "text": _json_text(content)}], "isError": False})
        return _error(request_id, -32601, f"Method not found: {method}")
    except Exception as exc:  # noqa: BLE001
        return _result(request_id, {"content": [{"type": "text", "text": str(exc)}], "isError": True})


def _json_text(data: Any) -> str:
    import json

    return json.dumps(data, ensure_ascii=False, indent=2)
