# O1 Pro Client

A simple web application for interacting with OpenAI's O1 model, featuring user management and cost tracking.

## Features

- Chat interface for O1 model with adjustable reasoning effort
- User management with simple 8-character tokens
- Cost tracking and usage limits per user
- Daily rate limiting (100 requests per day)
- Usage statistics and monitoring
- Single-session chat (no persistent history)

## Setup

1. Create and activate Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install openai fastapi uvicorn sqlalchemy
```

3. Create a test user:
```bash
python manage.py create "Your Name" --limit 100.0  # Set usage limit to $100
```

4. Start the server:
```bash
python main.py
```

The server will start on http://localhost:8011

## User Management

The system uses simple 8-character tokens for authentication. Manage users with the following commands:

- Create user: `python manage.py create "User Name" --limit 1000.0`
- List users and stats: `python manage.py list`
- Toggle user status: `python manage.py toggle <token>`
- Reset daily limits: `python manage.py reset <token>`

## API Endpoints

### POST /chat
Send a chat message to O1 model.

Request body:
```json
{
    "messages": [
        {"role": "user", "content": "Your message"}
    ],
    "token": "your8char",
    "reasoning_effort": "low"  # Optional: "low", "medium", "high"
}
```

Response:
```json
{
    "content": "Model response",
    "total_tokens": 123,
    "cost": 0.123,
    "user_total_cost": 1.234,
    "daily_requests": 5
}
```

### GET /user/stats/{token}
Get usage statistics for a user.

Response:
```json
{
    "name": "User Name",
    "total_tokens": 1234,
    "total_cost": 1.234,
    "daily_requests": 5,
    "usage_limit": 100.0,
    "is_active": true,
    "last_used": "2024-01-15T12:34:56",
    "last_ip": "127.0.0.1"
}
```

## Rate Limiting and Usage Control

- Daily request limit: 100 requests per user per day
- Usage limit: Configurable per user (default: $1000)
- Rate limit status: 429 response when limit exceeded
- Authentication: 401 response for invalid tokens

## License

MIT 