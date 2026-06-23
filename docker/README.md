# Docker Images

This directory contains Dockerfiles for running the CopilotKit + LangGraph app in development and packaging the UI for deployment.

## Prerequisites

- Docker installed locally.
- A `.env` file at the repository root.
- Required runtime secret:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
```

Do not bake `.env` files into images. Pass secrets at runtime with `--env-file`, an orchestrator secret store, or CI/CD variables.

## Development Image

`Dockerfile.dev` builds a single development image with:

- Node.js 22 and pnpm 10.15.0 for the Next.js UI.
- uv 0.9.18 and Python 3.12 for the LangGraph agent.
- Both services started together with `concurrently`.

Build the image:

```bash
docker build -f docker/Dockerfile.dev -t ag-ui-app-dev .
```

Run the container:

```bash
docker run --rm \
  --name ag-ui-app-dev \
  --env-file .env \
  -p 3000:3000 \
  -p 8123:8123 \
  ag-ui-app-dev
```

Local endpoints:

- UI: `http://localhost:3000`
- LangGraph dev server: `http://localhost:8123`

The development image copies the repository at build time. Rebuild after source, dependency, or agent changes unless you use the live-edit workflow below.

## Live Source Editing

For local development, bind mount the repository into `/app` so edits on your machine are visible inside the container:

```bash
docker run --rm \
  --name ag-ui-app-dev \
  --env-file .env \
  -p 3000:3000 \
  -p 8123:8123 \
  -v "$PWD:/app" \
  -v /app/node_modules \
  -v /opt/venv \
  ag-ui-app-dev
```

Edit files normally on the host, such as `src/`, `agent/`, and `scripts/`. Next.js should reload UI changes automatically. Restart the container if agent changes do not reload cleanly.

The anonymous `/app/node_modules` and `/opt/venv` volumes preserve dependencies installed in the image; without them, the host mount can hide container dependencies.

## Production / Deployment Image

`Dockerfile.prod` runs the production Next.js UI on port `3000`.

Current production build behavior:

- The build stage starts from `myregistry/ui-devbase-alpine:1.0`.
- That base image must contain the app source, dependencies, and pnpm setup.
- The runtime copies `.next`, `public`, `package.json`, `pnpm-lock.yaml`, and `node_modules` from the build stage.
- The Python LangGraph agent is not included in the production runtime image.

Build the production image after providing a valid build base image:

```bash
docker build -f docker/Dockerfile.prod -t ag-ui-app-prod .
```

Run the production UI:

```bash
docker run --rm \
  --name ag-ui-app-prod \
  --env-file .env \
  -p 3000:3000 \
  ag-ui-app-prod
```

For deployment, publish the image to your registry:

```bash
docker tag ag-ui-app-prod registry.example.com/ag-ui-app:latest
docker push registry.example.com/ag-ui-app:latest
```

Deploy the LangGraph agent separately, then configure the UI so CopilotKit can reach that agent endpoint. Do not expose the development LangGraph server publicly without authentication and network controls.

## Operational Notes

- `.dockerignore` should exclude `node_modules`, `.next`, `agent/.venv`, and `.env` files.
- Keep API keys and provider credentials in runtime secrets.
- If the UI cannot reach the agent, verify the agent container or service is running, port `8123` is reachable, and the UI environment points to the correct LangGraph URL.
- If builds become slow, check that large local folders are excluded from the Docker build context.
