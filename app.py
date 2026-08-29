"""

Run it in one of two ways:

    uvicorn app:app --reload        (best while writing code)
    python app.py                   (best inside Docker later)

Then  http://localhost:8000/docs in the browser.
"""

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ---------------------------------------------------------------------
# 1. Configuration - never hardcode, always read the environment
# ---------------------------------------------------------------------
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
APP_ENV = os.environ.get("APP_ENV", "local")


# ---------------------------------------------------------------------
# 2. The application object + our "database" (just a dict in memory)
# ---------------------------------------------------------------------
app = FastAPI(title="Server Inventory API", version="1.0.0")

servers = {
    1: {"id": 1, "name": "web-01", "ip": "10.0.0.11", "env": "prod"},
    2: {"id": 2, "name": "db-01", "ip": "10.0.0.21", "env": "prod"},
}


# ---------------------------------------------------------------------
# 3. The shape of the data we accept when someone sends a POST
# ---------------------------------------------------------------------
class NewServer(BaseModel):
    name: str
    ip: str
    env: str = "dev"


# ---------------------------------------------------------------------
# 4. The endpoints
# ---------------------------------------------------------------------

@app.get("/health")
def health():
    """Is the app alive? Docker and Kubernetes will call this."""
    return {"status": "ok", "env": APP_ENV}


@app.get("/servers")
def list_servers():
    """Return every server we know about."""
    print(f"GET /servers -> returning {len(servers)} servers")
    return list(servers.values())


@app.get("/servers/{server_id}")
def get_server(server_id: int):
    """Return one server by its id."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail=f"server {server_id} not found")
    return servers[server_id]


@app.post("/servers", status_code=201)
def create_server(new_server: NewServer):
    """Add a new server to the list."""
    new_id = max(servers.keys(), default=0) + 1

    server = {
        "id": new_id,
        "name": new_server.name,
        "ip": new_server.ip,
        "env": new_server.env,
    }

    servers[new_id] = server
    print(f"POST /servers -> created server {new_id} ({new_server.name})")
    return server


@app.delete("/servers/{server_id}")
def delete_server(server_id: int):
    """Remove a server from the list."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail=f"server {server_id} not found")

    deleted = servers.pop(server_id)
    print(f"DELETE /servers/{server_id} -> removed {deleted['name']}")
    return {"deleted": deleted}


# ---------------------------------------------------------------------
# 5. Start the server when we run: python app.py
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print(f"Starting Server Inventory API on {HOST}:{PORT} (env={APP_ENV})")
    uvicorn.run(app, host=HOST, port=PORT)




