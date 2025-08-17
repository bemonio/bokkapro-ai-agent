# BokkaPro AI Agent

Autonomous route planning agent for BokkaPro's logistics platform.

## Features

- Retrieves logistics data from backend APIs.
- Generates optimized routes using OR-Tools.
- Reacts to real-time events and scheduled tasks.
- Exposes FastAPI endpoints for manual control.
- Designed for future AI/ML integration.

## Development

This project is under active development. All modules currently contain placeholder implementations.

### Running the API

```
uvicorn main:app --reload
```

### Testing

```
pytest
```

## Environment Variables

See `.env.example` for required settings.
