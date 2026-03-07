#!/usr/bin/env python3
"""
Simple script to create a test user and verify database setup
"""
from app.core.database import SessionLocal, init_db
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_user():
    """Create a test user in the database"""
    print("🔧 Initializing database...")
    init_db()
    
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=pwd_context.hash("testpassword123"),
            is_active=True,
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Test user created successfully!")
        print(f"   ID: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print(f"   Name: {test_user.full_name}")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
