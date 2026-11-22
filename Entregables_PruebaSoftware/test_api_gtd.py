"""Pruebas de API (equivalentes a la colección de Postman). Cubren TC-SYN-01..12.
Endpoints supuestos: /items. Ajustar a la API real."""
import time
import uuid
import pytest
import requests
from conftest import API_URL, USER, PASSWORD


@pytest.fixture(scope="module")
def headers():
    r = requests.post(f"{API_URL}/auth/login", json={"user": USER, "password": PASSWORD}, timeout=10)
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture
def item(headers):
    r = requests.post(f"{API_URL}/items", json={"title": f"QA-{uuid.uuid4().hex[:6]}"}, headers=headers, timeout=10)
    assert r.status_code == 201
    data = r.json()
    yield data
    requests.delete(f"{API_URL}/items/{data['id']}", headers=headers, timeout=10)


def test_TC_SYN_01_post_crea_elemento(headers):
    r = requests.post(f"{API_URL}/items", json={"title": "Nuevo QA"}, headers=headers, timeout=10)
    assert r.status_code == 201 and "id" in r.json()
    requests.delete(f"{API_URL}/items/{r.json()['id']}", headers=headers, timeout=10)


def test_TC_SYN_02_get_lista(headers, item):
    r = requests.get(f"{API_URL}/items", headers=headers, timeout=10)
    assert r.status_code == 200
    assert any(i["id"] == item["id"] for i in r.json())


def test_TC_SYN_03_get_inexistente(headers):
    r = requests.get(f"{API_URL}/items/{uuid.uuid4()}", headers=headers, timeout=10)
    assert r.status_code == 404


def test_TC_SYN_04_put_actualiza(headers, item):
    r = requests.put(f"{API_URL}/items/{item['id']}", json={"title": "Editado"}, headers=headers, timeout=10)
    assert r.status_code == 200
    assert requests.get(f"{API_URL}/items/{item['id']}", headers=headers, timeout=10).json()["title"] == "Editado"


def test_TC_SYN_05_delete(headers):
    nuevo = requests.post(f"{API_URL}/items", json={"title": "Borrar"}, headers=headers, timeout=10).json()
    assert requests.delete(f"{API_URL}/items/{nuevo['id']}", headers=headers, timeout=10).status_code == 204
    assert requests.get(f"{API_URL}/items/{nuevo['id']}", headers=headers, timeout=10).status_code == 404


def test_TC_SYN_06_payload_invalido(headers):
    r = requests.post(f"{API_URL}/items", json={}, headers=headers, timeout=10)
    assert r.status_code == 400


def test_TC_SYN_07_sin_token():
    r = requests.get(f"{API_URL}/items", timeout=10)
    assert r.status_code == 401


def test_TC_SYN_11_reintento_idempotente(headers):
    key = {"Idempotency-Key": uuid.uuid4().hex, **headers}
    a = requests.post(f"{API_URL}/items", json={"title": "Idem"}, headers=key, timeout=10)
    b = requests.post(f"{API_URL}/items", json={"title": "Idem"}, headers=key, timeout=10)
    assert a.json()["id"] == b.json()["id"]
    requests.delete(f"{API_URL}/items/{a.json()['id']}", headers=headers, timeout=10)


def test_TC_SYN_12_tiempo_respuesta(headers):
    t0 = time.perf_counter()
    r = requests.get(f"{API_URL}/items", headers=headers, timeout=10)
    assert r.status_code == 200
    assert time.perf_counter() - t0 < 2.0
