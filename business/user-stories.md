# user-stories.md

```markdown
# User Stories — receipt-printer

---

## Epic 1: PDF-to-Command Conversion

**As a** backend developer integrating POS checkout,
**I want** to pass a PDF receipt path and receive printer-ready ESC/POS commands,
**so that** I can print receipts without learning printer-specific binary protocols.

**Acceptance Criteria:**
- Input: valid PDF (single or multi-page); output: byte stream or file in target command language
- Supports ESC/POS (Epson), Star PRNT, and CPCL as target formats
- Font, line width, and barcode elements in the PDF are preserved in output
- Conversion completes in < 500 ms for receipts ≤ 5 pages on commodity hardware
- Returns a typed error if the PDF is corrupt or unsupported

**Complexity:** M

---

**As a** developer building a cloud POS,
**I want** to send a PDF receipt over HTTP and receive a print job ID,
**so that** I can decouple my application server from direct printer I/O.

**Acceptance Criteria:**
- REST endpoint `POST /jobs` accepts `multipart/form-data` with a PDF field and a `printer_id`
- Response returns `{ job_id, status: "queued" }` within 200 ms
- Job status is queryable via `GET /jobs/:id`
- Endpoint rejects files > 10 MB with `413` and non-PDF MIME types with `415`
- Auth via API key header

**Complexity:** M

---

**As a** developer handling multi-currency markets,
**I want** the converter to detect and preserve Unicode characters (Thai, Arabic, CJK) from the PDF,
**so that** receipts print correctly on printers with the matching code page.

**Acceptance Criteria:**
- Automatically selects the correct code page for the detected character set
- Falls back to image rendering for unsupported glyphs rather than dropping characters
- Test suite covers UTF-8 receipts in Thai (TIS-620), Arabic (CP720), and CJK (Big5/GB2312)
- Logs a warning when fallback rendering is used

**Complexity:** L

---

## Epic 2: Printer Discovery & Configuration

**As a** sysadmin deploying kiosks in a retail chain,
**I want** to auto-discover thermal printers on the local network via mDNS/USB enumeration,
**so that** I can register printers without manually entering IP addresses.

**Acceptance Criteria:**
- CLI command `receipt-printer discover` lists all detected printers with model, connection type, and IP/port
- Discovery runs in < 3 seconds on a /24 subnet
- Detected printers can be added to config with a single flag: `--add`
- Works for USB-attached printers on Linux and macOS

**Complexity:** M

---

**As a** developer testing locally,
**I want** a software printer emulator that writes output to a file,
**so that** I can develop and CI-test print flows without physical hardware.

**Acceptance Criteria:**
- `receipt-printer emulate --output ./output.bin` starts a virtual printer on a local TCP port
- Captured bytes are written to the specified file on job completion
- A companion `receipt-printer preview <file>` renders the binary as a PNG for visual inspection
- Emulator is usable as a library (not just CLI) for use in test suites

**Complexity:** M

---

**As a** retail operator managing 50+ printers,
**I want** to define printer profiles in a YAML config file,
**so that** I can version-control printer settings and deploy them via CI/CD.

**Acceptance Criteria:**
- Config schema supports: model, connection (USB/TCP), command-language, paper-width, code-page
- `receipt-printer validate-config` returns line-level errors for invalid YAML
- Config hot-reloads without restarting the service (SIGHUP or file-watch)
- Schema is published as a JSON Schema for IDE autocomplete

**Complexity:** S

---

## Epic 3: Developer Integration & SDK

**As a** Node.js developer,
**I want** an npm package with a typed `print(pdfBuffer, printerConfig)` function,
**so that** I can integrate receipt printing in three lines of code.

**Acceptance Criteria:**
- Package exports full TypeScript types; no `@types/` package required
- `print()` returns a `Promise<PrintResult>` with `{ success, jobId, warnings[] }`
- README includes a minimal working example (< 20 lines)
- Package ships with zero native binary dependencies on Linux x64 and arm64
- Publishes to npm under `@axentx/receipt-printer`

**Complexity:** M

---

**As a** Python developer building a Django POS backend,
**I want** a `pip install receipt-printer` package with the same API,
**so that** I am not forced to run a separate sidecar service.

**Acceptance Criteria:**
- Package published to PyPI under `receipt-printer`
- Exposes `receipt_printer.print(pdf_path_or_bytes, config: dict) -> PrintResult`
- Ships pre-built wheels for Linux x64, arm64, and macOS arm64
- Tested against Python 3.11 and 3.12

**Complexity:** L

---

**As a** developer integrating with an existing print queue (CUPS / Windows Print Spooler),
**I want** the library to submit jobs to the OS print system rather than talking to the printer directly,
**so that** I can use existing printer management infrastructure.

**Acceptance Criteria:**
- Optional `driver: "cups"` or `driver: "winspooler"` config field routes jobs to OS queue
- Correct printer name from the OS queue is resolved by the library
- Job status reflects the OS queue state (pending, printing, error)
- Documented clearly as an alternative to the direct TCP/USB driver

**Complexity:** L

---

## Epic 4: Reliability & Observability

**As a** developer operating a high-volume food-delivery platform,
**I want** automatic retry with exponential backoff when a printer is temporarily offline,
**so that** transient network blips do not cause missed receipts.

**Acceptance Criteria:**
- Retry policy configurable: `max_attempts`, `initial_delay_ms`, `backoff_multiplier`
- Default policy: 3 attempts, 500 ms initial delay, ×2 multiplier
- Retries are logged at WARN level with attempt count and elapsed time
- After all retries exhausted, job status transitions to `"failed"` and a `PrintError` is thrown/returned
- Dead-letter queue (configurable file or Redis list) captures failed jobs for manual replay

**Complexity:** M

---

**As a** DevOps engineer running receipt-printer in production,
**I want** Prometheus-compatible metrics exposed on `/metrics`,
**so that** I can alert on print failure rates and job queue depth.

**Acceptance Criteria:**
- Exposes: `receipt_printer_jobs_total{status}`, `receipt_printer_job_duration_seconds`, `receipt_printer_queue_depth`
- Metrics endpoint requires no auth by default but can be restricted by IP allowlist in config
- Compatible with Prometheus scrape format (text/plain; version=0.0.4)
- Grafana dashboard JSON bundled in `contrib/grafana/`

**Complexity:** S

---

**As a** developer debugging malformed receipt output,
**I want** structured JSON logs with per-job trace IDs,
**so that** I can correlate a bad print with the exact PDF and conversion step that produced it.

**Acceptance Criteria:**
- Every log line includes: `timestamp`, `level`, `job_id`, `printer_id`, `step` (parse/convert/send)
- Log level configurable via env var `LOG_LEVEL` (debug/info/warn/error)
- Sensitive fields (file paths with PII) are redactable via `log.redact_paths: true` in config
- `job_id` propagates to child spans if OpenTelemetry is configured

**Complexity:** S
```