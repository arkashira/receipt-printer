# STORIES.md – receipt‑printer

## Overview
The **receipt‑printer** library provides a thin, cross‑platform abstraction over thermal receipt printers.  
It accepts a PDF (or PDF‑like buffer) and emits the exact byte stream required by the target printer model (ESC/POS, StarPRNT, etc.).  
The goal of this backlog is to deliver a **Minimum Viable Product (MVP)** that lets developers integrate receipt printing with a single function call, while laying the groundwork for extensibility, testing, and production‑grade reliability.

---

## Epics

| Epic | Description | MVP Priority |
|------|-------------|--------------|
| **E1 – Core PDF → Command Engine** | Parse PDF, rasterize to bitmap, map bitmap to printer command set, expose a simple API. | ✅ |
| **E2 – Printer Model Support** | Provide built‑in drivers for the most common thermal printers (ESC/POS, StarPRNT, Epson TM‑T20). | ✅ |
| **E3 – Configuration & Extensibility** | Allow callers to customize DPI, density, cut mode, and to plug‑in custom drivers. | ✅ |
| **E4 – Error Handling & Diagnostics** | Surface meaningful errors, expose logging hooks, and provide a diagnostic mode. | ✅ |
| **E5 – CI / Test Harness** | Automated unit & integration tests, sample printer emulator, CI pipeline. | ✅ |
| **E6 – Documentation & Samples** | README, API reference, quick‑start guide, example projects for Node, Python, Go. | ✅ |
| **E7 – Production‑Ready Packaging** | Publish to npm / PyPI / Go modules, semantic versioning, CI‑driven release. | ✅ |
| **E8 – Advanced Features (Future)** | QR/barcode generation, multi‑page receipts, cash‑drawer kick, receipt templates. | ❌ (post‑MVP) |

---

## User Story Backlog

### Epic E1 – Core PDF → Command Engine

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E1‑01** | **As a developer, I want a single `printReceipt(pdfBuffer, options)` function, so that I can print a receipt with minimal code.** | - Function signature exists in `src/index.ts` (or language‑specific entry point).<br>- Returns a `Promise<PrintResult>` (or sync result) containing `bytesSent` and `printerModel`.<br>- Throws a typed `ReceiptPrinterError` on failure. |
| **E1‑02** | **As a developer, I want the library to automatically rasterize the PDF to a 1‑bit bitmap at the printer’s native DPI, so that the output matches the original layout.** | - Uses a verified rasterizer (e.g., `pdf-lib` + `sharp` or `poppler`).<br>- Bitmap width matches printer’s printable width (e.g., 384 px for 58 mm).<br>- Unit test verifies that a sample PDF renders to an expected bitmap checksum. |
| **E1‑03** | **As a developer, I want the bitmap converted to the printer’s command set, so that the printer can render the receipt.** | - Implements ESC/POS “GS v 0” raster command (or equivalent for other models).<br>- Output byte array matches reference command sequence from the printer SDK. |
| **E1‑04** | **As a developer, I want the conversion to be performed in a streaming fashion, so that large receipts do not exhaust memory.** | - API accepts a `ReadableStream` or `Uint8Array` and returns a `ReadableStream` of command bytes.<br>- Memory usage stays < 5 MiB for a 2‑page receipt (validated by a performance test). |

### Epic E2 – Printer Model Support

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E2‑01** | **As a developer, I want built‑in support for ESC/POS printers, so that I can print to the majority of low‑cost devices.** | - Driver module `src/drivers/escpos.ts` implements required commands (initialize, line feed, cut, partial cut).<br>- Unit tests against a mock ESC/POS device confirm correct byte sequences. |
| **E2‑02** | **As a developer, I want built‑in support for StarPRNT printers, so that I can target Star devices without extra work.** | - Driver `src/drivers/starprnt.ts` implements Star-specific raster command and cut command.<br>- Compatibility test with a Star emulator passes. |
| **E2‑03** | **As a developer, I want built‑in support for Epson TM‑T20, so that I can use Epson’s popular model.** | - Driver `src/drivers/epson.ts` implements Epson’s command set (including cash‑drawer kick).<br>- Integration test with Epson’s sample firmware validates output. |
| **E2‑04** | **As a developer, I want the library to auto‑detect the printer model from a supplied identifier, so that I don’t have to manually select a driver.** | - `printReceipt` accepts `printerId` (e.g., USB vendor/product, network IP).<br>- Internal registry maps IDs to driver implementations.<br>- Fallback to a default driver with a warning log. |

### Epic E3 – Configuration & Extensibility

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E3‑01** | **As a developer, I want to configure DPI and print density, so that receipts look crisp on high‑resolution printers.** | - `options.dpi` (default 203) and `options.density` (0‑100) accepted.<br>- Changing DPI changes bitmap width accordingly.<br>- Tests verify that a 203 dpi PDF rasterizes to 384 px width, while 300 dpi yields 576 px. |
| **E3‑02** | **As a developer, I want to enable or disable automatic paper cutting, so that I can control post‑print behavior.** | - `options.cutMode` = `full | partial | none`.<br>- Driver emits the correct cut command or skips it.<br>- End‑to‑end test confirms cut bytes appear only when requested. |
| **E3‑03** | **As a developer, I want to plug‑in a custom driver, so that I can support niche printers.** | - Public API `registerDriver(modelId: string, driver: DriverInterface)`.<br>- Custom driver receives bitmap and returns command bytes.<br>- Sample custom driver in `examples/custom-driver/` passes integration test. |
| **E3‑04** | **As a developer, I want a logger hook, so that I can capture diagnostic information.** | - `options.logger?: Logger` where `Logger` implements `info`, `warn`, `error`.<br>- All major steps emit a log entry with timestamps.<br>- Test verifies that a mock logger receives expected calls. |

