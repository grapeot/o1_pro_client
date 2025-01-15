# O1 Pro Client

A simple web application for interacting with OpenAI's O1 model, featuring user management and cost tracking.

## Features

- Chat interface for O1 model
- User management with API keys
- Cost tracking per user
- Usage statistics
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
python manage.py create "Your Name"
```

4. Start the server:
```bash
python main.py
```

The server will start on http://localhost:8011

## API Endpoints

### POST /chat
Send a chat message to O1 model.

Request body:
```json
{
    "messages": [{"role": "user", "content": "Your message"}],
    "api_key": "your-api-key",
    "reasoning_effort": "low"
}
```

### GET /user/stats/{api_key}
Get usage statistics for a user.

## Management Commands

- Create user: `python manage.py create "User Name"`
- List users and stats: `python manage.py list`

## License

MIT 