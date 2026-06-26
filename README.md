<h3 align="center">🖨️ receipt-printer</h3>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: JavaScript](https://img.shields.io/badge/Language-JavaScript-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Build: Node.js](https://img.shields.io/badge/Build-Node.js-green.svg)](https://nodejs.org/)
[![Stars: 0](https://img.shields.io/github/stars/axentx/receipt-printer.svg)](https://github.com/axentx/receipt-printer/stargazers)

</div>

---

# 🚀 receipt-printer

**Power businesses with automated receipt generation and printing.**

## Why receipt-printer?

- **Automated Printing**: Streamline transaction processing with instant receipt generation and print output.
- **Template Flexibility**: Customize receipt layouts using HTML/CSS templates via a built-in CRUD UI and API.
- **Secure Data Handling**: Store transaction data securely with PostgreSQL-backed persistence.
- **Plug-and-Play Integration**: Support for multiple printer types through modular driver architecture.
- **Scalable Architecture**: Designed for 24/7 operation and high-volume environments.
- **Built for Retail & Hospitality**: Ideal for restaurants, kiosks, and retail chains requiring fast, reliable receipt handling.

## Feature Overview

| Feature              | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| Receipt Generation   | Converts raw transaction data into printable receipts                       |
| Template Management  | Editable HTML/CSS templates via UI and RESTful API                        |
| Printer Integration  | Modular drivers support various thermal and dot-matrix printers             |
| Secure Storage       | Uses PostgreSQL for persistent and secure transaction logging               |
| Redis Caching        | Optimized performance with Redis for caching frequently accessed templates  |
| PDF Conversion       | Python-based `pdf-converter` module to transform PDFs into printer commands |

## Tech Stack

- **Node.js**
- **JavaScript**
- **Redis**
- **PostgreSQL**
- **Express**
- **Python**

## Project Structure

```
receipt-printer/
├── business/         # Business logic modules
├── docs/             # Documentation files
├── src/              # Source code root
│   ├── api/          # REST API endpoints
│   ├── core/         # Core services like template engine and printer drivers
│   ├── db/           # Database schema and connection logic
│   └── utils/        # Utility functions
├── tests/            # Unit and integration tests
├── pyproject.toml    # Python dependencies and configuration
├── README.md         # This file
└── package.json      # Node.js dependencies and scripts
```

## Getting Started

### Prerequisites

Ensure you have installed:
- Node.js v18+
- PostgreSQL
- Redis

### Installation

```bash
git clone https://github.com/axentx/receipt-printer.git
cd receipt-printer
npm install
```

### Running Locally

Start the application with:

```bash
npm run start
```

Run tests with:

```bash
npm run test
```

### Environment Setup

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update database credentials and Redis settings accordingly.

## Deploy

To deploy the receipt-printer service:

```bash
# Build and push Docker image (if applicable)
docker build -t axentx/receipt-printer .
docker push axentx/receipt-printer
```

Deploy using your preferred container orchestration tool (e.g., Kubernetes or Docker Compose).

## Status

✅ Active development  
Latest commit: `2404c4c feat(receipt-printer): real, sandbox-tested implementation`

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.