### Epic E4 – Error Handling & Diagnostics

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E4‑01** | **As a developer, I want clear error messages when PDF parsing fails, so that I can quickly fix input files.** | - Errors include `code: 'PDF_PARSE_ERROR'` and original stack trace.<br>- Unit test forces malformed PDF and asserts error type/message. |
| **E4‑02** | **As a developer, I want a diagnostic mode that returns the intermediate bitmap, so that I can debug rendering issues.** | - `options.diagnostic = true` returns `{ bitmap: Uint8Array, commands: Uint8Array }` in addition to normal result.<br>- Snapshot test validates bitmap checksum for a known PDF. |
| **E4‑03** | **As a developer, I want timeouts for network printers, so that my app does not hang indefinitely.** | - `options.timeoutMs` (default 5000).<br>- If no ACK from printer within timeout, `ReceiptPrinterError` with `code: 'PRINTER_TIMEOUT'` is thrown.<br>- Integration test with a mock network printer simulates timeout. |

### Epic E5 – CI / Test Harness

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E5‑01** | **As the team, we need unit tests covering > 90 % of the codebase, so that regressions are caught early.** | - Jest (or equivalent) config with coverage threshold 90 %.<br>- CI badge in README reflects current coverage. |
| **E5‑02** | **As the team, we need a printer emulator for automated integration tests, so that we can run CI without hardware.** | - `emulator/escpos-emulator.js` accepts command bytes and validates sequence.<br>- CI pipeline runs integration tests against emulator for each driver. |
| **E5‑03** | **As the team, we need a release pipeline that publishes to npm (and optionally PyPI/Go), so that customers receive stable versions.** | - GitHub Actions workflow `release.yml` triggers on `tag` push, runs tests, builds, and publishes.<br>- Semantic version bump enforced by `standard-version`. |

### Epic E6 – Documentation & Samples

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E6‑01** | **As a developer, I want a quick‑start guide, so that I can get a printer working in < 5 minutes.** | - README contains “Getting Started” section with install, sample code, and hardware checklist.<br>- Badge links to CI status and npm version. |
| **E6‑02** | **As a developer, I want API reference generated from JSDoc/TSDoc (or Sphinx for Python), so that I can discover all options.** | - `npm run docs` builds HTML docs in `docs/`.<br>- Docs are hosted via GitHub Pages (badge in README). |
| **E6‑03** | **As a developer, I want language‑specific examples (Node, Python, Go), so that I can adopt the library in my stack.** | - `examples/node/`, `examples/python/`, `examples/go/` each contain a runnable script that prints a sample receipt to the emulator. |
| **E6‑04** | **As a developer, I want a FAQ section covering common pitfalls (paper width, image inversion), so that I can troubleshoot quickly.** | - FAQ added to README with at least 5 entries.<br>- Each entry links to the relevant issue in the repo. |

### Epic E7 – Production‑Ready Packaging

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E7‑01** | **As a DevOps engineer, I want the library to be published as a single bundle (ESM & CJS), so that it works in all Node environments.** | - Build script produces `dist/receipt-printer.esm.js` and `dist/receipt-printer.cjs.js`.<br>- `package.json` fields `main`, `module`, `types` correctly point to bundles. |
| **E7‑02** | **As a DevOps engineer, I want a `peerDependency` on a PDF rasterizer library, so that consumers can control the rasterizer version.** | - `package.json` lists `pdf-lib` (or chosen rasterizer) as a peerDependency with version range `^2.0.0`.<br>- Installation guide mentions required peer install. |
| **E7‑03** | **As a product manager, I want a changelog automatically generated from commit messages, so that customers see what changed per release.** | - `standard-version` runs on `npm version` and updates `CHANGELOG.md`.<br>- CI publishes changelog to GitHub Releases. |

### Epic E8 – Advanced Features (Future)

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E8‑01** | **As a developer, I want QR‑code generation embedded in receipts, so that customers can scan promotions.** | - API `addQRCode(data, options)` that rasterizes QR into bitmap before final conversion.<br>- Unit test verifies correct QR pattern. |
| **E8‑02** | **As a developer, I want multi‑page receipt support, so that long transactions can be printed fully.** | - `printReceipt` accepts an array of PDFs or a multi‑page PDF and inserts paper feed commands between pages.<br>- Integration test prints a 3‑page receipt to emulator. |
| **E8‑03** | **As a developer, I want a cash‑drawer kick command, so that POS systems can open the drawer automatically.** | - Driver exposes `kickDrawer()` that emits the appropriate ESC/POS command.<br>- Test validates command byte sequence. |

---

## Prioritization for MVP (first release)

1. **E1‑01, E1‑02, E1‑03** – Core conversion pipeline.  
2. **E2‑01, E2‑02, E2‑03** – Baseline driver set.  
3. **E3‑01, E3‑02** – Essential configuration (DPI, cut).  
4. **E4‑01, E4‑02** – Robust error handling & diagnostics.  
5. **E5‑01, E5‑02** – Automated testing & emulator.  
6. **E6‑01, E6‑02, E6‑03** – Documentation & sample code.  
7. **E7‑01, E7‑02, E7‑03** – Packaging & release pipeline.  

All stories above are **shippable** and independent; they can be implemented in parallel by separate squads while maintaining a single integrated CI pipeline.

--- 

*End of STORIES.md*
