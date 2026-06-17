# TECH_SPEC.md
## Receipt‑Printer
**Project:** `receipt-printer`  
**Owner:** Axentx – Product Engineering  
**Status:** MVP → Production (target ship Q4 2026)  

A thermal‑printer abstraction layer that ingests PDF receipts and emits printer‑specific command streams (ESC/POS, CPCL, ZPL, etc.). It hides low‑level driver quirks, provides a unified async API, and can be embedded in any Node.js, Python, or Go service.

---

## 1. Architecture Overview
```
+-------------------+        +-------------------+        +-------------------+
|   Client SDKs     | <----> |   Receipt‑Printer | <----> |   Printer Driver  |
| (Node / Python / |        |   Service (API)   |        |   Plugins (DLL)   |
|   Go)             |        |   (Docker)        |        |   (vLLM, SGLang)  |
+-------------------+        +-------------------+        +-------------------+
          ^                           ^                           ^
          |                           |                           |
   HTTP/WS/GRPC                gRPC/REST                     Native
   (JSON)                     (protobuf)                  (C/C++)
```

* **Client SDKs** – language‑specific wrappers exposing a single `printReceipt(pdfBuffer, options)` call.  
* **Receipt‑Printer Service** – stateless microservice containerised with Docker, exposing a gRPC/REST API. Handles PDF parsing, rasterisation, command generation, and job queuing.  
* **Printer Driver Plugins** – dynamically loaded native libraries (C/C++) that translate raster data into device‑specific command sets. Plugins are isolated per‑printer model and loaded via a plugin manager.  

The service is horizontally scalable; each instance is identical and can be autoscaled behind a load balancer. State (job metadata, metrics) lives in Redis; persistent logs in PostgreSQL.

---

## 2. Core Components

| Component | Responsibility | Language / Tech |
|-----------|----------------|-----------------|
| **API Gateway** | HTTP/REST → gRPC translation, auth, rate‑limit | Envoy + Go |
| **gRPC Service** | `PrintJob` RPC, health checks | Go (grpc-go) |
| **PDF Processor** | PDF → bitmap raster (monochrome, 203 dpi) | C++ (poppler), exposed via cgo |
| **Raster Optimizer** | Dithering, compression, image scaling | Rust (image crate) |
| **Plugin Manager** | Load/unload printer drivers, sandboxing | Go (plugin package) |
| **Driver Plugins** | Bitmap → ESC/POS / CPCL / ZPL command stream | C/C++ (compiled per‑model) |
| **Job Queue** | Async job persistence, retries | Redis Streams |
| **Metrics & Tracing** | Prometheus, OpenTelemetry | Go |
| **Persistence** | Job audit log, error details | PostgreSQL 15 |
| **CI/CD** | Build, test, container publish | GitHub Actions, Docker BuildKit |

---

## 3. Data Model

### 3.1 PrintJob (PostgreSQL)

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Unique job identifier |
| `client_id` | TEXT | API key / tenant |
| `printer_model` | TEXT | Target printer model |
| `status` | ENUM(`queued`,`processing`,`completed`,`failed`) |
| `pdf_sha256` | BYTEA | Hash of input PDF (dedup) |
| `created_at` | TIMESTAMPTZ |
| `started_at` | TIMESTAMPTZ |
| `completed_at` | TIMESTAMPTZ |
| `error_message` | TEXT | NULL if success |
| `command_blob` | BYTEA | Raw printer command (optional for audit) |

### 3.2 Redis Job Payload (JSON)

```json
{
  "job_id": "uuid",
  "pdf": "<base64>",
  "options": {
    "density_dpi": 203,
    "dither": "floyd-steinberg",
    "cut_after": true
  }
}
```

---

## 4. API Specification

### 4.1 gRPC Service (`printer.v1.PrinterService`)

```proto
service PrinterService {
  // Submit a new print job
  rpc PrintJob (PrintJobRequest) returns (PrintJobResponse);

  // Stream status updates
  rpc WatchJob (WatchJobRequest) returns (stream JobStatus);

  // Health check
  rpc Health (HealthCheckRequest) returns (HealthCheckResponse);
}
```

#### `PrintJobRequest`

| Field | Type | Description |
|-------|------|-------------|
| `pdf` | `bytes` | PDF binary (max 5 MiB) |
| `printer_model` | `string` | Exact model identifier (e.g., `epson_tm‑T20`) |
| `options` | `PrintOptions` | Optional raster/command tweaks |

#### `PrintOptions`

| Field | Type | Default |
|-------|------|---------|
| `density_dpi` | `int32` | `203` |
| `dither` | `enum` (`NONE`, `FLOYD_STEINBERG`) | `FLOYD_STEINBERG` |
| `cut_after` | `bool` | `true` |
| `timeout_ms` | `int32` | `30000` |

#### `PrintJobResponse`

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `string` (UUID) | Identifier for tracking |
| `estimated_time_ms` | `int32` | Approx. processing time |

#### `JobStatus`

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `string` |
| `status` | `enum` (`QUEUED`,`PROCESSING`,`COMPLETED`,`FAILED`) |
| `progress_pct` | `int32` |
| `error_message` | `string` (optional) |

### 4.2 REST Wrapper (JSON)

`POST /v1/print`  
Body: same fields as `PrintJobRequest` (base64‑encoded PDF).  
Response: `{ "job_id": "...", "estimated_time_ms": 1234 }`

`GET /v1/status/{job_id}` – returns current `JobStatus`.

Authentication: API‑Key header `X-AXENTX-KEY`. Rate‑limit 60 req/min per key (Envoy).

---

