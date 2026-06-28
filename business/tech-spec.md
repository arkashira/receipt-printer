```markdown
# Tech Spec — receipt-printer v1

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | TypeScript (Node 20 LTS) | Strong typing for printer command structs; broad npm ecosystem |
| Runtime | Node.js 20 | Native Buffer/stream support for raw ESC/POS byte sequences |
| Framework | Fastify 4 | Low-overhead HTTP, schema validation via JSON Schema built-in |
| PDF parsing | `pdf2pic` + `sharp` | Rasterise PDF pages to bitmap for image-mode printing |
| Printer drivers | `node-escpos` (ESC/POS), custom Star STAR-PRN module | Cover 80%+ of thermal printers in market |
| Queue | BullMQ + Redis | Async print job handling; retries on printer timeout |
| ORM | Drizzle ORM + PostgreSQL | Type-safe queries; easy migrations |
| CLI tool | `commander` + `pkg` | Ship standalone binary for developer integration |

---

## Hosting (free-tier-first)

| Component | Platform | Free Tier Limit |
|---|---|---|
| API server | Railway.app (Starter) | 500 hrs/mo, 512 MB RAM |
| PostgreSQL | Supabase (free) | 500 MB, 2 CPU |
| Redis / BullMQ | Upstash Redis | 10k commands/day |
| File storage (PDFs) | Supabase Storage | 1 GB |
| CI/CD | GitHub Actions | 2000 min/mo |
| Secrets | Railway env vars | — |

Scale path: Fly.io (dedicated) → self-hosted on bare metal when print volume > 50k jobs/mo.

---

## Data Model

### `print_jobs`
```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
api_key_id    UUID NOT NULL REFERENCES api_keys(id)
status        TEXT NOT NULL CHECK (status IN ('queued','processing','done','failed'))
printer_model TEXT NOT NULL          -- e.g. 'EPSON_TM_T88V'
copies        SMALLINT DEFAULT 1
pdf_path      TEXT NOT NULL          -- Supabase storage path
raw_bytes_kb  INT                    -- size of generated command payload
error_msg     TEXT
created_at    TIMESTAMPTZ DEFAULT NOW()
completed_at  TIMESTAMPTZ
```

### `api_keys`
```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_email   TEXT NOT NULL
key_hash      TEXT NOT NULL UNIQUE    -- bcrypt hash of API key
label         TEXT
rate_limit    INT DEFAULT 100         -- requests/hour
created_at    TIMESTAMPTZ DEFAULT NOW()
revoked_at    TIMESTAMPTZ
```

### `supported_printers`
```sql
model_id      TEXT PRIMARY KEY        -- 'EPSON_TM_T88V'
vendor        TEXT NOT NULL
protocol      TEXT NOT NULL CHECK (protocol IN ('ESC/POS','STAR-PRN','ZPL'))
paper_width   SMALLINT NOT NULL       -- mm: 58 or 80
features      JSONB                   -- {"cutter":true,"logo":false,...}
```

### `conversion_logs`
```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
job_id        UUID REFERENCES print_jobs(id)
stage         TEXT                    -- 'pdf_parse','rasterise','encode'
duration_ms   INT
created_at    TIMESTAMPTZ DEFAULT NOW()
```

---

## API Surface

| # | Method | Path | Purpose |
|---|---|---|---|
| 1 | `POST` | `/v1/jobs` | Submit PDF (multipart) + printer model → enqueue print job |
| 2 | `GET` | `/v1/jobs/:id` | Poll job status + download link for raw command bytes |
| 3 | `DELETE` | `/v1/jobs/:id` | Cancel queued job |
| 4 | `GET` | `/v1/jobs` | List jobs for authenticated key (pagination: `?limit&cursor`) |
| 5 | `GET` | `/v1/printers` | List all supported printer models + protocols |
| 6 | `GET` | `/v1/printers/:model_id` | Capabilities detail for one printer model |
| 7 | `POST` | `/v1/convert` | Sync convert (≤ 2 MB PDF) → return raw bytes directly (no queue) |
| 8 | `POST` | `/v1/keys` | Provision new API key (admin-only, header-gated) |
| 9 | `DELETE` | `/v1/keys/:id` | Revoke API key |
| 10 | `GET` | `/v1/health` | Liveness + dependency check (DB, Redis, queue depth) |

All endpoints return `application/json`. Raw byte download via `/v1/jobs/:id?format=raw` returns `application/octet-stream`.

---

## Security Model

**Authentication**  
Bearer token (`Authorization: Bearer <api_key>`). Key is compared against `bcrypt` hash stored in DB. Never log raw keys.

**Secrets**  
All secrets (DB URL, Redis URL, Supabase service key, admin provisioning token) live in Railway environment variables. No secrets in repo or Docker image layers.

**IAM / Scopes**  
Two roles:
- `user` — can submit jobs, read own jobs, list printers
- `admin` — can provision/revoke keys; set via `ADMIN_TOKEN` env var checked on key-management endpoints

**Input validation**  
- PDF MIME-type check + magic byte validation before storage
- Max upload: 10 MB per PDF
- `printer_model` validated against `supported_printers` table
- All request bodies validated via Fastify JSON Schema (ajv)

**Transport**  
HTTPS enforced at Railway ingress. HTTP → HTTPS redirect enabled. HSTS header set.

**Rate limiting**  
Per-key limit stored in `api_keys.rate_limit`; enforced via BullMQ + sliding-window counter in Redis.

---

## Observability

**Logs**  
- Structured JSON logs via `pino`
- Fields: `job_id`, `api_key_id`, `printer_model`, `stage`, `duration_ms`, `error`
- Shipped to Railway's built-in log drain → Logtail free tier (50 GB/mo)

**Metrics**  
- Custom Prometheus endpoint at `/metrics` (via `fastify-metrics`)
- Key counters: `jobs_submitted_total`, `jobs_completed_total`, `jobs_failed_total`, `pdf_parse_duration_ms` (histogram)
- Scraped by Grafana Cloud free tier (10k series)

**Traces**  
- OpenTelemetry SDK with `@opentelemetry/auto-instrumentations-node`
- Export to Grafana Tempo (free tier, 50 GB traces/mo)
- Trace spans cover: HTTP handler → queue enqueue → worker stages (parse, rasterise, encode)

**Alerting**  
- Grafana alert: job failure rate > 5% over 5 min → email + webhook

---

## Build / CI

```yaml
# .github/workflows/ci.yml  (simplified)
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: {image: postgres:16, env: {POSTGRES_PASSWORD: test}}
      redis:    {image: redis:7}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '20', cache: 'npm'}
      - run: npm ci
      - run: npm run db:migrate
      - run: npm run test          # vitest
      - run: npm run lint          # eslint + tsc --noEmit

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: npm run build         # tsc → dist/
      - run: docker build -t receipt-printer:${{ github.sha }} .
      - run: docker scout cves --exit-code 1   # fail on critical CVEs

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: railwayapp/railway-action@v2
        with: {service: receipt-printer}
```

**Branch strategy**: `main` → auto-deploy to Railway prod. Feature branches require passing CI + 1 reviewer approval.

**DB migrations**: Drizzle Kit (`drizzle-kit push`) runs as a Railway deploy hook before new container starts.
```