# O1 Pro Client

A simple web application for interacting with OpenAI's O1 model, featuring user management and cost tracking.

## Features

- Modern chat interface with O1 Pro mode toggle
- User management with simple 8-character tokens
- Cost tracking and usage limits per user
- Detailed token usage tracking (input, reasoning, output)
- Thinking time display for each response
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
- Reset request count: `python manage.py reset <token>`

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
    "reasoning_effort": "medium"  # "medium" or "high" for O1 Pro mode
}
```

Response:
```json
{
    "content": "Model response",
    "input_tokens": 50,
    "reasoning_tokens": 150,
    "output_tokens": 100,
    "total_tokens": 300,
    "cost": 0.123,
    "user_total_cost": 1.234,
    "request_count": 5,
    "thinking_time": 12.34
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
    "request_count": 5,
    "usage_limit": 100.0,
    "is_active": true,
    "last_used": "2024-01-15T12:34:56",
    "last_ip": "127.0.0.1"
}
```

## Usage Control

- Usage limit: Configurable per user (default: $1000)
- Authentication: 401 response for invalid tokens
- Cost limit: 429 response when usage limit exceeded

## License

MIT 