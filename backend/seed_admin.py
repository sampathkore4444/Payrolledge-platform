from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@payrolledge.com").first()
if not existing:
    admin = User(
        email="admin@payrolledge.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True,
        is_superuser=True
    )
    db.add(admin)
    db.commit()
    print("Admin user created: admin@payrolledge.com / admin123")
else:
    print("Admin user already exists")

db.close()
