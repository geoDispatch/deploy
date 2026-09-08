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
├── docker-compose.yml
├── docs/
│   ├── README.md
│   ├── SETUP.md
│   └── LICENSE
└── Makefile
```

## Submodules

This repository uses Git submodules for core components:

- `agent` → AI decision service
- `supervisor` → orchestration/backend service
- `dashboard` → frontend interface
```