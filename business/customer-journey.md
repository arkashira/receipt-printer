`customer-journey.md` written to `/tmp/customer-journey.md`.

Key decisions made:

- **Persona is the developer, not the end merchant.** The real pain-holder is the engineer burning hours on ESC/POS command hell — the merchant is one step removed. Journey maps to that dev experience.
- **Try phase is the highest-risk drop-off.** No hardware in CI is the #1 abandonment trigger; the `--dry-run`/`MockPrinter` recommendation directly plugs that hole.
- **Expand phase bridges OSS→revenue.** Given the confidence score (0.1) and absent TAM data, the commercial add-on path (fleet management, SLA license) is the only plausible monetization without needing large market data — it rides on individual dev advocacy scaling to team/agency use.
- **Metrics are proxy-friendly** — all measurable via GitHub, PyPI/npm download stats, and issue tracker without needing instrumented analytics.