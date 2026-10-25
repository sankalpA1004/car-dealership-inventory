"""REST API for the car dealership inventory kata."""
import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Purchase, User, Vehicle
from .schemas import LoginRequest, QuantityRequest, RegisterRequest, TokenResponse, VehicleCreate, VehicleResponse, VehicleUpdate
from .security import create_access_token, decode_subject, hash_password, verify_password

@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="AutoHaus Inventory API", version="1.0.0", description="JWT-secured car dealership inventory API", lifespan=lifespan)
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in origins], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
bearer = HTTPBearer(auto_error=False)


@app.get("/api/health")
def health():
    return {"status": "ok"}

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    subject = decode_subject(credentials.credentials)
    if not subject or not subject.isdigit():
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    user = db.get(User, int(subject))
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user

def admin_user(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Administrator privileges required")
    return user

@app.post("/api/auth/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    user = User(email=email, full_name=payload.full_name.strip(), hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    return TokenResponse(access_token=create_access_token(str(user.id)), is_admin=user.is_admin, full_name=user.full_name)

@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return TokenResponse(access_token=create_access_token(str(user.id)), is_admin=user.is_admin, full_name=user.full_name)

@app.get("/api/vehicles", response_model=list[VehicleResponse])
def list_vehicles(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return list(db.scalars(select(Vehicle).order_by(Vehicle.id.desc())).all())

@app.get("/api/vehicles/search", response_model=list[VehicleResponse])
def search_vehicles(make: str | None = None, model: str | None = None, category: str | None = None,
                    min_price: float | None = Query(default=None, ge=0), max_price: float | None = Query(default=None, ge=0),
                    db: Session = Depends(get_db), user: User = Depends(current_user)):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot exceed max_price")
    stmt = select(Vehicle)
    if make and make.strip(): stmt = stmt.where(Vehicle.make.ilike(f"%{make.strip()}%"))
    if model and model.strip(): stmt = stmt.where(Vehicle.model.ilike(f"%{model.strip()}%"))
    if category and category.strip(): stmt = stmt.where(Vehicle.category.ilike(f"%{category.strip()}%"))
    if min_price is not None: stmt = stmt.where(Vehicle.price >= min_price)
    if max_price is not None: stmt = stmt.where(Vehicle.price <= max_price)
    return list(db.scalars(stmt.order_by(Vehicle.id.desc())).all())

@app.post("/api/vehicles", response_model=VehicleResponse, status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle); db.commit(); db.refresh(vehicle)
    return vehicle

@app.put("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None: raise HTTPException(status_code=404, detail="Vehicle not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None: setattr(vehicle, key, value)
    db.commit(); db.refresh(vehicle)
    return vehicle

@app.delete("/api/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None: raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle); db.commit()

@app.post("/api/vehicles/{vehicle_id}/purchase", response_model=VehicleResponse)
def purchase_vehicle(vehicle_id: int, payload: QuantityRequest = QuantityRequest(), db: Session = Depends(get_db), user: User = Depends(current_user)):
    # Atomic conditional update prevents overselling when requests arrive concurrently.
    result = db.execute(update(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.quantity >= payload.quantity).values(quantity=Vehicle.quantity - payload.quantity))
    if result.rowcount == 0:
        db.rollback()
        if db.get(Vehicle, vehicle_id) is None: raise HTTPException(status_code=404, detail="Vehicle not found")
        raise HTTPException(status_code=409, detail="Insufficient stock")
    vehicle = db.get(Vehicle, vehicle_id)
    db.add(Purchase(user_id=user.id, vehicle_id=vehicle.id, quantity=payload.quantity, unit_price=vehicle.price))
    db.commit(); db.refresh(vehicle)
    return vehicle

@app.post("/api/vehicles/{vehicle_id}/restock", response_model=VehicleResponse)
def restock_vehicle(vehicle_id: int, payload: QuantityRequest, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None: raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle.quantity += payload.quantity
    db.commit(); db.refresh(vehicle)
    return vehicle
