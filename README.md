# receipt-printer

A minimal, pure‑Python testing framework that simulates printing receipts on
different thermal printer models and layouts. It is designed for the
*receipt‑printer* product’s “Testing and Validation” epic.

## Features

- **Model awareness** – supports multiple printer models (`PrinterModel` enum).
- **Layout validation** – checks line width and total line count (`ReceiptLayout`).
- **Test scenarios** – define a receipt’s content, model, and layout (`TestScenario`).
- **Error handling** – clear `ReceiptPrintError` messages for unsupported models,
  overflow, or too‑many lines.
- **Zero runtime dependencies** – only the Python standard library.

## Quick start
