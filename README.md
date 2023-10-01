
---
# IBAN Validation API

Simple API for validating IBANs from Montenegro.

Some of the libraries used for implementation:
- FastAPI
- Asynchronous SQLAlchemy (for storing validation history)
- Alembic migrations
- ARQ - Simple Queues using Redis (for offloading insertion of validation history into background)
- Pytest for testing
- Schwifty IBAN validation library (ONLY FOR TESTING!!!)


The reason of using ARQ is to improve performance of API. Theoretically it can support much more traffic and request processing time is much lower.

Note:
I would like to point out that `schwifty` library is only used for generating IBAN codes for tests.
The reason behind this is I didn't want to use functions for calculating/checking checksums written in this project for 
testing (generating IBANs and calculating checksums), 
instead I used `schwifty` as completely independent source for generating codes.
That way, if there is something wrong in my code, we would see different behaviour compared to `schwifty`.


## Getting Started

Before starting, ensure Docker Compose is installed since this project is completely dockerized.

Copy `.env.example` file and rename it `.env`
```bash
cp .env.example .env
```

Start API service

```bash
docker compose up api
```
You should see logs like this, that means everything is up and running
``` bash
iban-worker-1  | 21:20:36: Starting worker for 1 functions: process_iban_validation_result
iban-worker-1  | 21:20:36: redis_version=7.2.1 mem_usage=1.08M clients_connected=1 db_keys=2 
iban-api-1     | INFO:     Will watch for changes in these directories: ['/app']
iban-api-1     | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
iban-api-1     | INFO:     Started reloader process [11] using WatchFiles
iban-api-1     | INFO:     Started server process [13]
iban-api-1     | INFO:     Waiting for application startup.
iban-api-1     | INFO:     Application startup complete.
```

## Testing

Just in case, before starting tests, ensure that other services are down
```bash
docker compose down
```

```bash
docker compose up tests
```
