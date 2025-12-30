# Mesa 24/7 Backend Challenge

Payment processing and payout microservice for restaurant operations - Technical challenge

## Overview

Production-grade microservice built with FastAPI, SQLAlchemy, and PostgreSQL that handles:

- **Event ingestion** from payment processors (with strict idempotency)
- **Ledger accounting** (double-entry style bookkeeping per restaurant)
- **Balance computation** (available funds per restaurant)
- **Async payout generation** (batch process triggered by API)

## Tech Stack

- **Python 3.11+**
- **FastAPI** (async endpoints)
- **SQLAlchemy 2.x** (async ORM)
- **PostgreSQL 15+**
- **Alembic** (database migrations)
- **Docker Compose**
- **pytest** (testing framework)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/JordyDev-Villanueva/mesa247-backend-challenge.git
cd mesa247-backend-challenge
```

2. **Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Setup environment variables**

```bash
cp .env.example .env
```

4. **Start the database with Docker Compose**

```bash
docker-compose up -d db
```

5. **Run database migrations**

```bash
alembic upgrade head
```

6. **Start the application**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Project Structure

```
mesa247-backend-challenge/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core functionality (database, logging, exceptions)
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   └── main.py          # FastAPI application
├── alembic/             # Database migrations
├── tests/               # Test suite
├── sql/                 # Raw SQL queries
├── events/              # Test dataset (JSONL)
├── docker-compose.yml
└── requirements.txt
```

## Database Schema

### Tables

- **processor_events**: Stores events from payment processors (idempotent)
- **ledger_entries**: Double-entry ledger for all financial movements
- **payouts**: Payout records per restaurant
- **payout_items**: Line items breaking down payout calculations

## Development

### Running Tests

```bash
pytest
```

### Running with Docker Compose (Full Stack)

```bash
docker-compose up --build
```

### Code Formatting

```bash
black app/ tests/
ruff check app/ tests/
```

## API Endpoints

### Payment Processor Events

- `POST /v1/processor/events` - Ingest payment processor events (idempotent)

### Restaurant Balance

- `GET /v1/restaurants/{restaurant_id}/balance` - Get restaurant balance

### Payouts

- `POST /v1/payouts/run` - Generate payouts (async batch process)
- `GET /v1/payouts/{payout_id}` - Get payout details

## Features

✅ Idempotent event processing with database-level enforcement
✅ Double-entry ledger accounting system
✅ Real-time balance calculations
✅ Async payout generation
✅ Structured JSON logging
✅ Full API documentation (OpenAPI/Swagger)

## Implementation Status

- [x] Project setup and database models
- [ ] API endpoints implementation
- [ ] Business logic (services)
- [ ] Repository pattern
- [ ] Tests
- [ ] SQL queries
- [ ] Event dataset
- [ ] Documentation

## License

This is a technical challenge project for Mesa 24/7.

## Author

Jordy Dev Villanueva
