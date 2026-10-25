"""Create or promote an administrator from environment variables; never expose this as a public endpoint."""
import os
from app.database import Base, SessionLocal, engine
from app.models import User
from app.security import hash_password

email = os.getenv("ADMIN_EMAIL", "").strip().lower()
password = os.getenv("ADMIN_PASSWORD", "")
name = os.getenv("ADMIN_NAME", "Dealership Admin").strip()
if not email or len(password) < 12:
    raise SystemExit("Set ADMIN_EMAIL and ADMIN_PASSWORD (at least 12 characters) before running this script.")
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    user = db.query(User).filter_by(email=email).one_or_none()
    if user:
        user.is_admin = True
        user.hashed_password = hash_password(password)
        user.full_name = name
    else:
        user = User(email=email, full_name=name, hashed_password=hash_password(password), is_admin=True)
        db.add(user)
    db.commit()
    print(f"Administrator account ready for {email}")
finally:
    db.close()
