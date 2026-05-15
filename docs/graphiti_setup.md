# Graphiti + Neo4j Setup

Graphiti is disabled by default. The app and tests run without Docker, Neo4j, or `graphiti-core`.

## Enable Neo4j

1. Set the password in your shell or system environment:

   ```powershell
   $env:NEO4J_PASSWORD = Read-Host "Neo4j password"
   ```

2. Start Neo4j:

   ```powershell
   docker compose up -d neo4j
   ```

3. Install the optional Python package:

   ```powershell
   python -m pip install "graphiti-core>=0.29.0"
   ```

4. Flip the config flag:

   ```yaml
   memory:
     graphiti_enabled: true
     neo4j_uri: "bolt://localhost:7687"
     neo4j_user: "neo4j"
     neo4j_password_env: "NEO4J_PASSWORD"
   ```

The password is read only from the environment variable named by
`memory.neo4j_password_env`. Do not put a Neo4j password in `config.yaml`.

## API

- `POST /memory/graph/add` with `{ "text": "...", "source": "api" }`
- `POST /memory/graph/query` with `{ "text": "...", "limit": 5 }`

Both endpoints return HTTP 503 while Graphiti is disabled or unavailable.
