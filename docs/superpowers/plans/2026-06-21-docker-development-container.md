# Docker Development Container Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `docker/Dockerfile.dev` build and run the Next.js UI and Python LangGraph agent together, reachable on ports 3000 and 8123.

**Architecture:** Extend the official Node 22 development image with pinned uv tooling and a uv-managed Python 3.12 installation. Cache JavaScript and Python dependency installation before copying the remaining source, then supervise both host-bound development servers with the existing `concurrently` dependency.

**Tech Stack:** Docker, Node.js 22, pnpm 10.15.0, Python 3.12, uv 0.9.18, Next.js 16, LangGraph CLI, concurrently 9.

---

### Task 1: Establish the Dockerfile contract

**Files:**
- Test: `docker/Dockerfile.dev` (static contract checks before implementation)

- [ ] **Step 1: Verify the current Dockerfile fails the required contract**

Run:

```bash
rg -q 'ghcr.io/astral-sh/uv:0\.9\.18' docker/Dockerfile.dev \
  && rg -q 'uv python install 3\.12' docker/Dockerfile.dev \
  && rg -q 'EXPOSE 3000 8123' docker/Dockerfile.dev \
  && rg -q -- '--hostname 0\.0\.0\.0' docker/Dockerfile.dev \
  && rg -q -- '--host 0\.0\.0\.0' docker/Dockerfile.dev
```

Expected: non-zero exit status because uv, Python 3.12, port 8123, and explicit service bindings are absent.

### Task 2: Implement the dual-service development image

**Files:**
- Modify: `docker/Dockerfile.dev`

- [ ] **Step 1: Add pinned Python tooling and cacheable dependencies**

Use an official uv stage and copy `/uv` and `/uvx` into `node:22-bookworm-slim`. Set `UV_PYTHON_INSTALL_DIR=/opt/uv/python`, install Python 3.12, retain the existing pnpm setup, and copy `package.json`, `pnpm-lock.yaml`, `.npmrc`, `scripts/`, and `agent/` before the frozen install. The existing `postinstall` then executes `uv sync` against `agent/uv.lock`.

- [ ] **Step 2: Define the dual-service command**

Expose both ports and set the command to:

```dockerfile
CMD ["sh", "-c", "node scripts/copilotkit-dev-infra.mjs && pnpm exec concurrently --kill-others --names ui,agent --prefix-colors blue,green \"pnpm exec next dev --turbopack --hostname 0.0.0.0 --port 3000\" \"cd agent && uv run langgraph dev --host 0.0.0.0 --port 8123 --no-browser\""]
```

- [ ] **Step 3: Re-run the static contract check**

Run the command from Task 1.

Expected: exit status 0.

- [ ] **Step 4: Check Dockerfile whitespace and scope**

Run:

```bash
git diff --check && git diff -- docker/Dockerfile.dev
```

Expected: no whitespace errors; the diff only contains the required image, dependency, port, and command changes while preserving pre-existing additions.

### Task 3: Build and smoke-test the image

**Files:**
- Verify: `docker/Dockerfile.dev`

- [ ] **Step 1: Build the development image**

Run:

```bash
docker build -f docker/Dockerfile.dev -t ag-ui-app-dev .
```

Expected: successful pnpm frozen install, uv Python 3.12 installation, and frozen agent dependency sync.

- [ ] **Step 2: Start both services**

Run:

```bash
docker run --rm --name ag-ui-app-dev-smoke --env-file .env -p 3000:3000 -p 8123:8123 ag-ui-app-dev
```

Expected: logs report Next.js ready on port 3000 and LangGraph ready on port 8123 without either process exiting.

- [ ] **Step 3: Probe both endpoints from another shell**

Run:

```bash
curl --fail --silent --show-error http://127.0.0.1:3000/ >/dev/null
curl --fail --silent --show-error http://127.0.0.1:8123/docs >/dev/null
```

Expected: both commands exit 0.

- [ ] **Step 4: Stop the smoke-test container**

Run:

```bash
docker stop ag-ui-app-dev-smoke
```

Expected: the container stops cleanly and is removed by `--rm`.
