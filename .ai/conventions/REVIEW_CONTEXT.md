# Review Context — poe2-trade-agent

Guidance for automated code review. These are the project's own rules and they
override any generic best-practice advice.

## What the project is

A website for saving Path of Exile 2 trade searches as templates. The app only
**builds** links to the official trade site
(`https://www.pathofexile.com/trade2/search/poe2/<league>?q=<URL-encoded JSON>`);
the browser opens them. The backend never calls GGG's servers. The owner is
learning Python with this project, so prefer simple, idiomatic code over clever code.

## Stack — do not suggest patterns from other ecosystems

- **backend/** — Python 3.14, FastAPI, Pydantic + pydantic-settings, SQLModel,
  PostgreSQL 16 via psycopg, Alembic, pwdlib + PyJWT, httpx. Managed with uv.
  Tests: pytest against a real PostgreSQL test database. Lint/types: Ruff, mypy (strict).
- **frontend/** — React, TypeScript, Vite, Tailwind CSS, react-router-dom,
  TanStack Query, Zod. ESLint + Prettier. **No test runner is configured.**
- **infra/** — AWS CDK in Python. Production runs Docker Compose (Traefik + backend
  + PostgreSQL) on one EC2 instance; deploys go GitHub Actions → GHCR → AWS SSM.

Layout follows `full-stack-fastapi-template`: `app/main.py` creates the app,
`app/api/routes/*.py` hold routers (combined in `app/api/main.py` and mounted under
`/api/v1`), `app/api/deps.py` holds shared dependencies, `app/core/` holds config,
database and security, `app/models/` holds tables and request/response shapes,
`app/services/` holds logic that isn't HTTP.

## Numbered rules — flag violations explicitly and name the rule

1. **Test naming.** Python tests follow PEP 8 snake_case: `test_<feature>_<condition>`,
   optionally ending with the expected result, e.g. `test_register_duplicate_username` or
   `test_user_duplicate_username_is_rejected`. camelCase names such as
   `testRegister_DuplicateUsername` are wrong (Ruff's `N` rules report them).
2. **Comments never mention planning files.** No `TASK_XX`, `PLAN`, `RESEARCH`,
   spike results or section numbers in code, comments or docstrings; state the fact itself.
3. **TSDoc links.** Every code object a TSDoc/JSDoc comment mentions is linked with
   `{@link Name}`, and the name is in scope (type-only import if needed).
4. **No new dependencies without approval.** Any new entry in `pyproject.toml` or
   `package.json` must be called out; the owner approves each library.
5. **App settings come from `app/core/config.py`** (pydantic-settings). No
   `os.environ` / `os.getenv` in `backend/app/`. Test setup (`backend/tests/conftest.py`)
   and `infra/` (the CDK reads `CDK_DEFAULT_ACCOUNT`) may read the environment directly.
   Every new app setting is added to `.env.example` with a dummy value.
6. **Type hints everywhere.** Every function has parameter and return types; the
   code must pass `mypy --strict`. No bare `Any` without a reason.
7. **Routes stay thin.** A route validates input, calls a service or query, and
   returns a response model. Shared lookups (DB session, current user) are FastAPI
   dependencies in `app/api/deps.py`, not repeated in each route.
8. **`useState`, not `useRef`, for component-owned values.** `useRef` is for DOM
   nodes, timer ids, and previous-render tracking only. A component must never be
   defined inside a hook or inside another component.
9. **No synchronous `setState` in `useEffect`.** Derive values inline, reset state
   during render via previous-prop comparison, or remount with a `key`.
10. **Nav matching compares path SEGMENTS.** `pathname.startsWith(linkTo)` is a
    defect — split on `/` and compare segment by segment.
11. **Log failures; never swallow an error silently.** Backend: each module uses
    `logger = logging.getLogger(__name__)`, never `print()`. An `except` that carries on
    must log a warning with `exc_info=True` (or re-raise), and a failed call to an
    outside service (Cloudflare, poe.ninja, the mod list download) must be logged.
    Logging is configured once per entry point, not in library code. Frontend: use
    `createLogger(scope)` from `src/lib/logger.ts`, never `console.*`. Don't log normal
    outcomes (404, wrong password, a failed human check), and never log passwords,
    tokens or secrets.

## Repository invariants

- **Never modify an Alembic migration that is already merged.** Schema changes
  need a NEW revision under `backend/app/alembic/versions/`.
- No secrets, keys, or tokens in committed files. `.env` stays untracked. Never
  log passwords, JWTs or other personal data. Passwords are hashed with pwdlib.
- **Outbound HTTP calls (httpx: poe.ninja, Cloudflare Turnstile, GitHub) need
  explicit timeouts.**
- **TypeScript:** no `any`. Parse untrusted data (API responses, `localStorage`,
  query params, pasted trade URLs) with Zod at the boundary rather than casting with `as`.
- **Keep it simple.** Don't add handling for unlikely edge cases.

## Testing expectations

- New backend logic requires pytest tests; a bug fix requires a regression test.
- API changes require a test that calls the endpoint through FastAPI's test client.
- Tests must be deterministic and independent.
- **`frontend/` has no test runner — never ask for frontend tests.**
