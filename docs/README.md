<<<<<<< HEAD
# geoDispatch — Deploy

This directory contains deployment documentation, runbooks, and environment-specific instructions for the `geoDispatch` platform.

## Purpose

Use this documentation to:

- Deploy services consistently across environments
- Configure required environment variables and secrets
- Validate deployment health after release
- Troubleshoot common deployment failures
- Roll back safely when needed

## Code Structure

```text
geoDispatch/deploy
├── agent/        (git submodule)
├── dashboard/    (git submodule)
├── supervisor/   (git submodule)
├── .env.example
├── .gitignore
├── .gitmodules
├── docker-compose.yml
├── docs/
│   ├── README.md
│   ├── SETUP.md
│   └── LICENSE.md
└── Makefile
```

## Submodules

This repository uses Git submodules for core components:

- `agent` → AI decision service
- `supervisor` → orchestration/backend service
- `dashboard` → frontend interface
=======
# GeoDispatch Deployment Repository (`deploy`)

This repository orchestrates the build, deployment, and local multi-service composition for **GeoDispatch**.

## Architecture & Ownership

```
deploy/
├── .env.example                <- Master environment template (tracked)
├── .env                        <- Local environment file (gitignored)
├── .gitignore                  <- Git ignore configuration
├── .gitmodules                 <- Submodule repository tracking
├── docker-compose.yml          <- Root Compose file (includes service composes)
├── Makefile                    <- Dev/ops workflow automation
├── supervisor/                 <- Submodule: Go Supervisor service
├── agent/                      <- Submodule: Python Agent service
├── dashboard/                  <- Submodule: SolidJS + Leaflet Dashboard (Vite-based)
├── contracts/                  <- Submodule: Shared JSON Schemas & Examples
└── mock-camara/                <- Native repo service: Mock CAMARA API server
```

- **Submodules**: `supervisor`, `agent`, `dashboard`, and `contracts` are separate repositories tracked as Git submodules in `.gitmodules`.
- **Native Service**: `mock-camara` lives natively inside `deploy/`.
- **Network**: All services communicate over the `geodispatch-net` bridge network.

## Quick Start

### 1. Clone the Repository

When cloning for the first time, ensure you include submodules:
```bash
git clone --recurse-submodules https://github.com/geodispatch/deploy.git
cd deploy
```

If you already cloned without `--recurse-submodules`, initialize submodules with:
```bash
make init
```

### 2. Environment Setup

Generate your local `.env` file from the example template:
```bash
make prepare
```

*Note: `.env` is gitignored to protect local credentials.*

### 3. Build & Run Services

Start all services in detached mode:
```bash
make up
```

Check running container status:
```bash
make status
```

Follow container logs:
```bash
make logs
```

Stop services:
```bash
make down
```

### 4. Updating Submodules

To pull the latest commits from all submodule main branches:
```bash
make update-submodules
```
>>>>>>> 5ef440c (deploy under testing: NOT *ready-to-use* YET)
