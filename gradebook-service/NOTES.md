# Task 2 & Task 8: Failure Investigation Notes

## 1. Initial Test Requests Results (Task 2)

- **(a) GET /students/NOPE**
  - **Status:** `200 OK`
  - **Response:** `{"error": "not found"}`

- **(b) POST /students with body "5"**
  - **Status:** Server crashed (`Empty reply from server`).

- **(c) Invalid mark score "abc"**
  - **Status:** `200 OK`
  - **Response:** Accepted string score `"abc"` without validation.

- **(d) Assessment with total "0"**
  - **Status:** `200 OK`
  - **Response:** Created assessment with total "0".

- **(e) POST mark for non-existent assessment**
  - **Status:** `200 OK`
  - **Response:** Created mark for non-existent assessment.

---

## 2. Why deleting gradebook.json was necessary

Deleting `gradebook.json` between tests cleared saved corrupted data from previous tests so that it did not interfere with subsequent test cases.

---

## 3. Bare `except:` Clauses Found (Task 2)

- **Line 19:** In `load()` catching all exceptions during file loading.
- **Line 28:** In `save()` catching all exceptions and passing silently.
- **Line 84:** In POST body parsing catching all JSON decoding errors.

---

## 4. Post-Fix Test Request Results (Task 8)

- **(a) GET /students/NOPE**
  - **Status:** `404 Not Found`
  - **Response:** `{"error": "Student 'NOPE' not found."}`

- **(b) POST /students with body 5**
  - **Status:** `400 Bad Request`
  - **Response:** `{"error": "Payload must be a JSON object."}`

- **(c) POST mark with score "abc"**
  - **Status:** `400 Bad Request`
  - **Response:** `{"error": "Field 'score' must be a valid number."}`

- **(d) POST assessment with total "0"**
  - **Status:** `400 Bad Request`
  - **Response:** `{"error": "Assessment total must be greater than 0."}`

- **(e) POST mark for non-existent assessment**
  - **Status:** `404 Not Found`
  - **Response:** `{"error": "Assessment 'A1' does not exist."}`
// ============================================================== (LAB 04)
# Lab 04 - Proving the tests can fail
I changed the / to * in pct() and ran the tests:
3 failed, 25 passed

After undoing the change:
28 passed

## Which double is which
- Stub: fixed_now in tests/test_add_mark.py. It always returns the same time,
  so the expected "at" value is known.
- Fake: the state fixture in tests/conftest.py. It is a plain dict that works
  like the real gradebook. The files in tests/test_storage.py are real files
  in tmp_path.
- Mock: Mock() passed as save in tests/test_add_mark.py. It records the call,
  so the tests can check "called once" and "not called".

## Why I did not mock pct() or the file in Task 5
- pct() is plain logic inside my own program. I can call it directly, and
  mocking it would hide the very calculation under test.
- tmp_path gives a real, empty file for each test. Testing load() and save()
  against it checks what really happens (JSON written and read back, a
  missing file, a corrupt file). A mock would only check that I called open.

## LAB 05 TASK 01 
# Lab 05 Notes

## Task 1
- Total coverage: 25%
- Lowest coverage file: src/orders.py (16%)

## Task 2
- Cycle 1 failure message: ...
- Cycle 2 failure message: ...
- Cycle 4 failure message: ...
- Did cycle 3 fail first? No


## Debug A ===============================================
[6b105bb5a5f3f2248fd06fca505f451de57832c8] Complete Task 1: Setup coverage, hypothesis, requirements, and NOTES.md
running 'python' 'check_trailing_slash.py'
127.0.0.1 - - [24/Nov/2026 14:03:50] "GET /students/S1/ HTTP/1.1" 404 -
GET /students/S1/ -> 404
Bisecting: 0 revisions left to test after this (roughly 1 step)
[ba5740ab2fd0be0a08a05a0e8e0c40b1eadf35b6] Complete Task 1: Setup coverage, hypothesis, requirements, and NOTES.md
running 'python' 'check_trailing_slash.py'
127.0.0.1 - - [24/Nov/2026 14:03:50] "GET /students/S1/ HTTP/1.1" 404 -
GET /students/S1/ -> 404
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[891061f425afcdf26a9167b96c3a88aebb3fd6cb] Add tests and clean up duplicate project
running 'python' 'check_trailing_slash.py'
127.0.0.1 - - [24/Nov/2026 14:03:51] "GET /students/S1/ HTTP/1.1" 404 -
GET /students/S1/ -> 404
891061f425afcdf26a9167b96c3a88aebb3fd6cb is the first 'bad' commit
commit 891061f425afcdf26a9167b96c3a88aebb3fd6cb
Author: Burhan Ahmad <burhanahmadcase@gmail.com>
Date:   Mon Sep 28 08:31:10 2026 +0500

    Add tests and clean up duplicate project

 software-construction-lab/README.md                  |   0
 software-construction-lab/requirements.txt           | Bin 468 -> 0 bytes
 .../src/__pycache__/hello.cpython-314.pyc            | Bin 496 -> 0 bytes
 software-construction-lab/src/hello.py               |   2 --
 .../test_hello.cpython-314-pytest-9.1.1.pyc          | Bin 1415 -> 0 bytes
 software-construction-lab/tests/test_hello.py        |   5 -----
 src/__pycache__/hello.cpython-314.pyc                | Bin 496 -> 496 bytes
 src/__pycache__/orders.cpython-314.pyc               | Bin 0 -> 2350 bytes
 .../test_hello.cpython-314-pytest-9.1.1.pyc          | Bin 1415 -> 1415 bytes
 .../test_orders.cpython-314-pytest-9.1.1.pyc         | Bin 0 -> 1965 bytes
 tests/test_orders.py                                 |  19 +++++++++++++++++++
 11 files changed, 19 insertions(+), 7 deletions(-)
 delete mode 100644 software-construction-lab/README.md
 delete mode 100644 software-construction-lab/requirements.txt
 delete mode 100644 software-construction-lab/src/__pycache__/hello.cpython-314.pyc
 delete mode 100644 software-construction-lab/src/hello.py
 delete mode 100644 software-construction-lab/tests/__pycache__/test_hello.cpython-314-pytest-9.1.1.pyc
 delete mode 100644 software-construction-lab/tests/test_hello.py
 create mode 100644 src/__pycache__/orders.cpython-314.pyc
 create mode 100644 tests/__pycache__/test_orders.cpython-314-pytest-9.1.1.pyc
 create mode 100644 tests/test_orders.py
bisect found first 'bad' commit

# Lab 06 Notes

| Bug | Cause | Fix | Test |
| :--- | :--- | :--- | :--- |
| Bug A | `self.path.removeprefix("/students/")` kept trailing `/` and query strings | Strip query string with `.split("?", 1)[0]` and `.strip("/")` before extracting `sid` | `test_student_is_found_with_a_trailing_slash_or_query` |
| Bug B | `add_assessment` mutated `state["assessments"]` before `save()` without rollback on `OSError` | Wrapped `save()` in `try...except` to delete the added assessment, log `log.warning(...)`, and re-raise | `test_failed_save_leaves_no_trace` |
| Bug C | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 0: invalid start byte` | Decode body inside `try...except ValueError` in `_parse_json_body` to raise `ValidationError` (HTTP 400) | `test_body_that_is_not_utf8_is_a_bad_request` |

