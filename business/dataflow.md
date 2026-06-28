```markdown
# receipt-printer — System Dataflow Architecture

## ASCII Block Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL DATA SOURCES                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  PDF Receipt │  │  POS System  │  │  Printer Capability DB   │  │
│  │  (file/URL)  │  │  (webhook)   │  │  (ESC/POS, TSPL, ZPL…)  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
└─────────┼─────────────────┼──────────────────────-┼────────────────┘
          │                 │                        │
          ▼                 ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         INGESTION LAYER                             │
│                   [AUTH BOUNDARY — API Key / JWT]                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  REST API Gateway  /v1/print  (multipart or JSON+base64)    │   │
│  │  • Rate limiter (token-bucket, per API key)                 │   │
│  │  • Request validator (MIME type, max 10 MB)                 │   │
│  │  • Job UUID assignment + timestamp                          │   │
│  └────────────────────────────┬─────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PROCESSING / TRANSFORM LAYER                    │
│  ┌───────────────┐    ┌─────────────────┐    ┌──────────────────┐  │
│  │  PDF Parser   │───▶│  Layout Engine  │───▶│  Command Codegen │  │
│  │  (pdfmium /   │    │  (column/table  │    │  ESC/POS, TSPL,  │  │
│  │   pdfplumber) │    │   extraction)   │    │  ZPL, STAR PRNT) │  │
│  └───────────────┘    └─────────────────┘    └────────┬─────────┘  │
│                                                        │            │
│  ┌─────────────────────────────────────────────────┐  │            │
│  │  Printer Profile Resolver                       │◀─┘            │
│  │  • model → command dialect mapping              │               │
│  │  • paper width normalization (58mm / 80mm)      │               │
│  │  • font/barcode capability check                │               │
│  └──────────────────────────┬──────────────────────┘               │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           STORAGE TIER                              │
│  ┌────────────────────┐  ┌───────────────────┐  ┌───────────────┐  │
│  │  Job Queue         │  │  Object Store     │  │  Profile DB   │  │
│  │  (Redis / BullMQ)  │  │  (S3-compatible)  │  │  (SQLite /    │  │
│  │  pending → done    │  │  raw PDF + output │  │   Postgres)   │  │
│  │  TTL: 24 h         │  │  TTL: 72 h        │  │  printer caps │  │
│  └────────────────────┘  └───────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       QUERY / SERVING LAYER                         │
│                   [AUTH BOUNDARY — same API Key]                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  GET /v1/jobs/{uuid}          — status + download URL        │   │
│  │  GET /v1/jobs/{uuid}/raw      — binary command stream        │   │
│  │  GET /v1/printers             — supported model catalogue    │   │
│  │  POST /v1/printers/detect     — USB/serial auto-detect hook  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          EGRESS TO USER                             │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────────────┐ │
│  │  Sync HTTP   │  │  Webhook / WS   │  │  SDK (Node / Python /  │ │
│  │  response    │  │  job-complete   │  │   PHP) wraps REST      │ │
│  │  (< 2 s PDF) │  │  notification   │  │   + streams to device  │ │
│  └──────────────┘  └─────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Inventory by Tier

### External Data Sources
- **PDF Receipt** — file upload (multipart/form-data) or URL reference; must be a valid PDF ≤ 10 MB
- **POS System** — upstream system posting receipts via webhook; authenticated with HMAC-SHA256 shared secret
- **Printer Capability DB** — static + community-contributed JSON manifests mapping model numbers → dialect, paper widths, supported features (barcodes, QR, cut commands)

### Ingestion Layer
- **REST API Gateway** — single `/v1/print` endpoint; accepts `printer_model` + `paper_width_mm` params
- **Rate Limiter** — token-bucket per API key; default 60 req/min, burst 10
- **Request Validator** — MIME type assertion (`application/pdf`), size cap, required-field check
- **Job ID Service** — UUIDv7 (time-ordered) assigned at intake; HTTP 202 returned immediately for async jobs

### Processing / Transform Layer
- **PDF Parser** — extracts text blocks, images, barcodes with bounding-box coordinates; uses pdfplumber (Python) or pdf.js (Node)
- **Layout Engine** — maps bounding boxes to thermal receipt columns; handles multi-column tables, line items, totals
- **Command Codegen** — dialect-aware emitter: ESC/POS (Epson/Star/80% of market), TSPL (TSC), ZPL (Zebra), STAR PRNT
- **Printer Profile Resolver** — looks up `printer_model` in Profile DB; falls back to generic ESC/POS 80 mm if unknown

### Storage Tier
| Store | Technology | Data | TTL |
|---|---|---|---|
| Job Queue | Redis + BullMQ | job state machine | 24 h |
| Object Store | MinIO / S3 | raw PDF, output binary | 72 h |
| Profile DB | SQLite (dev) / Postgres (prod) | printer cap manifests, API keys | permanent |

### Query / Serving Layer
- `GET /v1/jobs/{uuid}` — returns `{status, created_at, completed_at, download_url}`
- `GET /v1/jobs/{uuid}/raw` — streams binary command file; `Content-Type: application/octet-stream`
- `GET /v1/printers` — paginated catalogue of supported models with dialect tags
- `POST /v1/printers/detect` — accepts USB vendor/product ID or serial port descriptor; returns best-match profile

### Egress to User
- **Sync path** — small PDFs (< 100 KB) processed inline; binary returned in the HTTP 200 body within 2 s SLA
- **Async path** — large PDFs queued; client polls or receives webhook `POST` to registered callback URL on job completion
- **SDK layer** — thin wrappers (Node.js, Python, PHP) that call REST + pipe the binary stream directly to a local device file (`/dev/usb/lp0`, `\\.\COM3`, etc.)

---

## Auth Boundaries

| Boundary | Mechanism | Scope |
|---|---|---|
| Inbound API calls | Bearer API Key (header `X-API-Key`) | all `/v1/*` routes |
| POS webhook intake | HMAC-SHA256 signature on request body | `/v1/print` POST only |
| Job result retrieval | Same API Key **or** signed short-lived URL (15 min) | `/v1/jobs/{uuid}/raw` |
| Internal queue → worker | Redis AUTH password + TLS | internal only, not exposed |
| Object store | IAM policy / presigned URL | workers write; API issues read URLs |
| Printer profile writes | Admin key (separate tier) | `POST /v1/printers` manifest submissions |
```