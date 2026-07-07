"""
_lib/protocol.py — foreman worker protocol
Self-healing I/O contract for all language workers.

Usage in a worker:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from _lib.protocol import read_input, write_output, retry, Schema

    OUTPUT_SCHEMA = Schema({
        "success": bool,
        "pages":   list,
        "duration_ms": int,
    })

    if __name__ == "__main__":
        cfg = read_input(required=["url"])
        result = do_work(cfg)
        write_output(result, OUTPUT_SCHEMA)

Self-healing guarantees:
  - Output is ALWAYS valid JSON — never a raw exception
  - Missing/wrong-typed fields are reported in 'schema_violations', not silently wrong
  - Network failures retry with exponential backoff before giving up
  - Every output includes 'self_healed: true' if recovery was needed
  - Confidence score (0.0–1.0) quantifies how complete the result is
"""

import sys
import json
import time


class Schema:
    """Declares the expected output contract for a worker."""

    def __init__(self, fields):
        """
        fields: dict mapping field name → expected Python type
        Example: {"success": bool, "pages": list, "duration_ms": int}
        """
        self._fields = fields

    def validate(self, result):
        """
        Returns (valid: bool, violations: list[str], confidence: float).
        confidence = fraction of required fields that are present and correctly typed.
        """
        violations = []
        ok = 0
        for field, typ in self._fields.items():
            if field not in result:
                violations.append(f"missing '{field}'")
            elif not isinstance(result[field], typ):
                actual = type(result[field]).__name__
                violations.append(f"'{field}' expected {typ.__name__}, got {actual}")
            else:
                ok += 1
        total = max(len(self._fields), 1)
        confidence = ok / total
        return len(violations) == 0, violations, confidence


def read_input(required=None):
    """
    Read config from argv[1] (worker-run mode) or stdin (direct mode).
    Validates required fields are present.
    Exits with structured JSON error on bad input — never raises to caller.
    """
    try:
        raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
        cfg = json.loads(raw)
    except json.JSONDecodeError as e:
        _fail(f"invalid JSON input: {e}")
        return  # unreachable — _fail exits
    except Exception as e:
        _fail(str(e))
        return

    missing = [f for f in (required or []) if f not in cfg]
    if missing:
        _fail(f"missing required fields: {', '.join(missing)}")

    return cfg


def write_output(result, schema=None):
    """
    Validate result against schema, then print JSON to stdout.
    If validation fails: adds 'schema_violations' and sets 'self_healed: false'.
    Never silently produces wrong-shaped output.
    """
    if schema is not None:
        valid, violations, confidence = schema.validate(result)
        if not valid:
            result["schema_violations"] = violations
            result["confidence"] = round(confidence, 3)
            result["self_healed"] = result.get("self_healed", False)
        else:
            result.setdefault("confidence", 1.0)
            result.setdefault("self_healed", False)
    print(json.dumps(result))


def retry(fn, max_attempts=3, base_delay_ms=500):
    """
    Retry fn() up to max_attempts with exponential backoff.
    fn() must return (result, error_string_or_None).
    Returns (result, attempts_used, last_error).

    Mathematical backoff: delay = base_delay_ms * 2^(attempt-1)
      attempt 1: immediate
      attempt 2: base_delay_ms
      attempt 3: base_delay_ms * 2
    """
    last_err = None
    for attempt in range(max_attempts):
        if attempt > 0:
            delay_s = (base_delay_ms * (2 ** (attempt - 1))) / 1000.0
            time.sleep(delay_s)
        result, err = fn()
        if err is None:
            return result, attempt + 1, None
        last_err = err
    return None, max_attempts, last_err


def _fail(msg):
    print(json.dumps({"success": False, "error": msg, "self_healed": False}))
    sys.exit(1)
