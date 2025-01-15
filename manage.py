from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
import secrets
import argparse

def create_session():
    engine = create_engine('sqlite:///o1_chat.db')
    Session = sessionmaker(bind=engine)
    return Session()

def create_user(name: str) -> User:
    """Create a new user with a random API key."""
    session = create_session()
    
    # Generate a random API key
    api_key = secrets.token_urlsafe(32)
    
    # Create new user
    user = User(name=name, api_key=api_key)
    session.add(user)
    session.commit()
    
    print(f"Created user: {name}")
    print(f"API Key: {api_key}")
    return user

def list_users():
    """List all users and their usage statistics."""
    session = create_session()
    users = session.query(User).all()
    
    print("\nUser Statistics:")
    print("-" * 80)
    print(f"{'Name':<20} {'Total Tokens':<15} {'Total Cost':<15} {'Last Used':<20}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.name:<20} {user.total_tokens:<15} ${user.total_cost:<14.4f} {user.last_used_at.strftime('%Y-%m-%d %H:%M')}")

def main():
    parser = argparse.ArgumentParser(description='Manage O1 Chat users')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create user command
    create_parser = subparsers.add_parser('create', help='Create a new user')
    create_parser.add_argument('name', help='User name')
    
    # List users command
    subparsers.add_parser('list', help='List all users')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_user(args.name)
    elif args.command == 'list':
        list_users()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 