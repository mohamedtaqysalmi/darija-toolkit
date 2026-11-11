from fastapi.testclient import TestClient

from darija_toolkit.api import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]


def test_transliterate() -> None:
    response = client.post("/transliterate", json={"text": "salam labas 3lik"})
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "سلام لاباس عليك"
    assert body["tokens"]


def test_detect() -> None:
    response = client.post("/detect", json={"text": "wach bghiti"})
    assert response.status_code == 200
    assert response.json()["label"] == "darija_arabizi"


def test_normalize() -> None:
    response = client.post("/normalize", json={"text": "saaaafi!!!"})
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "safi!"
    assert body["changes"] >= 1


def test_openapi_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/transliterate" in paths
    assert "/detect" in paths
    assert "/normalize" in paths
