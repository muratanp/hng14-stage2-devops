# FIXES.md — Bug Report

Every issue found in the starter repository, with file, line, description, and fix.

---

## FIX 1 — `api/.env` committed to the repository

| Field | Detail |
|-------|--------|
| **File** | `api/.env` |
| **Line** | entire file |
| **Problem** | A real `.env` file containing `REDIS_PASSWORD=supersecretpassword123` was committed directly to the repository. |
| **Fix** | Deleted `api/.env`. Added `.env` and `.env.*` (except `.env.example`) to `.gitignore`. Added `.env.example` with placeholder values to know what variables are required without exposing real credentials. |

---

## FIX 2 — `api/main.py` — Redis host hardcoded as `localhost`

| Field | Detail |
|-------|--------|
| **File** | `api/main.py` |
| **Line** | 8 |
| **Problem** | `r = redis.Redis(host="localhost", port=6379)` — `localhost` is hardcoded. Inside a Docker container the Redis service is not reachable at `localhost`; it must be addressed by its Docker network service name (e.g. `redis`). This would cause an immediate connection failure in any containerized environment. |
| **Fix** | Changed to read from environment variables: `REDIS_HOST` (default `"redis"`), `REDIS_PORT` (default `6379`). |

---

## FIX 3 — `api/main.py` — Redis connection ignores password

| Field | Detail |
|-------|--------|
| **File** | `api/main.py` |
| **Line** | 8 |
| **Problem** | `redis.Redis(host="localhost", port=6379)` — no `password` argument. Redis is configured with `requirepass` in docker-compose, so unauthenticated connections are rejected. The API would receive `NOAUTH Authentication required` errors on every Redis command. |
| **Fix** | Added `password=REDIS_PASSWORD` to the Redis constructor, sourced from the `REDIS_PASSWORD` environment variable. |

---

## FIX 4 — `api/main.py` — No `/health` endpoint

| Field | Detail |
|-------|--------|
| **File** | `api/main.py` |
| **Line** | N/A (missing) |
| **Problem** | There was no health check endpoint. Docker's `HEALTHCHECK` instruction and `depends_on: condition: service_healthy` in docker-compose both require a working health endpoint; without one the container health state never becomes `healthy` and dependent services refuse to start. |
| **Fix** | Added `GET /health` that calls `r.ping()` and returns `{"status": "ok"}`. |

---

## FIX 5 — `api/main.py` — 404 returned as `200 OK` with an error body

| Field | Detail |
|-------|--------|
| **File** | `api/main.py` |
| **Lines** | 18–20 |
| **Problem** | `return {"error": "not found"}` — when a job ID is not found the handler returns HTTP `200 OK` with a JSON body containing `"error"`. Clients have no way to distinguish success from failure by status code, and the frontend would silently poll forever on a non-existent job. |
| **Fix** | Replaced with `raise HTTPException(status_code=404, detail="Job not found")` so the correct HTTP status is returned. |

---

## FIX 6 — `api/main.py` — Queue name `"job"` collides with hash key namespace

| Field | Detail |
|-------|--------|
| **File** | `api/main.py` |
| **Line** | 13 |
| **Problem** | `r.lpush("job", job_id)` — the queue list is stored under the key `"job"`, but job status hashes are stored under `"job:{id}"`. While Redis can store different types under different keys, using `"job"` as both a bare list key and a prefix for hashes is confusing and error-prone (e.g. `KEYS job*` would return both). |
| **Fix** | Renamed the queue key to `"jobs"` in both `api/main.py` and `worker/worker.py` for unambiguous namespacing. |

---

## FIX 7 — `frontend/app.js` — API URL hardcoded as `localhost:8000`

| Field | Detail |
|-------|--------|
| **File** | `frontend/app.js` |
| **Line** | 6 |
| **Problem** | `const API_URL = "http://localhost:8000"` — `localhost` inside a container refers to the container itself, not the API service. The frontend would fail to reach the API with a connection refused error. |
| **Fix** | Changed to `process.env.API_URL || 'http://api:8000'` so the Docker service name is used by default and can be overridden per-environment. |

---

