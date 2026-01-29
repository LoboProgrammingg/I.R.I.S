---
trigger: always_on
---

# IRIS / Paytime AI Billing System — Deployment Rules (ALWAYS)

## Purpose
This document defines **non-negotiable deployment principles**.

The system must be:
- Cloud-agnostic
- Reproducible
- Environment-driven
- Safe for financial workloads

Deployment is treated as **part of the architecture**, not infrastructure trivia.

---

## 1. Core Deployment Principles

### 1.1 Cloud Agnosticism
- The system must NOT depend on:
  - Railway-specific APIs
  - AWS-only services
  - GCP-only features
- All services must be deployable using:
  - Docker
  - Environment variables
  - Standard networking

---

### 1.2 Environment-Driven Configuration
- All configuration MUST come from environment variables
- No hardcoded environment logic
- No config files per provider

Examples:
- DATABASE_URL
- REDIS_URL
- CELERY_BROKER_URL
- PAYTIME_API_KEY

---

### 1.3 Single Source of Truth
- `Dockerfile` is the canonical runtime definition
- Local, staging, and production must use the same image
- `docker-compose.yml` is for local dev only

---

## 2. Deployment Units

The system consists of independent deployable units:

| Unit | Responsibility |
|---|---|
| `api` | FastAPI app (webhooks + APIs) |
| `worker` | Celery worker |
| `beat` | Celery beat (scheduler) |

Each unit:
- Uses the same image
- Has different entrypoints/commands

---

## 3. Database & Migrations

### 3.1 Migration Rules
- Alembic migrations must be run:
  - Explicitly
  - Before new code handles traffic
- Migrations must NEVER:
  - Run automatically on app startup
  - Be coupled to web process lifecycle

---

### 3.2 Migration Responsibility
- Migrations are:
  - Manual in early stages
  - CI-driven in mature stages
- Failed migrations must block deploy

---

## 4. Zero-Downtime & Safety (MVP-Compatible)

For MVP:
- Rolling deploys are acceptable
- Brief read-only windows are acceptable
- No schema-breaking changes without backward compatibility

---

## 5. Secrets & Credentials
- Secrets must be injected by the platform
- Never baked into images
- Never logged
- Never committed

---

## 6. Observability at Deploy Time
- Health (`/health`) must pass before traffic
- Readiness (`/ready`) must pass before webhooks are enabled
- Deploy must fail if readiness fails

---

## 7. Prohibited Practices

The following are forbidden:
- Running migrations automatically on boot
- Provider-specific hacks in code
- Multiple Dockerfiles per environment
- Manual SSH changes in production
- Snowflake servers

---

## Final Rule

> **If a deployment cannot be reproduced locally with Docker, it is invalid.**

Deploy safety is critical for financial systems.
