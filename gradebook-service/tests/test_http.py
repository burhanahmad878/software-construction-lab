import http.client
import http.server
import threading
from collections.abc import Iterator
from typing import Any

import gradebook
import pytest


@pytest.fixture
def port(state: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> Iterator[int]:
    monkeypatch.setattr(gradebook, "STATE", state)
    server = http.server.HTTPServer(("127.0.0.1", 0), gradebook.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server.server_port
    server.shutdown()
    server.server_close()


def send(port: int, method: str, path: str, body: bytes | None = None) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port)
    connection.request(method, path, body=body)
    response = connection.getresponse()
    return response.status, response.read()


@pytest.mark.parametrize("path", ["/students/S1", "/students/S1/", "/students/S1?format=json"])
def test_student_is_found_with_a_trailing_slash_or_query(port: int, path: str) -> None:
    status, _ = send(port, "GET", path)
    assert status == 200


def test_body_that_is_not_utf8_is_a_bad_request(port: int) -> None:
    status, _ = send(port, "POST", "/students", body=b"\x80\x81\x82")
    assert status == 400