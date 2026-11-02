import pytest
from starlette.testclient import TestClient
from implementations.api.app import app

@pytest.fixture(scope="module", autouse=True)
def init_lifespan():
    with TestClient(app) as c:
        yield c

client = TestClient(app)


def test_api_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Playground" in response.text


def test_api_rate_limiter():
    response = client.get("/api/v1/rate-limiter/check?client_id=test_api_client")
    assert response.status_code == 200
    data = response.json()
    assert "allowed" in data
    assert "remaining_tokens" in data


def test_api_snowflake():
    response = client.get("/api/v1/unique-id/snowflake")
    assert response.status_code == 200
    data = response.json()
    assert "snowflake_id" in data
    assert "base62_code" in data
    assert "components" in data


def test_api_url_shortener():
    # Shorten
    post_res = client.post(
        "/api/v1/url/shorten",
        json={"url": "https://bytebytego.com/courses/system-design-interview"},
    )
    assert post_res.status_code == 200
    data = post_res.json()
    short_code = data["short_code"]

    # Redirect
    get_res = client.get(f"/s/{short_code}", follow_redirects=False)
    assert get_res.status_code == 307
    assert get_res.headers["location"] == "https://bytebytego.com/courses/system-design-interview"


def test_api_autocomplete():
    res = client.get("/api/v1/autocomplete/search?prefix=sys")
    assert res.status_code == 200
    results = res.json()
    assert isinstance(results, list)
    assert len(results) > 0


def test_api_leaderboard():
    res = client.get("/api/v1/leaderboard/top?limit=3")
    assert res.status_code == 200
    top = res.json()
    assert len(top) == 3


def test_api_wallet_transfer():
    res = client.post(
        "/api/v1/wallet/transfer",
        json={
            "from_account": "user_alice",
            "to_account": "user_bob",
            "amount_cents": 1000,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"

