"""Department gradebook HTTP service."""

import http.server
import json
import logging
import sys
from collections.abc import Callable
from typing import Any

from errors import ConflictError, GradebookError, NotFoundError, ValidationError
from models import Mark, parse_mark, parse_student
from rules import ensure_weight_fits

DATA = "gradebook.json"
DEFAULT_PORT = 8000
STATE: dict[str, Any] = {"students": {}, "assessments": {}, "marks": []}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def load() -> None:
    """Load gradebook state from JSON file."""
    global STATE
    try:
        with open(DATA, encoding="utf-8") as f:
            STATE = json.load(f)
    except FileNotFoundError:
        STATE = {"students": {}, "assessments": {}, "marks": []}


def save() -> None:
    """Save gradebook state to JSON file."""
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(STATE, f, indent=2)


def get_students() -> list[dict[str, Any]]:
    """Return list of all students."""
    return list(STATE["students"].values())


def get_student(sid: str) -> dict[str, Any]:
    """Return a single student by ID."""
    if sid not in STATE["students"]:
        raise NotFoundError(f"Student '{sid}' not found.")

    st = STATE["students"][sid].copy()
    student_marks = [m for m in STATE["marks"] if m["student"] == sid]

    if not student_marks:
        st["percentage"] = "0"
        return st

    total_earned = 0.0
    total_possible = 0.0
    for m in student_marks:
        aid = m["assessment"]
        if aid in STATE["assessments"]:
            total_earned += float(m["score"])
            total_possible += float(STATE["assessments"][aid]["total"])

    if total_possible > 0:
        student_pct = (total_earned / total_possible) * 100
        st["percentage"] = str(round(student_pct, 2))
    else:
        st["percentage"] = "0"

    return st


def get_assessments() -> list[dict[str, Any]]:
    """Return list of all assessments."""
    return list(STATE["assessments"].values())


def pct(sid: str) -> str:
    """Return a student's weighted percentage formatted to two decimals."""
    if sid not in STATE["students"]:
        return "0"

    student_marks = [m for m in STATE["marks"] if m["student"] == sid]
    if not student_marks:
        return "0"

    total_earned = 0.0
    total_possible = 0.0
    for m in student_marks:
        aid = m["assessment"]
        if aid in STATE["assessments"]:
            assessment = STATE["assessments"][aid]
            score = float(m["score"])
            total = float(assessment["total"])
            weight = float(assessment["weight"])
            if total > 0:
                total_earned += (score / total) * weight
            total_possible += weight

    if total_possible > 0:
        return str(round(total_earned, 2))
    return "0"


def get_report() -> list[dict[str, Any]]:
    """Generate summary report for all students."""
    res = []
    for sid in STATE["students"]:
        st = get_student(sid)
        res.append({"id": st["id"], "name": st["name"], "pct": st.get("percentage", "0")})
    return res


def add_student(payload: Any) -> dict[str, Any]:
    """Add a new student."""
    st = parse_student(payload)
    if st.id in STATE["students"]:
        raise ConflictError(f"Student with id '{st.id}' already exists.")

    data = {"id": st.id, "name": st.name}
    STATE["students"][st.id] = data
    save()
    return data


def add_assessment(
    state: dict[str, Any],
    assessment: dict[str, Any],
    save_func: Callable[[], None],
) -> None:
    """Add a new assessment after verifying it doesn't duplicate IDs or exceed weight limits."""
    assessment_id = assessment.get("id")
    assessments_store = state.get("assessments", {})

    if isinstance(assessments_store, dict):
        existing_list = list(assessments_store.values())
    else:
        existing_list = assessments_store

    for existing in existing_list:
        if existing.get("id") == assessment_id:
            raise ConflictError(f"Assessment with id '{assessment_id}' already exists.")

    existing_weights = [float(a.get("weight", 0)) for a in existing_list]
    new_weight = float(assessment.get("weight", 0))
    ensure_weight_fits(existing_weights, new_weight)

    if isinstance(assessments_store, dict):
        assessments_store[assessment_id] = assessment
    else:
        assessments_store.append(assessment)

    try:
        save_func()
    except Exception:
        if isinstance(assessments_store, dict) and assessment_id in assessments_store:
            del assessments_store[assessment_id]
        elif assessment in assessments_store:
            assessments_store.remove(assessment)
        log.warning("could not save assessment %s; change rolled back", assessment_id)
        raise


