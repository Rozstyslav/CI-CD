import json
import pytest
from peewee import SqliteDatabase

from app import app               
from db import ProductModel, db 

@pytest.fixture(scope="function")
def client():

    test_db = SqliteDatabase(":memory:")

    ProductModel._meta.set_database(test_db)

    test_db.bind([ProductModel], bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables([ProductModel])

    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c

    test_db.drop_tables([ProductModel])
    test_db.close()

    ProductModel._meta.set_database(db)

def test_products_crud_flow(client):

    r = client.get("/api/products")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


    new_item = {"name": "Sugar", "price": 32}
    r = client.post(
        "/api/products",
        data=json.dumps(new_item),
        content_type="application/json",
    )
    assert r.status_code in (200, 201)
    created = r.get_json()

    for k in ("id", "name", "price"):
        assert k in created
    pid = created["id"]

    r = client.get("/api/products")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Sugar"
    assert data[0]["price"] == 32


    r = client.get(f"/api/products/{pid}")
    assert r.status_code == 200
    item = r.get_json()
    assert item["id"] == pid
    assert item["name"] == "Sugar"
    assert item["price"] == 32


    r = client.put(
        f"/api/products/{pid}",
        data=json.dumps({"price": 40}),
        content_type="application/json",
    )
    assert r.status_code in (200, 204)

    r = client.get(f"/api/products/{pid}")
    assert r.status_code == 200
    item = r.get_json()
    assert item["price"] == 40


    r = client.delete(f"/api/products/{pid}")
    assert r.status_code in (200, 204)


    r = client.get(f"/api/products/{pid}")
    assert r.status_code in (404, 410)
