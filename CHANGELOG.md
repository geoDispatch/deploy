# Changelog

All changes, modifications, and system configuration updates made to this project will be documented in this file.

## [2026-09-09]

### System Configuration
- Initialized [CHANGELOG.md](file:///home/kojack/Desktop/deploy/CHANGELOG.md) to track all project modifications and actions.
- Documented fix for Docker socket permission denial (`sudo usermod -aG docker $USER && newgrp docker`).

### Bug Fixes
- **mock-camara**: Created `mock-camara/app/` package directory and relocated `__init__.py`, `main.py`, and `models.py` into it to satisfy Dockerfile `COPY app/ ./app/` and module import resolution (`from app.models import ...`).
- **Networking**: Unified Docker Compose networks into a single `geodispatch-net` network by setting `networks.default.name = geodispatch-net` in [docker-compose.yml](file:///home/kojack/Desktop/deploy/docker-compose.yml) and removing explicit network isolation from [mock-camara/docker-compose.yml](file:///home/kojack/Desktop/deploy/mock-camara/docker-compose.yml), enabling inter-service DNS resolution (`supervisor` -> `mock-camara`).
- **Makefile**: Updated `prepare` target in [Makefile](file:///home/kojack/Desktop/deploy/Makefile) to automatically ensure `supervisor/.env` is initialized from `supervisor/.env.example` if not present.