## 5. Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Runtime** | Go 1.22 | Low‑latency, native concurrency, easy Docker |
| **PDF Rasterisation** | Poppler (C++) via cgo | Proven, high‑fidelity PDF rendering |
| **Image Processing** | Rust `image` crate | Safe, fast dithering & scaling |
| **Plugin System** | Go `plugin` (dlopen) | Runtime load/unload, isolation |
| **Driver Implementations** | C/C++ (static libs) | Direct hardware access, minimal overhead |
| **Message Queue** | Redis Streams | Simple, durable, low latency |
| **Metadata Store** | PostgreSQL 15 | ACID guarantees for audit |
| **Observability** | Prometheus + OpenTelemetry | Standard metrics & tracing |
| **Containerisation** | Docker (multi‑stage) | Reproducible builds, small runtime image |
| **CI/CD** | GitHub Actions, Docker BuildKit | Automated testing & publishing |
| **Testing** | Go `testing`, Rust `cargo test`, C++ GoogleTest | Full stack unit + integration coverage |

---

## 6. Dependencies

| Dependency | Version | License |
|------------|---------|---------|
| `github.com/grpc/grpc-go` | v1.62.0 | BSD‑3 |
| `github.com/go-redis/redis/v9` | v9.5.2 | MIT |
| `github.com/jackc/pgx/v5` | v5.4.0 | MIT |
| `github.com/prometheus/client_golang` | v1.18.0 | Apache‑2.0 |
| `poppler` | 23.09.0 | GPL‑2 (runtime only, allowed under commercial exception) |
| `image` (Rust) | 0.25 | MIT/Apache‑2.0 |
| `envoyproxy/envoy` | 1.30.0 | Apache‑2.0 |
| `docker` | BuildKit 0.12 | Apache‑2.0 |

All third‑party binaries are compiled into the final Docker image; licenses are recorded in `LICENSES/THIRD_PARTY.md`.

---

## 7. Deployment Diagram

```
+-------------------+      +-------------------+      +-------------------+
|   API Gateway     | ---> |  Receipt‑Printer  | ---> |  Redis Cluster    |
| (Envoy + Auth)    |      |  Service (Go)    |      +-------------------+
+-------------------+      +-------------------+                |
          |                         |                       |
          |                         v                       v
          |                +-------------------+   +-------------------+
          |                |  PostgreSQL DB    |   |  Plugin Dir (PVC) |
          |                +-------------------+   +-------------------+
          |                         |
          v                         v
+-------------------+      +-------------------+
|   Client SDKs     |      |  Printer Driver   |
| (Node/Py/Go)      |      |  Plugins (C++)    |
+-------------------+      +-------------------+
```

* **Kubernetes** (v1.28) deployment with a `StatefulSet` for PostgreSQL, `Deployment` for the service (replicas = autoscale), and `DaemonSet` for optional edge‑printer nodes.  
* **ConfigMaps** store static mapping `printer_model → plugin.so`.  
* **Secrets** hold API keys and TLS certs.  
* **Health probes** (`/healthz`) used by K8s liveness/readiness.

---

## 8. Security & Compliance

| Concern | Mitigation |
|---------|------------|
| **Input Validation** | PDF size capped (5 MiB); PDF parsing sandboxed via `seccomp` profile. |
| **Code Execution** | Plugins loaded in separate Linux namespaces; no network access. |
| **Data at Rest** | PostgreSQL encrypted with `pgcrypto`; Redis TLS enabled. |
| **Transport** | All external traffic TLS 1.3; internal gRPC uses mTLS. |
| **Auth** | API‑Key per tenant, stored in Vault; rate‑limit enforced at Envoy. |
| **Compliance** | Licenses tracked; no user‑identifiable data persisted beyond hash. |

---

## 9. Testing Strategy

| Layer | Tool | Coverage Goal |
|-------|------|---------------|
| Unit (Go) | `go test ./...` | 85 % |
| Unit (Rust) | `cargo test` | 80 % |
| Unit (C++) | GoogleTest | 75 % |
| Integration | Docker‑Compose (service + Redis + PG) | 90 % of API paths |
| End‑to‑End | Test harness that loads real printer plugins (mocked via virtual USB) | 70 % |
| Performance | Locust + custom latency probes | ≤ 150 ms per 300 KB PDF under load 100 RPS |
| Security | Trivy, Owasp‑ZAP | No critical findings |

All tests run on every PR; required status checks block merges.

---

## 10. Release & Versioning

* **Semantic Versioning** (MAJOR.MINOR.PATCH).  
* Docker images tagged `axentx/receipt-printer:<semver>` and `latest`.  
* Helm chart (`charts/receipt-printer`) versioned alongside the service.  
* Changelog maintained in `CHANGELOG.md`.  

**Release Checklist**
1. Increment version in `go.mod` & `Cargo.toml`.  
2. Run full CI pipeline, ensure all gates pass.  
3. Build multi‑arch Docker image (`linux/amd64`, `linux/arm64`).  
4. Push to Axentx container registry.  
5. Publish Helm chart and update documentation.  

---

## 11. Future Enhancements (Post‑MVP)

| Feature | Priority | Notes |
|---------|----------|-------|
| **WebSocket streaming** for real‑time status | High | Complement to REST polling |
| **Dynamic plugin marketplace** | Medium | Allow third‑party driver contributions |
| **AI‑enhanced layout detection** (using vLLM) | Low | Auto‑crop receipts, remove logos |
| **Batch printing API** | Medium | Submit multiple PDFs in one call |
| **Edge‑node auto‑discovery** | Low | Zero‑conf printer detection via mDNS |

---

*Prepared by:* Senior Product/Engineering Lead – Axentx  
*Date:* 2026‑06‑17  
*Document ID:* TP‑RP‑001  

---
