# Local operations

Start Docker Desktop, copy `.env.example` to `.env`, then run `docker compose up --build`. The coordinator liveness endpoint is `/health`; open `/docs` for the API schema.

Workers use distinct IDs. Add more by starting worker containers with unique `MESH_COMPUTE_WORKER_ID` values. The dashboard polls as a fallback if WebSocket updates disconnect.

Use `docker compose down` for a clean stop. The named database volume preserves tasks. Back up PostgreSQL before deleting that volume. Example credentials are only for local development.
