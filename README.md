# Relay API

REST API for controlling DCT Tech USB relay modules via HID.

## Quick Start

```bash
# Clone and set up
git clone <repo-url> && cd relay-api
python -m venv venv && venv\Scripts\activate  # Windows
# source venv/bin/activate                    # Linux/macOS
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Run in mock mode (no hardware needed)
set RELAY_MOCK=true     # Windows
# export RELAY_MOCK=true  # Linux/macOS
python run.py
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Features

- **Single & Bulk Control** — Turn individual or all relay channels ON/OFF
- **State Tracking** — Query current relay states at any time
- **Fail-Safe** — All relays default to OFF on startup and shutdown
- **API Key Auth** — Optional `X-API-Key` header authentication
- **Audit Logging** — All state changes logged with ISO-8601 timestamps
- **Rate Limiting** — Configurable per-client request throttling
- **Mock Mode** — Develop and test without USB hardware

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/relays` | Get all relay states |
| `PUT` | `/api/v1/relays` | Set all relays to same state |
| `GET` | `/api/v1/relays/{channel}` | Get single relay state |
| `PUT` | `/api/v1/relays/{channel}` | Set single relay state |
| `GET` | `/api/v1/relays/device/info` | USB device information |
| `GET` | `/health` | Health check (no auth required) |

### Example

```bash
# Turn relay 1 ON
curl -X PUT http://localhost:8000/api/v1/relays/1 \
  -H "Content-Type: application/json" \
  -d '{"state": "on"}'

# With API key authentication
curl -X PUT http://localhost:8000/api/v1/relays/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"state": "on"}'
```

## Configuration

All settings are configured via environment variables with the `RELAY_` prefix. See [.env.example](.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `RELAY_MOCK` | `false` | Use in-memory mock instead of real hardware |
| `RELAY_CHANNELS` | `2` | Number of relay channels on the board |
| `RELAY_HOST` | `0.0.0.0` | Server bind address |
| `RELAY_PORT` | `8000` | Server port |
| `RELAY_API_KEY` | *(empty)* | API key for authentication (empty = disabled) |
| `RELAY_RATE_LIMIT` | `0` | Max requests/min per client IP (0 = disabled) |
| `RELAY_CORS_ORIGINS` | `["*"]` | Allowed CORS origins |

## Docker

```bash
# Build
docker build -t relay-api .

# Run with USB device passthrough
docker run -d \
  --name relay-api \
  --device /dev/hidraw0 \
  -p 8000:8000 \
  -e RELAY_API_KEY=your-secret-key \
  relay-api

# Run in mock mode
docker run -d -p 8000:8000 -e RELAY_MOCK=true relay-api
```

## Development

```bash
# Run tests
python -m pytest tests/ -v

# Type checking
python -m mypy app/
```

## Architecture

```
app/
├── main.py              # FastAPI app, lifespan, middleware
├── config.py            # Pydantic settings (env vars)
├── middleware.py         # Rate limiting
├── core/
│   ├── device.py        # RelayDevice protocol + HID/Mock implementations
│   └── exceptions.py    # Typed exception hierarchy
├── models/
│   └── schemas.py       # Pydantic request/response models
├── api/
│   ├── dependencies.py  # DI: auth, service access, device guard
│   └── v1/
│       ├── relays.py    # Relay control endpoints
│       └── system.py    # Health check
└── services/
    └── relay_service.py # Thread-safe business logic + audit logging
```

## License

MIT
