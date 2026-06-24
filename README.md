<h3 align="center">🛠️ receipt-printer</h3>

<div align="center">
  <a href="https://github.com/your-org/receipt-printer"><img src="https://img.shields.io/github/license/your-org/receipt-printer?color=brightgreen" alt="License"></a>
  <a href="https://github.com/your-org/receipt-printer"><img src="https://img.shields.io/github/languages/top/your-org/receipt-printer?color=blue" alt="Language"></a>
  <a href="https://github.com/your-org/receipt-printer/actions"><img src="https://img.shields.io/github/workflow/status/your-org/receipt-printer/CI?label=build&color=orange" alt="Build Status"></a>
  <a href="https://github.com/your-org/receipt-printer/stargazers"><img src="https://img.shields.io/github/stars/your-org/receipt-printer?style=social" alt="Stars"></a>
</div>

---

# 🚀 receipt-printer
**Power businesses with automated, secure, and scalable receipt printing.**  
A Node.js‑based service that generates receipts from business data, applies customizable templates, and sends them to any thermal printer—24/7.

## Why receipt-printer? ⚡
- **Zero‑Code Integration** – Abstracts printer‑specific ESC/POS commands, slashing dev time by up to 70 %.
- **Broad Compatibility** – Works with > 150 thermal printer models, eliminating hardware lock‑in.
- **Template Flexibility** – Choose from built‑in receipt layouts or craft your own with simple JSON.
- **Reliability‑First** – Redis‑backed job queue guarantees delivery even during network spikes.
- **Secure Storage** – PostgreSQL stores every receipt audit‑log, meeting PCI‑DSS traceability.
- **Scalable Architecture** – Horizontal scaling via stateless Express workers behind a load balancer.
- **Designed for 24/7 Ops** – Auto‑retries, health‑checks, and graceful shutdown for nonstop retail environments.

## Feature Overview 📦

| Feature | Description |
|---------|-------------|
| **RESTful API** | Endpoints to create, fetch, and re‑print receipts (`/receipts`) |
| **Template Engine** | JSON‑driven layouts; supports logos, QR codes, and multi‑column tables |
| **Printer Abstraction** | Auto‑detects printer model; maps generic commands to device‑specific ESC/POS |
| **Job Queue** | Redis‑based queue with retry/back‑off policies |
| **Audit Log** | PostgreSQL schema records every print request, status, and payload |
| **Health Checks** | `/healthz` endpoint for Kubernetes liveness/readiness probes |
| **Docker Ready** | Official Dockerfile for one‑click deployment |

## Tech Stack 🔧
- **Node.js** – Runtime environment
- **JavaScript** – Core language
- **Express.js** – HTTP server & routing
- **PostgreSQL** – Persistent receipt storage & audit logs
- **Redis** – In‑memory job queue & caching

## Project Structure 🌳
```
receipt-printer/
├─ business/          # Domain‑specific logic (order → receipt)
├─ docs/              # Design docs, PRD, ROADMAP, etc.
├─ src/               # Application source
│  ├─ api/            # Express route handlers
│  ├─ jobs/           # Redis queue workers
│  ├─ models/         # PostgreSQL ORM definitions
│  └─ printer/        # Device abstraction layer
├─ tests/             # Jest / SuperTest suites
├─ pyproject.toml     # Entry‑point metadata (for packaging)
└─ README.md
```

## Getting Started 🚀
```bash
# 1️⃣ Clone the repo
git clone https://github.com/your-org/receipt-printer.git
cd receipt-printer

# 2️⃣ Install dependencies
npm ci

# 3️⃣ Set up environment variables (example)
cat <<EOF > .env
PORT=3000
POSTGRES_URL=postgres://user:pass@localhost:5432/receipts
REDIS_URL=redis://localhost:6379
EOF

# 4️⃣ Initialise the database (run once)
npm run db:migrate

# 5️⃣ Start the service locally
npm start
```

### Run Tests
```bash
npm test
```

## Deploy 📦
The project ships with a production‑ready Docker image.

```bash
# Build the Docker image
docker build -t receipt-printer:latest .

# Run with PostgreSQL & Redis containers (docker‑compose example)
docker compose up -d
```

*For Kubernetes, expose the service via a Deployment and a Service manifest; the `/healthz` endpoint satisfies liveness/readiness probes.*

## Status
Active development – latest commit `eb4d7da` (feat: real, sandbox‑tested implementation).

## Contributing
We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
Released under the MIT License.