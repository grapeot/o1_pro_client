from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
import secrets
import string
import argparse
from datetime import datetime

def create_session():
    engine = create_engine('sqlite:///o1_chat.db')
    Session = sessionmaker(bind=engine)
    return Session()

def generate_token(length: int = 8) -> str:
    """Generate a random token of specified length using letters and numbers."""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_user(name: str, usage_limit: float = 1000.0) -> User:
    """Create a new user with a random token."""
    session = create_session()
    
    # Generate a unique token
    while True:
        token = generate_token()
        if not session.query(User).filter(User.token == token).first():
            break
    
    # Create new user
    user = User(
        name=name,
        token=token,
        usage_limit=usage_limit
    )
    session.add(user)
    session.commit()
    
    print(f"\nCreated user:")
    print(f"Name: {name}")
    print(f"Token: {token}")
    print(f"Usage limit: ${usage_limit:.2f}")
    return user

def list_users():
    """List all users and their usage statistics."""
    session = create_session()
    users = session.query(User).all()
    
    print("\nUser Statistics:")
    print("-" * 100)
    print(f"{'Name':<20} {'Token':<10} {'Total Cost':<12} {'Requests Today':<15} {'Last IP':<15} {'Status':<8} {'Last Used':<20}")
    print("-" * 100)
    
    for user in users:
        status = "Active" if user.is_active else "Inactive"
        last_used = user.last_used_at.strftime('%Y-%m-%d %H:%M') if user.last_used_at else "Never"
        daily_requests = f"{user.daily_request_count}/100" if user.daily_request_count else "0/100"
        
        print(f"{user.name:<20} {user.token:<10} ${user.total_cost:<10.2f} {daily_requests:<15} {user.last_ip or 'N/A':<15} {status:<8} {last_used}")

def toggle_user(token: str):
    """Toggle user active status."""
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    
    if not user:
        print(f"User with token {token} not found")
        return
    
    user.is_active = not user.is_active
    session.commit()
    
    status = "activated" if user.is_active else "deactivated"
    print(f"User {user.name} ({token}) has been {status}")

def reset_limits(token: str):
    """Reset user's daily request count."""
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    
    if not user:
        print(f"User with token {token} not found")
        return
    
    user.daily_request_count = 0
    user.last_request_date = None
    session.commit()
    
    print(f"Request limits reset for user {user.name} ({token})")

def main():
    parser = argparse.ArgumentParser(description='Manage O1 Chat users')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create user command
    create_parser = subparsers.add_parser('create', help='Create a new user')
    create_parser.add_argument('name', help='User name')
    create_parser.add_argument('--limit', type=float, default=1000.0, help='Usage limit in USD')
    
    # List users command
    subparsers.add_parser('list', help='List all users')
    
    # Toggle user command
    toggle_parser = subparsers.add_parser('toggle', help='Toggle user active status')
    toggle_parser.add_argument('token', help='User token')
    
    # Reset limits command
    reset_parser = subparsers.add_parser('reset', help='Reset user request limits')
    reset_parser.add_argument('token', help='User token')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_user(args.name, args.limit)
    elif args.command == 'list':
        list_users()
    elif args.command == 'toggle':
        toggle_user(args.token)
    elif args.command == 'reset':
        reset_limits(args.token)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 