## FIX 8 — `frontend/app.js` — Error responses from API not propagated correctly

| Field | Detail |
|-------|--------|
| **File** | `frontend/app.js` |
| **Lines** | 25–29 |
| **Problem** | The `/status/:id` catch block returns `500` regardless of whether the upstream error was a `404`, `502`, etc. A missing job silently appears as a server error. |
| **Fix** | Reads `err.response.status` when available and forwards it: `const status = err.response ? err.response.status : 500`. |

---

## FIX 9 — `frontend/app.js` — No `/health` endpoint

| Field | Detail |
|-------|--------|
| **File** | `frontend/app.js` |
| **Line** | N/A (missing) |
| **Problem** | Same as FIX 4 for the API — Docker's `HEALTHCHECK` requires a live endpoint. Without it the container stays in `starting` health state and `depends_on: condition: service_healthy` for any downstream service would block indefinitely. |
| **Fix** | Added `GET /health` returning `{"status": "ok"}`. |

---

## FIX 10 — `worker/worker.py` — Redis host hardcoded as `localhost`

| Field | Detail |
|-------|--------|
| **File** | `worker/worker.py` |
| **Line** | 6 |
| **Problem** | `r = redis.Redis(host="localhost", port=6379)` — same container networking issue as FIX 2; the worker cannot reach Redis at `localhost`. |
| **Fix** | Changed to read `REDIS_HOST` and `REDIS_PORT` from environment variables, defaulting to `"redis"` and `6379` respectively. |

---

## FIX 11 — `worker/worker.py` — Redis connection ignores password

| Field | Detail |
|-------|--------|
| **File** | `worker/worker.py` |
| **Line** | 6 |
| **Problem** | Same as FIX 3; no `password` argument means all Redis commands fail with `NOAUTH`. |
| **Fix** | Added `password=REDIS_PASSWORD` sourced from the `REDIS_PASSWORD` environment variable. |

---

## FIX 12 — `worker/worker.py` — `signal` imported but never used

| Field | Detail |
|-------|--------|
| **File** | `worker/worker.py` |
| **Line** | 4 |
| **Problem** | `import signal` is present but no signal handlers are registered. This means `SIGTERM` (sent by `docker stop`) immediately kills the process mid-job, potentially leaving a job in `queued` state permanently. |
| **Fix** | Implemented `handle_shutdown` for both `SIGTERM` and `SIGINT`. The worker sets `running = False` on receiving a signal and exits cleanly after the current job finishes, instead of being killed abruptly. |

---

## FIX 13 — `api/requirements.txt` / `worker/requirements.txt` — Unpinned dependency versions

| Field | Detail |
|-------|--------|
| **Files** | `api/requirements.txt`, `worker/requirements.txt` |
| **Lines** | all |
| **Problem** | All packages (`fastapi`, `uvicorn`, `redis`) had no version pins. Unpinned dependencies mean builds are not reproducible — a future `pip install` may pull a breaking version. |
| **Fix** | Pinned all dependencies to specific versions (`fastapi==0.104.1`, `uvicorn==0.24.0`, `redis==5.0.1`, `httpx==0.25.2`). |

---

## FIX 14 — No `.gitignore` in the repository

| Field | Detail |
|-------|--------|
| **File** | `.gitignore` (missing) |
| **Line** | N/A |
| **Problem** | There was no `.gitignore`. This allowed `api/.env`, `__pycache__/`, and `node_modules/` to be committed (`.env` actually was committed — see FIX 1). |
| **Fix** | Created `.gitignore` that excludes `.env` files (except `.env.example`), Python cache, Node modules, and Docker tarballs. |

---

## FIX 15 — No ESLint configuration

| Field | Detail |
|-------|--------|
| **Files** | `frontend/package.json`, `frontend/.eslintrc.json` |
| **Line** | N/A (missing) |
| **Problem** | `frontend/package.json` had no lint script and no ESLint dependency. The CI pipeline requires `eslint` linting of JavaScript. |
| **Fix** | Added `eslint` to `devDependencies`, added `"lint": "eslint app.js"` script, and created `.eslintrc.json` with Node environment and recommended ruleset. |
