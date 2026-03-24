import json
from datetime import datetime, timezone
from pathlib import Path


DEBUG_LOG_PATH = Path(r"d:\more\razum-more-hack\.cursor\debug.log")


def _log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "id": f"log_{datetime.now(timezone.utc).timestamp()}_{hypothesis_id}",
        "runId": "run-2",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
    }
    # region agent log
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
    # endregion


class DebugApiTraceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):
            match = getattr(request, "resolver_match", None)
            _log(
                "H1",
                "events-project/debug_middleware.py:31",
                "API request start",
                {
                    "method": request.method,
                    "path": request.path,
                    "url_name": getattr(match, "url_name", None),
                },
            )
        try:
            response = self.get_response(request)
        except Exception as exc:  # pragma: no cover
            _log(
                "H2",
                "events-project/debug_middleware.py:45",
                "Unhandled API exception",
                {"path": request.path, "exception_type": type(exc).__name__},
            )
            raise

        if request.path.startswith("/api/"):
            match = getattr(request, "resolver_match", None)
            _log(
                "H5",
                "events-project/debug_middleware.py:56",
                "API request finish",
                {
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "url_name": getattr(match, "url_name", None),
                    "view_name": getattr(match, "view_name", None),
                },
            )
        return response
