# FastAPI Hello World

A minimal FastAPI application to get you started.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /items/{item_id}` - Example endpoint with parameters

## Documentation

- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative docs (ReDoc): `http://127.0.0.1:8000/redoc`

## Next Steps

- Add more endpoints
- Implement request body validation with Pydantic models
- Add database integration
- Implement authentication
