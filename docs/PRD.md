# Receipt‑Printer PRD  

**Product:** receipt-printer  
**Team:** Architecture → Development → QA → Review → Validation  
**Owner:** Senior Product Lead (you)  
**Date:** 2026‑06‑17  
**Version:** 1.0  

---  

## 1. Problem Statement  

Developers building point‑of‑sale (POS), e‑commerce, or logistics applications must integrate with a wide variety of thermal receipt printers (Epson, Star, Bixolon, etc.). Each device requires its own command set (ESC/POS, CPCL, ZPL, etc.) and low‑level handling of PDF rasterisation, image dithering, and line‑feed timing.  

Current pain points:  

| Symptom | Impact |
|---------|--------|
| **Fragmented SDKs** – Teams import multiple vendor SDKs, increasing bundle size and maintenance overhead. | Higher dev cost, slower time‑to‑market. |
| **Inconsistent output** – PDF → printer conversion varies across devices, causing mis‑aligned text, truncated receipts, or unreadable barcodes. | Poor customer experience, increased support tickets. |
| **Hardware‑specific quirks** – Need to manually tune feed speed, cut commands, and paper width per model. | Time‑consuming debugging, higher defect rate. |
| **Limited automation** – CI pipelines cannot reliably test receipt printing without physical hardware. | Slower release cycles, manual QA. |

**Result:** Developers either avoid printing features or spend weeks building a custom abstraction layer, delaying revenue‑generating capabilities.

---

## 2. Target Users  

| Persona | Description | Primary Need |
|---------|-------------|--------------|
| **POS Front‑end Engineer** | Builds UI for checkout terminals (React, Flutter, native). | Simple API to send a receipt PDF and have it print correctly on any supported thermal printer. |
| **Backend Service Engineer** | Generates PDF receipts server‑side (Node, Go, Python). | Ability to stream PDF bytes to a printer over network/USB without handling device specifics. |
| **DevOps / QA Engineer** | Automates end‑to‑end tests for receipt printing. | Mockable printer interface and deterministic output for CI. |
| **Small Business SaaS Founder** | Offers invoicing/receipt service to merchants. | Out‑of‑the‑box printing support to reduce integration effort for customers. |

---

## 3. Goals & Success Metrics  

| Goal | Metric | Target (6 mo) |
|------|--------|---------------|
| **Reduce integration effort** | Avg. developer hours to add receipt printing | ≤ 4 h (down from ~24 h). |
| **Increase print success rate** | % of receipts printed without manual re‑tuning | ≥ 95 % across supported printers (baseline 78 %). |
| **Enable CI testing** | % of test suites that include receipt‑print validation | ≥ 80 % (baseline 0 %). |
| **Revenue impact** | New paying customers citing “built‑in receipt printing” as a deciding factor | ≥ 15 % of new deals (survey). |
| **Adoption** | Number of downstream Axentx products that import `receipt-printer` | ≥ 3 (e.g., POS‑SDK, Order‑Fulfilment, Mobile‑Wallet). |

---

## 4. Scope  

### 4.1 In‑Scope (Must‑Have)  

1. **Unified API**  
   - `printReceipt(pdfBuffer, options?) → Promise<PrintResult>`  
   - Options: `printerId`, `paperWidthMm`, `cutAfter`, `density`, `timeoutMs`.  

2. **Device Driver Layer**  
   - Built‑in support for the top 5 thermal printers by market share (Epson TM‑T20, Star TSP100, Bixolon SRP‑350, Zebra ZD410, Citizen CT‑S310).  
   - Auto‑detect via USB, Serial, or Network (TCP/IP).  

3. **PDF → Raster Conversion**  
   - Use `vLLM`‑accelerated rasterisation for high‑throughput (≥ 200 mm/s).  
   - Dithering algorithms (Floyd‑Steinberg, Ordered) selectable per printer capability.  

4. **Command Generation**  
   - Translate raster bitmap to printer‑specific command set (ESC/POS, CPCL, ZPL).  
   - Include cut, feed, and status‑request commands.  

5. **Error Handling & Retries**  
   - Detect paper‑out, overheating, communication errors.  
   - Expose structured error codes (`ERR_PAPER_OUT`, `ERR_TIMEOUT`, etc.).  

6. **Mock Driver for CI**  
   - Virtual printer that records command stream to a file for snapshot testing.  

7. **Documentation & Samples**  
   - Quick‑start guide (Node, Python, Go).  
   - API reference generated via Typedoc / Sphinx.  

8. **Packaging**  
   - Publish as `@axentx/receipt-printer` (npm) and `axentx-receipt-printer` (PyPI, Go module).  

### 4.2 Out‑of‑Scope (Will Not Be Delivered in v1)  

| Item | Reason |
|------|--------|
| **Full 3rd‑party printer catalog** – > 50 models. | Will be added via plug‑in architecture post‑launch. |
| **Bluetooth Low Energy (BLE) support** | Low adoption in target enterprise POS; defer to v2. |
| **Embedded firmware updates** | Outside the abstraction layer’s responsibility. |
| **Real‑time receipt preview UI** | Separate product (receipt‑designer). |
| **Cloud‑based printing service** | Requires separate SaaS infra; focus on on‑prem driver. |

---

## 5. Key Features (Prioritized)  

