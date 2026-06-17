# ROADMAP.md – receipt‑printer

## Vision
Provide a **plug‑and‑play abstraction layer** that lets any application turn a PDF receipt into the exact command stream required by a wide range of thermal receipt printers. Developers should be able to integrate a single npm / pip / cargo package, call `print(pdf)`, and have the receipt printed correctly on the target hardware without dealing with ESC/POS, ZPL, CPCL, or vendor SDKs.

---

## Milestones Overview

| Milestone | Target Release | Core Theme | MVP‑Critical Items |
|-----------|----------------|------------|--------------------|
| **MVP**   | **2026‑08‑15** | **“Print‑Now”** – basic end‑to‑end printing for the top 3 printer families | ✅ PDF → raster conversion  <br>✅ ESC/POS command generator  <br>✅ Auto‑detect printer model via USB/Serial/Bluetooth  <br>✅ Simple CLI & language bindings (Python & Node)  <br>✅ CI pipeline with unit & integration tests |
| **v1.0**  | 2026‑12‑01 | **“Universal”** – broaden hardware support, add raster‑optimizations | + Support for ZPL & CPCL printers  <br>+ Wi‑Fi & network printer discovery  <br>+ High‑DPI raster engine (image dithering)  <br>+ Structured logging & metrics  <br>+ Documentation site & SDK examples |
| **v2.0**  | 2027‑04‑15 | **“Enterprise Ready”** – reliability, scaling & SaaS integration | + Job queue & retry logic (Redis/Sidekiq)  <br>+ Cloud‑print gateway (REST API)  <br>+ Multi‑page receipt handling  <br>+ Auditable print logs & compliance mode  <br>+ Plug‑in architecture for custom command sets |
| **v3.0**  | 2027‑09‑30 | **“AI‑Enhanced”** – smart receipt generation & analytics | + PDF generation from structured receipt JSON  <br>+ Automatic logo & barcode embedding  <br>+ Integration with Axentx’s vLLM for on‑device receipt summarization  <br>+ Usage analytics dashboard  <br>+ Open‑source community extensions |

---

## MVP – “Print‑Now” (must‑have for launch)

| Category | Item | Description | Owner | Status |
|----------|------|-------------|-------|--------|
| **Core Engine** | PDF → raster bitmap | Use `poppler` (or `pdfium`) to rasterize each page to 1‑bit bitmap at 203 dpi (standard thermal width). | Engine Team | ✅ Implemented (prototype) |
| | Bitmap → ESC/POS commands | Map raster lines to ESC/POS `GS v 0` graphics commands, handling line wrapping and feed. | Engine Team | ✅ Implemented |
| **Hardware Abstraction** | Printer discovery | Detect USB, Serial, and Bluetooth printers; read device IDs to select command set. | HW Team | ✅ Implemented (USB & Serial) |
| | Command set selector | Auto‑select ESC/POS, ZPL, CPCL based on model DB (initial 3 models). | HW Team | ✅ Implemented |
| **Language Bindings** | Python package (`receipt_printer`) | Expose `print(pdf_path, device)` function; include simple CLI (`receipt-printer-cli`). | SDK Team | ✅ Implemented |
| | Node.js package (`@axentx/receipt-printer`) | Same API surface as Python; publish to npm. | SDK Team | ✅ Implemented |
| **Testing & CI** | Unit tests | PDF raster, command generation, device detection. | QA | ✅ 85 % coverage |
| | Integration tests | Real‑hardware test matrix (3 printers) via Docker‑compose + USB passthrough. | QA | ✅ 3/3 passed |
| | CI pipeline | GitHub Actions: lint → test → build wheels/npm packages → publish on tag. | DevOps | ✅ |
| **Documentation** | Quick‑start guide | Installation, example code, troubleshooting. | Docs | ✅ |
| | API reference | Auto‑generated via Sphinx (Python) & TypeDoc (Node). | Docs | ✅ |
| **Release** | Versioning & tagging | Semantic version `0.1.0` with changelog. | Release Manager | ✅ |
| | License & compliance | Apache‑2.0, include third‑party attributions. | Legal | ✅ |

