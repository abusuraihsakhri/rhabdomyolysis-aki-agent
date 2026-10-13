# Rhabdomyolysis AKI Agent

A Python and browser-based **software demonstration** of generic rule checks, CSV processing, a FastAPI service, and an in-memory signed event log. The repository also retains earlier compatibility implementations.

**Clinical scope:** The numeric checks are illustrative and unitless. This software **does not implement a validated McMahon score, KDIGO AKI classifier, CK clearance model, or rhabdomyolysis treatment algorithm**. The project name describes its intended domain, not clinical validation. Never use the demo for diagnosis, triage, prescriptions, or decisions involving patients.

## Browser demonstration

Open [web/index.html](web/index.html) locally in a browser. It is a standalone, mobile-responsive JavaScript demonstration of the enterprise path's illustrative 25/12 thresholds, a manual priority flag, and status keyword checks. It requires no Python, API, third-party assets, or network calls. It can export an example JSON result. Only use synthetic input; no inputs are uploaded or intentionally persisted. The [GitHub Pages workflow](.github/workflows/pages.yml) publishes this directory when Pages is configured for GitHub Actions; a live URL is not claimed until deployment has been verified.

## Python setup

Python 3.10–3.12 is tested in CI (package metadata permits Python 3.9+). From a fresh checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[api,test]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

On Windows, activate the environment with `.venv\Scripts\activate` and set `AUDIT_SECRET_KEY` through your shell or process environment.

The signing key **must be supplied explicitly**; no production key is embedded. The `.env.example` file is a template, but the Python CLI does not automatically load `.env`.

## CLI

```bash
python cli.py audit --task-id DEMO-01 --target SYNTH-01 --primary 29 --secondary 13
python cli.py chat "status"
python cli.py batch --input sample.csv --output results.csv
python cli.py verify-audit
python simulator.py 100
```

The main CLI is `cli.py` (the enterprise demonstration using Pydantic models), also installed as `rhabdomyolysis-aki-engine`. Batch CSV accepts either the enterprise `primary_metric` / `is_critical_flag` fields or the supplied sample's `metric_primary` / `is_stat` equivalents, including textual `True` and `False`. Audit records exist only in memory during execution; batch results are written to the specified CSV file; a separate `verify-audit` invocation starts a new process and therefore cannot verify a prior process's audit chain.

For compatibility, `rhabdo_guard.py` and `python -m rhabdomyolysis_aki_agent.cli` retain older, distinct example rule paths. Their fields and thresholds differ; they are not interchangeable with the main CLI.

## REST API

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

The enterprise FastAPI service exposes `GET /health`, JSON counters at `GET /metrics`, `POST /api/audit`, and `POST /api/chat` (deterministic mock text only; **no clinical reasoning**). `GET /api/audit/logs` is disabled unless a separate `AUDIT_READ_TOKEN` is configured; requests must send that token through the `X-Audit-Key` header. OpenAPI documentation is at `/docs`.

Do not expose the API publicly without independent authentication, rate limiting, access control, and a privacy/security review. The built-in identifier detection uses a limited set of regular expressions, **not** comprehensive PHI detection or a HIPAA compliance certification. Audit logs are HMAC-SHA256 chained **in memory**; they are not durable, multi-process logs.

## Tests and Docker

```bash
python -m pytest -v
docker compose up --build
```

For Docker Compose, copy `.env.example` to `.env`, replace the signing key placeholder with a unique randomly generated key, and keep the file private. The Docker image installs the declared runtime dependencies and serves FastAPI on port 8000. CI runs the Python suite and compiles the modules on Python 3.10–3.12.

## Technical scope

- Python, Pydantic v2, FastAPI, Uvicorn, pytest; dependency-free HTML/CSS/JavaScript frontend.
- Generic threshold workers, synthetic-case output, CSV batch support, and regex-based identifier checks.
- Signed audit records detect record/chain tampering while the process remains running. No persistent database, clinical outcome validation, real external language-model integration, or EHR/FHIR integration is implemented.
- Browser demo supports current Chrome/Edge/Firefox/Safari with modern JavaScript; it does not execute Python or send data to a server.

## License

MIT. See [LICENSE](LICENSE).
