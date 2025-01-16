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
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env.example` to `.env`
- Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=your_api_key_here
```

4. Create a test user:
```bash
python manage.py create "Your Name" --limit 100.0  # Set usage limit to $100
```

5. Start the server:
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
    "prompt_tokens": 50,
    "reasoning_tokens": 150,
    "completion_tokens": 100,
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

## Security Configuration

### API Key
Set your OpenAI API key in the environment:
```bash
export OPENAI_API_KEY=your_api_key_here
```
Or create a `.env` file based on `.env.example`.

### Database
The SQLite database file contains sensitive user data. Make sure to:
- Keep it in a secure location
- Set proper file permissions
- Back it up regularly
- Do not commit it to version control

### User Tokens
- Tokens are 8 characters long and randomly generated
- Keep tokens secure and treat them like passwords
- Consider rotating tokens periodically
- Do not share tokens in public repositories or logs

## License

MIT 