| Priority | Feature | Description | Acceptance Criteria |
|----------|---------|-------------|----------------------|
| P1 | **Unified Print API** | Single entry point for all languages. | `printReceipt` resolves with `PrintResult.success===true` on supported printers. |
| P1 | **Auto‑Detection & Driver Registry** | Detects printer on USB/Serial/TCP and loads correct driver. | `listPrinters()` returns accurate list; `printReceipt` works without explicit `printerId` when only one printer is attached. |
| P1 | **PDF Rasterisation Engine** | High‑performance conversion using vLLM. | 1 MB PDF → raster ≤ 150 ms on standard VM; output matches reference bitmap within 2 px. |
| P2 | **Command Set Translators** | ESC/POS, CPCL, ZPL implementations. | Printed receipt matches visual reference on each supported model. |
| P2 | **Error Detection & Reporting** | Real‑time status queries and structured errors. | Simulated paper‑out triggers `ERR_PAPER_OUT` and aborts gracefully. |
| P3 | **CI Mock Driver** | Virtual printer that records command stream. | Unit tests can assert exact command sequence using snapshot files. |
| P3 | **Cross‑Language Bindings** | Node (npm), Python (PyPI), Go (module). | Same behavior verified by integration tests in all three ecosystems. |
| P4 | **Dynamic Dithering Selection** | Choose dithering per printer capability. | High‑density printers use ordered dithering; low‑density use Floyd‑Steinberg; visual diff < 5 % error. |
| P4 | **Cut & Feed Customisation** | Fine‑grained control over post‑print actions. | `cutAfter:true` triggers cut command; `paperFeedLines:3` feeds exactly 3 lines. |

---

## 6. User Stories  

1. **As a POS front‑end engineer**, I want to call `printReceipt(pdf)` and have the receipt printed on any attached thermal printer without writing device‑specific code.  

2. **As a backend service**, I need to stream a generated PDF receipt directly to a network‑connected printer, handling timeouts automatically.  

3. **As a QA engineer**, I want to run my CI pipeline and verify that the generated command stream matches an approved snapshot, without needing physical hardware.  

4. **As a small‑business SaaS founder**, I want to enable receipt printing for my merchants with a single dependency, reducing onboarding friction.  

---

## 7. Technical Architecture Overview  

```
+-------------------+       +-------------------+       +-------------------+
|   Application     |       |   receipt-printer |       |   Physical Printer|
| (Node / Python /  | <---> |  (Unified API)    | <---> | (USB / Serial /   |
|   Go)             |       |  - Driver Registry|       |  TCP)             |
+-------------------+       |  - PDF Engine (vLLM)      |                   |
                            |  - Cmd Translators         |                   |
                            |  - Error Handler           |                   |
                            +-------------------+       +-------------------+
```

* **PDF Engine** leverages the verified `vLLM` inference engine for fast rasterisation.  
* **Driver Registry** maps detected hardware IDs to command translators.  
* **Command Translators** are thin wrappers around open‑source ESC/POS, CPCL, ZPL libraries (MIT licensed).  
* **Mock Driver** implements the same interface, writing binary streams to `./mock-output/<timestamp>.bin`.  

All components are written in **Rust** for safety and compiled to native binaries; language bindings generated via `cbindgen` (C), `pyo3` (Python), and `cgo` (Go).

---

## 8. Milestones & Timeline  

| Milestone | Deliverable | Owner | Due |
|-----------|-------------|-------|-----|
| **M1 – Foundations** | Repo scaffold, CI pipeline, Rust core library | Architecture | 2026‑06‑30 |
| **M2 – PDF Engine Integration** | vLLM rasterisation wrapper, benchmark suite | Engineering | 2026‑07‑15 |
| **M3 – Driver Registry & Auto‑Detect** | USB/Serial/TCP detection, 3 printer drivers | Engineering | 2026‑07‑31 |
| **M4 – Unified API & Error Model** | `printReceipt` implementation, error codes | Engineering | 2026‑08‑15 |
| **M5 – Mock Driver & CI Tests** | Virtual printer, snapshot tests for all bindings | QA | 2026‑08‑31 |
| **M6 – Documentation & Samples** | README, quick‑start, API reference | Product/Docs | 2026‑09‑10 |
| **M7 – Beta Release** | Publish v0.1.0 to internal registry, collect feedback | Release | 2026‑09‑20 |
| **M8 – Public GA** | Publish to npm, PyPI, Go module; marketing kit | Product/BD | 2026‑10‑05 |

---

## 9. Risks & Mitigations  

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Printer firmware incompatibility** | Medium | High (fails to print) | Maintain a driver test matrix; allow community plug‑ins for edge cases. |
| **vLLM licensing or performance regression** | Low | Medium | Pin vLLM version; fallback to pure CPU rasteriser if GPU unavailable. |
| **Cross‑language binding bugs** | Medium | Medium | Automated contract tests per language; CI runs on all three runtimes. |
| **Security (USB/Network exposure)** | Low | High | Sandbox driver processes; enforce least‑privilege OS permissions. |
| **Insufficient market coverage (only 5 printers)** | Medium | Medium | Design plug‑in architecture; early outreach to printer OEMs for driver contributions. |

---

## 10. Open Questions  

1. Should we expose a **printer‑profile** JSON to allow customers to add custom drivers without code changes?  
2. Will we need **cloud‑based receipt rendering** (PDF → raster) for low‑power devices, or is on‑device conversion sufficient?  
3. What is the preferred **license** for the final package (MIT vs Apache‑2.0) given dependencies?  

*Answers to be resolved in the next sprint planning session.*

---  

**Prepared by:**  
Senior Product Lead – Receipt‑Printer  
Axentx OS  

*All information is based on current company knowledge base and validated market signals.*