def add_mark(
    state: dict[str, Any],
    mark: Mark,
    now: Callable[[], str],
    save: Callable[[], None],
) -> None:
    """Check a mark against the gradebook, then record it (replacing any existing mark) and save."""
    # All checks come first, so a rejected mark leaves no trace.
    if mark.student not in state["students"]:
        raise NotFoundError(f"no such student: {mark.student}")
    assessment_row = state["assessments"].get(mark.assessment)
    if assessment_row is None:
        raise NotFoundError(f"no such assessment: {mark.assessment}")
    if mark.score > assessment_row["total"] or mark.score < 0:
        raise ValidationError("score out of valid range")

    state["marks"] = [
        m
        for m in state["marks"]
        if not (m["student"] == mark.student and m["assessment"] == mark.assessment)
    ]

    state["marks"].append(
        {
            "student": mark.student,
            "assessment": mark.assessment,
            "score": mark.score,
            "at": now(),
        }
    )
    save()


class Handler(http.server.BaseHTTPRequestHandler):
    """HTTP Request handler with centralized error boundary."""

    def _send(self, code: int, body: Any) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _parse_json_body(self) -> Any:
        raw_length = self.headers.get("Content-Length")
        if not raw_length:
            raise ValidationError("Missing Content-Length header.")
        try:
            length = int(raw_length)
        except ValueError:
            raise ValidationError("Invalid Content-Length header.") from None

        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            raise ValidationError("Invalid JSON payload.") from None

    def _handle_request(self, method: str) -> tuple[int, Any]:
        clean_path = self.path.split("?", 1)[0].strip("/")
        parts = clean_path.split("/") if clean_path else []

        if method == "GET":
            if not parts:
                return 200, {"status": "ok"}
            if parts[0] == "students":
                if len(parts) == 1:
                    return 200, get_students()
                if len(parts) == 2:
                    sid = clean_path.removeprefix("students/")
                    return 200, get_student(sid)
            elif parts[0] == "assessments" and len(parts) == 1:
                return 200, get_assessments()
            elif parts[0] == "report" and len(parts) == 1:
                return 200, get_report()
            raise NotFoundError("Route not found.")

        if method == "POST":
            payload = self._parse_json_body()
            if not parts:
                raise NotFoundError("Route not found.")
            if parts[0] == "students" and len(parts) == 1:
                return 200, add_student(payload)
            if parts[0] == "assessments" and len(parts) == 1:
                add_assessment(STATE, payload, save)
                return 200, payload
            if parts[0] == "marks" and len(parts) == 1:
                m = parse_mark(payload)
                add_mark(STATE, m, lambda: "", save)
                return 200, {"ok": True}
            raise NotFoundError("Route not found.")

        raise NotFoundError("Method not supported.")

    def _dispatch(self, method: str) -> None:
        try:
            status, body = self._handle_request(method)
            self._send(status, body)
        except ValidationError as e:
            self._send(400, {"error": str(e)})
        except NotFoundError as e:
            self._send(404, {"error": str(e)})
        except ConflictError as e:
            self._send(409, {"error": str(e)})
        except GradebookError as e:
            self._send(400, {"error": str(e)})
        except Exception:
            log.exception("Unhandled server error")
            self._send(500, {"error": "internal error"})

    def do_GET(self) -> None:
        self._dispatch("GET")

    def do_POST(self) -> None:
        self._dispatch("POST")


def main() -> None:
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            raise SystemExit("Port must be an integer between 1 and 65535.") from None

    load()
    log.info("gradebook on %d", port)
    server = http.server.HTTPServer(("", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()