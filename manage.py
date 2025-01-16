from models import User
from database import get_session, init_db
import secrets
import string
import argparse
from datetime import datetime

def generate_token(length: int = 8) -> str:
    """Generate a random token of specified length using letters and numbers."""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_user(name: str, usage_limit: float = 1000.0) -> User:
    """Create a new user with a random token."""
    session = get_session()
    try:
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
    finally:
        session.close()

def list_users():
    """List all users and their usage statistics."""
    session = get_session()
    try:
        users = session.query(User).all()
        
        if not users:
            print("\nNo users found in the database.")
            return
        
        print("\nUser Statistics:")
        print("-" * 120)
        print(f"{'Name':<20} {'Token':<10} {'Total Cost':<12} {'Limit':<12} {'Remaining':<12} {'Requests':<15} {'Status':<8} {'Last Used':<20}")
        print("-" * 120)
        
        for user in users:
            status = "Active" if user.is_active else "Inactive"
            last_used = user.last_used_at.strftime('%Y-%m-%d %H:%M') if user.last_used_at else "Never"
            requests = f"{user.request_count}/100" if user.request_count is not None else "0/100"
            remaining = user.usage_limit - user.total_cost
            
            print(f"{user.name:<20} {user.token:<10} ${user.total_cost:<10.2f} ${user.usage_limit:<10.2f} ${remaining:<10.2f} {requests:<15} {status:<8} {last_used}")
    finally:
        session.close()

def toggle_user(token: str):
    """Toggle user active status."""
    session = get_session()
    try:
        user = session.query(User).filter(User.token == token).first()
        
        if not user:
            print(f"User with token {token} not found")
            return
        
        user.is_active = not user.is_active
        session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        print(f"User {user.name} ({token}) has been {status}")
    finally:
        session.close()

def reset_limits(token: str):
    """Reset user's request count."""
    session = get_session()
    try:
        user = session.query(User).filter(User.token == token).first()
        
        if not user:
            print(f"User with token {token} not found")
            return
        
        user.request_count = 0
        session.commit()
        
        print(f"Request limits reset for user {user.name} ({token})")
    finally:
        session.close()

def add_limit(token: str, amount: float):
    """Increase user's usage limit by specified amount."""
    session = get_session()
    try:
        user = session.query(User).filter(User.token == token).first()
        
        if not user:
            print(f"User with token {token} not found")
            return
        
        old_limit = user.usage_limit
        user.usage_limit += amount
        session.commit()
        
        remaining_budget = user.usage_limit - user.total_cost
        print(f"Usage limit for user {user.name} ({token}) increased by ${amount:.2f}")
        print(f"Old limit: ${old_limit:.2f}")
        print(f"New limit: ${user.usage_limit:.2f}")
        print(f"Current cost: ${user.total_cost:.2f}")
        print(f"Remaining budget: ${remaining_budget:.2f}")
    finally:
        session.close()

def main():
    # Initialize database
    init_db()
    
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
    
    # Add limit command
    add_limit_parser = subparsers.add_parser('add_limit', help='Add to user usage limit')
    add_limit_parser.add_argument('token', help='User token')
    add_limit_parser.add_argument('amount', type=float, help='Amount to add to usage limit in USD')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_user(args.name, args.limit)
    elif args.command == 'list':
        list_users()
    elif args.command == 'toggle':
        toggle_user(args.token)
    elif args.command == 'reset':
        reset_limits(args.token)
    elif args.command == 'add_limit':
        add_limit(args.token, args.amount)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 