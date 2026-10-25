def auth(token):
    return {"Authorization": f"Bearer {token}"}

def register(client, email="user@example.com"):
    return client.post("/api/auth/register", json={"email":email,"full_name":"Sample User","password":"secure-password"})

def vehicle_payload(**overrides):
    data = {"make":"Toyota","model":"Corolla","category":"Sedan","price":22000,"quantity":3,"description":"Reliable daily driver","image_url":""}
    data.update(overrides)
    return data

def test_register_hashes_password_and_returns_token(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json()["access_token"]
    from app.main import app
    from app.database import get_db
    from app.models import User
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    user = db.query(User).filter_by(email="user@example.com").one()
    assert user.hashed_password != "secure-password"
    db.close()
    db_generator.close()

def test_duplicate_registration_is_conflict(client):
    assert register(client).status_code == 201
    assert register(client).status_code == 409

def test_login_rejects_wrong_password(client):
    register(client)
    response = client.post("/api/auth/login", json={"email":"user@example.com","password":"wrong-password"})
    assert response.status_code == 401

def test_vehicle_list_requires_authentication(client):
    assert client.get("/api/vehicles").status_code == 401

def test_regular_user_cannot_create_vehicle(client, user_token):
    response = client.post("/api/vehicles", json=vehicle_payload(), headers=auth(user_token))
    assert response.status_code == 403

def test_admin_can_create_and_search_vehicle(client, admin_token):
    created = client.post("/api/vehicles", json=vehicle_payload(), headers=auth(admin_token))
    assert created.status_code == 201
    assert created.json()["quantity"] == 3
    found = client.get("/api/vehicles/search?make=toy&min_price=20000&max_price=23000", headers=auth(admin_token))
    assert found.status_code == 200
    assert len(found.json()) == 1

def test_invalid_vehicle_price_is_rejected(client, admin_token):
    response = client.post("/api/vehicles", json=vehicle_payload(price=-1), headers=auth(admin_token))
    assert response.status_code == 422

def test_user_purchase_decreases_stock(client, admin_token, user_token):
    vehicle = client.post("/api/vehicles", json=vehicle_payload(), headers=auth(admin_token)).json()
    response = client.post(f"/api/vehicles/{vehicle['id']}/purchase", json={"quantity":2}, headers=auth(user_token))
    assert response.status_code == 200
    assert response.json()["quantity"] == 1

def test_purchase_cannot_make_stock_negative(client, admin_token, user_token):
    vehicle = client.post("/api/vehicles", json=vehicle_payload(quantity=1), headers=auth(admin_token)).json()
    response = client.post(f"/api/vehicles/{vehicle['id']}/purchase", json={"quantity":2}, headers=auth(user_token))
    assert response.status_code == 409
    assert client.get("/api/vehicles", headers=auth(user_token)).json()[0]["quantity"] == 1

def test_regular_user_cannot_restock(client, admin_token, user_token):
    vehicle = client.post("/api/vehicles", json=vehicle_payload(quantity=1), headers=auth(admin_token)).json()
    response = client.post(f"/api/vehicles/{vehicle['id']}/restock", json={"quantity":2}, headers=auth(user_token))
    assert response.status_code == 403

def test_admin_can_restock_and_update_vehicle(client, admin_token):
    vehicle = client.post("/api/vehicles", json=vehicle_payload(quantity=1), headers=auth(admin_token)).json()
    restocked = client.post(f"/api/vehicles/{vehicle['id']}/restock", json={"quantity":4}, headers=auth(admin_token))
    assert restocked.status_code == 200 and restocked.json()["quantity"] == 5
    updated = client.put(f"/api/vehicles/{vehicle['id']}", json={"price":19999}, headers=auth(admin_token))
    assert updated.status_code == 200 and updated.json()["price"] == 19999

def test_admin_can_delete_vehicle(client, admin_token):
    vehicle = client.post("/api/vehicles", json=vehicle_payload(), headers=auth(admin_token)).json()
    response = client.delete(f"/api/vehicles/{vehicle['id']}", headers=auth(admin_token))
    assert response.status_code == 204

def test_search_rejects_inverted_price_range(client, user_token):
    response = client.get("/api/vehicles/search?min_price=50000&max_price=10000", headers=auth(user_token))
    assert response.status_code == 422