**MVP Success Criteria**

- ✅ Print a 2‑page PDF receipt on each of the three supported printers without manual command tweaking.  
- ✅ < 2 seconds latency from `print()` call to first feed line on typical hardware.  
- ✅ Zero runtime crashes in 1 000 automated print jobs.  
- ✅ Documentation enables a developer with no printer experience to integrate in < 30 minutes.

---

## v1.0 – “Universal”

| Theme | Deliverables | Owner | Target |
|-------|--------------|-------|--------|
| **Hardware breadth** | Add ZPL (Zebra) & CPCL (Star) command generators; support network (TCP/IP) printers. | HW Team | Q4 2026 |
| **Performance** | High‑DPI (300 dpi) raster engine with Floyd‑Steinberg dithering; optional image compression. | Engine Team | Q4 2026 |
| **Discovery** | mDNS/SSDP discovery for Wi‑Fi printers; UI for manual IP entry. | HW Team | Q4 2026 |
| **Observability** | Structured JSON logs, Prometheus metrics (jobs, errors, latency). | Infra | Q4 2026 |
| **Developer experience** | Rich examples (POS, e‑commerce, kiosk); docs site with live sandbox (GitHub Pages). | Docs | Q4 2026 |

---

## v2.0 – “Enterprise Ready”

| Theme | Deliverables | Owner | Target |
|-------|--------------|-------|--------|
| **Reliability** | Print job queue with retry/back‑off (Redis + Sidekiq/ BullMQ). | Backend | Q1 2027 |
| **Cloud gateway** | REST API (`POST /print`) that accepts PDF + printer ID; returns job status. | Backend | Q1 2027 |
| **Multi‑page handling** | Automatic page breaks, paper‑feed optimization, optional cut command. | Engine | Q1 2027 |
| **Compliance** | Audit log (tamper‑evident), GDPR‑ready data handling, “secure mode” that disables logo embedding. | Security | Q1 2027 |
| **Extensibility** | Plug‑in system (dynamic loading of custom command modules). | SDK | Q1 2027 |

---

## v3.0 – “AI‑Enhanced”

| Theme | Deliverables | Owner | Target |
|-------|--------------|-------|--------|
| **Smart receipt generation** | Convert structured JSON receipt data → PDF using a templating engine (Handlebars). | Product | Q2 2027 |
| **Dynamic assets** | Auto‑embed merchant logo, QR code, barcode from URLs. | Engine | Q2 2027 |
| **LLM summarization** | Use Axentx vLLM to generate concise receipt summaries for low‑bandwidth printers. | AI | Q2 2027 |
| **Analytics dashboard** | Visualize print volume, error rates, device health per tenant. | Infra | Q3 2027 |
| **Community ecosystem** | Official plug‑in marketplace, contribution guidelines, bounty program. | Community | Q3 2027 |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hardware diversity (driver quirks) | Delays in v1/v2 | Maintain a **device‑profile DB**; partner with printer vendors for test units. |
| PDF raster performance on low‑end servers | Latency spikes | Offer optional native `pdfium` binary and a WebAssembly fallback. |
| Security of cloud gateway | Data breach | TLS everywhere, token‑based auth, audit logs, regular pen‑tests. |
| License compliance of third‑party raster libs | Legal exposure | Use only Apache‑2.0 / MIT licensed libs; keep SPDX headers. |

---

## Success Metrics

| Metric | Target (12 mo) |
|--------|----------------|
| Active developer installs | 5 000 |
| Successful print jobs | 1 M |
| 99.5 % job success rate | ≥ 99.5 % |
| Avg latency (print start) | ≤ 2 s |
| Community contributions (PRs) | ≥ 30 |

--- 

*Prepared by the receipt‑printer product team, aligned with Axentx’s growth objectives and validated market need.*
