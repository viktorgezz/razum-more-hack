import json
import time
from pathlib import Path
from uuid import uuid4


class DebugRequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_path = Path("/home/daniil/Рабочий стол/учеба/razum-more-hackdd/.cursor/debug-f74f35.log")

    def __call__(self, request):
        response = self.get_response(request)
        # region agent log
        payload = {
            "sessionId": "f74f35",
            "runId": "pre-fix",
            "hypothesisId": "H_REQ",
            "id": f"log_{uuid4().hex}",
            "location": "events-project/debug_logging_middleware.py:__call__",
            "message": "HTTP request processed",
            "data": {
                "path": request.path,
                "method": request.method,
                "status_code": getattr(response, "status_code", None),
                "user_id": getattr(request.user, "id", None),
                "is_authenticated": bool(getattr(request.user, "is_authenticated", False)),
                "is_staff": bool(getattr(request.user, "is_staff", False)),
            },
            "timestamp": int(time.time() * 1000),
        }
        with self.log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, ensure_ascii=False) + "\n")
        # endregion
        return response
