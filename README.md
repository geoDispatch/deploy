# GeoDispatch Deployment (`deploy`)

Welcome to the **GeoDispatch** deployment repository! This repository orchestrates local development, multi-service composition, and containerized deployment for the entire GeoDispatch system.

---

## 🚀 Overview of Architecture & Setup

This repository uses a **Hybrid Git Submodule + Docker Compose Composition** pattern:

### 1. Hybrid Submodule + Compose Structure
- **Submodule Management**: Source code for `supervisor`, `agent`, `dashboard`, and `contracts` are tracked as Git submodules (configured in `.gitmodules`).
- **Native Service**: `mock-camara` lives natively inside `deploy/` as a dedicated mock service.
- **Root Compose (`docker-compose.yml`)**: Uses Docker Compose `include:` to stitch together individual service compose files (`agent/docker-compose.yml`, `supervisor/docker-compose.yml`, `dashboard/docker-compose.yml`, `mock-camara/docker-compose.yml`).
- **Shared Bridge Network**: All services join the `geodispatch-net` bridge network for inter-service communication.

### 2. Stack Components
- `supervisor/`: **Go Supervisor service** (manages state, dispatches tasks, connects to CAMARA and Python agent).
- `agent/`: **Python Agent service** (AI decision/logic engine).
- `dashboard/`: **SolidJS + Leaflet Dashboard** (Vite-based frontend displaying real-time vehicle and camera dispatch tracking).
- `contracts/`: **Shared Schemas & Examples** (JSON payloads and contract definitions).
- `mock-camara/`: **Mock CAMARA API** (simulates Nokia NaC / CAMARA network APIs for local dev and testing).

### 3. Environment & Security Standard (`.env.example`)
- `.env.example` serves as the master template.
- Running `make prepare` generates `.env` locally for your environment.
- **Security**: `.env` is explicitly ignored by `.gitignore` and **must never be committed** to Git.

---

## 📁 Repository Layout

```
deploy/
├── README.md                   <- Repository documentation
├── .env.example                <- Master environment template (tracked)
├── .env                        <- Local environment file (GITIGNORED, generated via `make prepare`)
├── .gitignore                  <- Git ignore patterns (.env, node_modules, __pycache__)
├── .gitmodules                 <- Git submodules tracking configuration
├── docker-compose.yml          <- Top-level Compose file stitching service sub-composes
├── Makefile                    <- Dev/ops workflow automation
├── supervisor/                 <- Git Submodule: Go Supervisor
│   ├── Dockerfile
│   └── docker-compose.yml
├── agent/                      <- Git Submodule: Python Agent
│   ├── Dockerfile
│   └── docker-compose.yml
├── dashboard/                  <- Git Submodule: SolidJS + Leaflet (Vite-based)
│   ├── Dockerfile
│   └── docker-compose.yml
├── contracts/                  <- Git Submodule: Shared Schemas & Examples
└── mock-camara/                <- Native Service: Mock CAMARA API
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 🔗 Submodules Configuration (`.gitmodules`)

The [`.gitmodules`](file:///Users/macroooowave/Desktop/deploy/.gitmodules) file maps local subdirectories to their corresponding remote repositories:

```ini
[submodule "supervisor"]
	path = supervisor
	url = https://github.com/geodispatch/supervisor
[submodule "agent"]
	path = agent
	url = https://github.com/geodispatch/agent
[submodule "dashboard"]
	path = dashboard
	url = https://github.com/geodispatch/dashboard
[submodule "contracts"]
	path = contracts
	url = https://github.com/geodispatch/contracts
```

---

## 🛠️ Quick Start Guide

### 1. Clone the Repository (with Submodules)

Because this repository uses submodules, clone with `--recurse-submodules`:

```bash
git clone --recurse-submodules https://github.com/geodispatch/deploy.git
cd deploy
```

If you already cloned without `--recurse-submodules`, initialize submodules by running:

```bash
make init
# or: git submodule update --init --recursive
```

### 2. Generate Local `.env` File

```bash
make prepare
```

### 3. Build & Run Services

Start all 4 services in the background:

```bash
make up
```

Verify service status:

```bash
make status
# or: docker compose ps
```

Tail logs from all services:

```bash
make logs
```

Stop services:

```bash
make down
```

---

## 🌐 Environment Variables & Service Communication

The following table details the environment variables, service endpoints, and port mappings used across GeoDispatch:

| Env Var | Used By | Purpose / Target Endpoint | Default Value |
|---|---|---|---|
| `SUPERVISOR_PORT` | Host mapping | `go-supervisor` HTTP port | `8080` |
| `SUPERVISOR_HOST` | Internal network | Service hostname | `go-supervisor` |
| `AGENT_URL` | `go-supervisor` | Target URL for Python Agent `/decide` | `http://python-agent:8000` |
| `CAMARA_URL` | `go-supervisor` | Target URL for mock or real Nokia NaC API | `http://mock-camara:8090` |
| `CAMARA_API_KEY` | `go-supervisor`, `mock-camara` | Shared secret API credential | `mock-secret-key-12345` |
| `AGENT_PORT` | Host mapping | `python-agent` HTTP port | `8000` |
| `DASHBOARD_PORT` | Host mapping | `dashboard` HTTP port | `3000` |
| `SUPERVISOR_WS_URL` | `dashboard` | Client WebSocket connection URL | `ws://localhost:8080/ws` |
| `MOCK_CAMARA_PORT` | Host mapping | `mock-camara` HTTP port | `8090` |

> [!NOTE]
> - `python-agent` responds to requests sent by `go-supervisor` via `AGENT_URL`; it makes no outbound service calls.
> - Port `8090` is assigned to `mock-camara` to prevent collisions with `supervisor` (`8080`), `agent` (`8000`), and `dashboard` (`3000`).

---

## 🔍 Verification

To verify the merged Docker Compose structure across all included service compose files, run:

```bash
docker compose config
```
