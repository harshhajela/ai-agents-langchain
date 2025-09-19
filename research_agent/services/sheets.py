from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

import gspread

from research_agent.app.deps import settings, logger

_client: gspread.Client | None = None


def _get_client() -> gspread.Client | None:
    global _client
    if _client is not None:
        return _client

    if not settings.google_service_account_json:
        logger.info("Google service account JSON not configured; Sheets disabled.")
        return None

    try:
        sa_info = json.loads(settings.google_service_account_json)
        _client = gspread.service_account_from_dict(sa_info)
        return _client
    except Exception as e:
        logger.error(f"Failed to init Google Sheets client: {e}")
        return None


def _get_worksheet():
    client = _get_client()
    if client is None:
        return None
    if not settings.gspread_sheet_id:
        logger.info("gspread_sheet_id not configured; Sheets disabled.")
        return None
    try:
        sh = client.open_by_key(settings.gspread_sheet_id)
        try:
            ws = sh.worksheet(settings.gspread_worksheet)
        except gspread.WorksheetNotFound:
            # create worksheet if missing
            ws = sh.add_worksheet(title=settings.gspread_worksheet, rows=1000, cols=4)
            ws.append_row(["created_at", "query", "final_summary", "sources_json"])
        return ws
    except Exception as e:
        logger.error(f"Failed to open worksheet: {e}")
        return None


def append_research_result(data: Dict[str, Any]) -> None:
    ws = _get_worksheet()
    if ws is None:
        return
    try:
        created_at = datetime.utcnow().isoformat()
        sources = data.get("sources", [])
        ws.append_row(
            [
                created_at,
                data.get("query", ""),
                data.get("final_summary", ""),
                json.dumps(sources),
            ]
        )
    except Exception as e:
        logger.error(f"Failed to append to Google Sheets: {e}")


def read_research_history(limit: int = 20) -> List[Dict[str, Any]]:
    ws = _get_worksheet()
    if ws is None:
        return []
    try:
        rows = ws.get_all_records()  # list of dicts keyed by header
        # most recent at bottom; return last N
        recent = rows[-max(1, min(limit, 100)) :]
        items: List[Dict[str, Any]] = []
        for r in reversed(recent):
            sources_json = r.get("sources_json") or "[]"
            try:
                sources = json.loads(sources_json)
            except Exception:
                sources = []
            items.append(
                {
                    "query": r.get("query", ""),
                    "final_summary": r.get("final_summary", ""),
                    "sources": sources,
                    "created_at": r.get("created_at"),
                }
            )
        return items
    except Exception as e:
        logger.error(f"Failed to read from Google Sheets: {e}")
        return []
