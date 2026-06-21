# Docker Development Container Design

## Objective

Update `docker/Dockerfile.dev` so one development container runs the Next.js UI and Python LangGraph agent. The UI must listen on port 3000 and the agent on port 8123, with both services reachable outside the container.

## Image and Dependencies

Use the existing official `node:22-bookworm-slim` base. Add the official, pinned `uv` binary and use it to install Python 3.12, matching `agent/pyproject.toml`. Keep pnpm 10.15.0 through Corepack. Install JavaScript dependencies from `pnpm-lock.yaml` and Python dependencies from `agent/uv.lock`; both installs must use frozen lockfiles.

Preserve the current uncommitted additions that copy `.npmrc`, `scripts/`, and `agent/` before dependency installation. Arrange copy steps so dependency layers remain cacheable while application source changes.

## Runtime

Expose ports 3000 and 8123. The container command will first run the existing environment preflight script, then use `concurrently` to supervise:

- Next.js development mode bound to `0.0.0.0:3000`.
- LangGraph development mode bound to `0.0.0.0:8123`.

If either process exits, `concurrently` must terminate the other and return a failure status. Runtime secrets remain external and are supplied through `--env-file`; `.env` values are not baked into the image.

## Validation

Because this change is container configuration, validation uses behavioral smoke tests rather than a new unit-test framework. Build the image from the repository root, start it with both port mappings and environment values, verify that both ports accept connections, and inspect startup logs for dependency or process failures.
