"""
Unified Interactive System Design API & Playground
Exposes live endpoints for all core distributed system patterns.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from starlette.staticfiles import StaticFiles

# Core implementations
from implementations.rate_limiter import (
    TokenBucketRateLimiter,
    SlidingWindowCounterRateLimiter,
)
from implementations.consistent_hashing import ConsistentHashRing, ConsistentHashSimulator
from implementations.unique_id_generator import SnowflakeIDGenerator, Base62
from implementations.url_shortener import URLShortenerService
from implementations.search_autocomplete import SearchAutocompleteSystem
from implementations.leaderboard import LeaderboardService
from implementations.digital_wallet import DigitalWalletService
from implementations.payment_system import DoubleEntryLedger, AccountType
from implementations.metrics_monitoring import MetricsMonitoringEngine, AlertRule, AlertState
from implementations.object_storage import ObjectStorageService

# Global service singletons
token_limiter = TokenBucketRateLimiter(capacity=10, refill_rate=2.0)
hash_ring = ConsistentHashRing(nodes=["node-alpha", "node-beta", "node-gamma"], vnodes_per_node=50)
snowflake_gen = SnowflakeIDGenerator(datacenter_id=1, worker_id=1)
url_service = URLShortenerService()
autocomplete_service = SearchAutocompleteSystem(top_k_size=5)
leaderboard_service = LeaderboardService()
wallet_service = DigitalWalletService()
ledger = DoubleEntryLedger()
metrics_engine = MetricsMonitoringEngine()
storage_service = ObjectStorageService(chunk_size=64 * 1024)

# Seed initial demonstration data
def _seed_data():
    # Autocomplete dictionary
    terms = {
        "system design": 1500,
        "system design interview": 1200,
        "system design primer": 950,
        "scalability patterns": 800,
        "consistent hashing": 750,
        "rate limiter algorithm": 600,
        "redis zset": 500,
        "kafka message queue": 450,
        "snowflake id": 400,
        "microservices architecture": 350,
    }
    autocomplete_service.bulk_load(terms)

    # Leaderboard players
    leaderboard_service.update_score("Alice", 9850)
    leaderboard_service.update_score("Bob", 8400)
    leaderboard_service.update_score("Charlie", 7200)
    leaderboard_service.update_score("Diana", 6900)
    leaderboard_service.update_score("Evan", 5100)

    # Wallets
    wallet_service.create_wallet("user_alice", initial_deposit_cents=50000)
    wallet_service.create_wallet("user_bob", initial_deposit_cents=25000)
    wallet_service.create_wallet("merchant_stripe", initial_deposit_cents=1000000)

    # Ledger
    ledger.create_account("vault_bank", AccountType.ASSET)
    ledger.create_account("user_alice_liability", AccountType.LIABILITY)
    ledger.create_account("user_bob_liability", AccountType.LIABILITY)
    ledger.transfer("vault_bank", "user_alice_liability", 50000, "Initial Bank Deposit")
    ledger.transfer("vault_bank", "user_bob_liability", 25000, "Initial Bank Deposit")

    # Metrics rule
    metrics_engine.register_alert_rule(
        AlertRule(
            rule_name="HighCPUUsage",
            metric_name="cpu_usage",
            threshold=85.0,
            operator=">",
            duration_samples=2,
        )
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed_data()
    yield


app = FastAPI(
    title="System Design Implementations API",
    description="Live interactive implementations of distributed system architectures from System Design Interview.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount VitePress static documentation portal
docs_dist_path = Path(__file__).resolve().parent.parent.parent / "docs" / ".vitepress" / "dist"
if docs_dist_path.exists():
    app.mount("/portal", StaticFiles(directory=str(docs_dist_path), html=True), name="portal")
    # Also mount /assets and /images at root level as a bulletproof fallback for static assets
    if (docs_dist_path / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(docs_dist_path / "assets")), name="assets_root")
    if (docs_dist_path / "images").exists():
        app.mount("/images", StaticFiles(directory=str(docs_dist_path / "images")), name="images_root")

@app.get("/portal", include_in_schema=False)
def portal_redirect():
    return RedirectResponse(url="/portal/")


# ----------------- SCHEMAS -----------------

class ShortenRequest(BaseModel):
    url: str
    custom_alias: Optional[str] = None
    ttl_seconds: Optional[int] = None

class AutocompleteInsertRequest(BaseModel):
    query: str
    frequency: int = 1

class ScoreUpdateRequest(BaseModel):
    player_id: str
    score: float

class WalletTransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount_cents: int

class MetricRecordRequest(BaseModel):
    metric_name: str
    value: float
    labels: Optional[Dict[str, str]] = None

class HashRingAddNodeRequest(BaseModel):
    node_id: str

# ----------------- ENDPOINTS -----------------

@app.get("/", response_class=HTMLResponse)
def index_page():
    return HTML_DASHBOARD


# 1. Rate Limiting
@app.get("/api/v1/rate-limiter/check")
def check_rate_limit(client_id: str = "guest"):
    res = token_limiter.allow_request(client_id)
    return {
        "client_id": client_id,
        "allowed": res.allowed,
        "limit": res.limit,
        "remaining_tokens": res.remaining,
        "retry_after_seconds": res.retry_after,
    }


# 2. Consistent Hashing
@app.get("/api/v1/consistent-hashing/ring")
def get_ring_status():
    keys_sample = [f"user_{i}" for i in range(1000)]
    distribution = ConsistentHashSimulator.analyze_distribution(hash_ring, keys_sample)
    return {
        "nodes": hash_ring.nodes,
        "total_virtual_nodes": hash_ring.total_vnodes,
        "simulation_sample": distribution,
    }

@app.post("/api/v1/consistent-hashing/nodes")
def add_hash_node(req: HashRingAddNodeRequest):
    hash_ring.add_node(req.node_id)
    return {"message": f"Node '{req.node_id}' added to ring.", "nodes": hash_ring.nodes}

@app.delete("/api/v1/consistent-hashing/nodes/{node_id}")
def remove_hash_node(node_id: str):
    hash_ring.remove_node(node_id)
    return {"message": f"Node '{node_id}' removed from ring.", "nodes": hash_ring.nodes}

@app.get("/api/v1/consistent-hashing/lookup")
def lookup_key(key: str, replicas: int = 1):
    target = hash_ring.get_node(key)
    all_replicas = hash_ring.get_nodes(key, count=replicas)
    return {"key": key, "primary_node": target, "replicas": all_replicas}


# 3. Snowflake ID Generator
@app.get("/api/v1/unique-id/snowflake")
def generate_snowflake():
    uid = snowflake_gen.generate()
    parts = snowflake_gen.parse(uid)
    return {
        "snowflake_id": str(uid),
        "base62_code": Base62.encode(uid),
        "components": {
            "timestamp_ms": parts.timestamp_ms,
            "utc_datetime": parts.utc_datetime.isoformat(),
            "datacenter_id": parts.datacenter_id,
            "worker_id": parts.worker_id,
            "sequence": parts.sequence,
        },
    }


# 4. URL Shortener
@app.post("/api/v1/url/shorten")
def shorten_url(req: ShortenRequest):
    try:
        entry = url_service.shorten(
            long_url=req.url,
            custom_alias=req.custom_alias,
            ttl_seconds=req.ttl_seconds,
        )
        return {
            "short_code": entry.short_code,
            "short_url": f"http://localhost:8000/s/{entry.short_code}",
            "long_url": entry.long_url,
            "click_count": entry.click_count,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/s/{short_code}")
def redirect_short_url(short_code: str):
    long_url = url_service.resolve(short_code)
    if not long_url:
        raise HTTPException(status_code=404, detail="Short URL not found or expired.")
    return RedirectResponse(url=long_url, status_code=307)

@app.get("/api/v1/url/stats/{short_code}")
def get_url_stats(short_code: str):
    meta = url_service.get_metadata(short_code)
    if not meta:
        raise HTTPException(status_code=404, detail="Short code not found.")
    return meta


# 5. Search Autocomplete
@app.get("/api/v1/autocomplete/search")
def search_autocomplete(prefix: str, limit: int = 5):
    suggestions = autocomplete_service.search(prefix, limit=limit)
    return [{"query": q, "frequency": f} for q, f in suggestions]

@app.post("/api/v1/autocomplete/insert")
def insert_term(req: AutocompleteInsertRequest):
    autocomplete_service.insert(req.query, req.frequency)
    return {"message": f"Inserted '{req.query}' with frequency {req.frequency}"}


# 6. Leaderboard
@app.get("/api/v1/leaderboard/top")
def get_top_players(limit: int = 10):
    return leaderboard_service.get_top_k(limit)

@app.post("/api/v1/leaderboard/score")
def update_player_score(req: ScoreUpdateRequest):
    entry = leaderboard_service.update_score(req.player_id, req.score)
    return entry


# 7. Digital Wallet & Ledger
@app.post("/api/v1/wallet/transfer")
def transfer_money(req: WalletTransferRequest):
    try:
        tx = wallet_service.transfer(req.from_account, req.to_account, req.amount_cents)
        return {
            "transaction_id": tx.tx_id,
            "status": tx.status,
            "from_account": tx.from_account,
            "to_account": tx.to_account,
            "amount_usd": req.amount_cents / 100.0,
            "from_balance_usd": wallet_service.get_balance(req.from_account) / 100.0,
            "to_balance_usd": wallet_service.get_balance(req.to_account) / 100.0,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/wallet/balances")
def get_wallet_balances():
    return {
        "user_alice": wallet_service.get_balance("user_alice") / 100.0,
        "user_bob": wallet_service.get_balance("user_bob") / 100.0,
        "merchant_stripe": wallet_service.get_balance("merchant_stripe") / 100.0,
    }


# 8. Metrics
@app.post("/api/v1/metrics/record")
def record_metric(req: MetricRecordRequest):
    metrics_engine.record_metric(req.metric_name, req.value, req.labels)
    agg = metrics_engine.query_aggregate(req.metric_name)
    alerts = metrics_engine.get_firing_alerts()
    return {
        "status": "recorded",
        "aggregate": agg,
        "firing_alerts": [a.rule_name for a in alerts],
    }

# ----------------- EMBEDDED DASHBOARD -----------------
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>System Design Live Playground</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f2937;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --success: #10b981;
      --danger: #ef4444;
      --warning: #f59e0b;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      padding: 2rem;
      line-height: 1.5;
    }
    header {
      text-align: center;
      margin-bottom: 2.5rem;
    }
    header h1 {
      font-size: 2.4rem;
      font-weight: 800;
      background: linear-gradient(135deg, #60a5fa, #a855f7);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }
    header p {
      color: var(--text-muted);
      font-size: 1.1rem;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.5rem;
      max-width: 1400px;
      margin: 0 auto;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .card h2 {
      font-size: 1.25rem;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #93c5fd;
    }
    .card p.desc {
      font-size: 0.875rem;
      color: var(--text-muted);
      margin-bottom: 1rem;
      min-height: 40px;
    }
    button {
      background: var(--accent);
      color: white;
      border: none;
      padding: 0.6rem 1rem;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.9rem;
      transition: background 0.2s;
    }
    button:hover { background: var(--accent-hover); }
    input {
      background: #1f2937;
      border: 1px solid #374151;
      color: white;
      padding: 0.6rem;
      border-radius: 6px;
      font-family: inherit;
      width: 100%;
      margin-bottom: 0.75rem;
    }
    .output {
      background: #030712;
      border: 1px solid #1f2937;
      border-radius: 6px;
      padding: 0.75rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: #34d399;
      margin-top: auto;
      min-height: 85px;
      overflow-x: auto;
      white-space: pre-wrap;
    }
    .badge {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 700;
    }
    .badge-ok { background: rgba(16, 185, 129, 0.2); color: var(--success); }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
    .links-bar {
      margin-top: 1rem;
      text-align: center;
    }
    .links-bar a {
      color: #60a5fa;
      text-decoration: none;
      margin: 0 1rem;
      font-weight: 500;
    }
    .links-bar a:hover { text-decoration: underline; }
    .translate-bar {
      margin-top: 1.25rem;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }
    #google_translate_element select {
      background: #1f2937;
      color: #f3f4f6;
      border: 1px solid #374151;
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      font-size: 0.9rem;
      cursor: pointer;
      outline: none;
    }
    .goog-te-gadget { color: #9ca3af !important; font-size: 0.8rem !important; }
    .goog-logo-link { display: none !important; }
    .goog-te-gadget > span { display: none !important; }
    .goog-te-banner-frame.skiptranslate { display: none !important; }
  </style>
</head>
<body>

  <header>
    <h1>⚡ डिस्ट्रीब्यूटेड सिस्टम्स लाइव सिम्युलेटर (Distributed Systems Playground)</h1>
    <p>jigsi_karia की System Design Interview (Vol 1 & 2) के लाइव कोड आर्किटेक्चर</p>
    <div class="links-bar">
      <a href="/portal/" target="_blank" style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 0.4rem 0.9rem; border-radius: 6px; font-weight: 600; text-decoration: none;">📖 सम्पूर्ण हिन्दी नोट्स (28 Chapters Portal)</a>
      <a href="http://localhost:5173/" target="_blank" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 0.4rem 0.9rem; border-radius: 6px; font-weight: 600; text-decoration: none;">⚡ VitePress Dev Server (:5173)</a>
      <a href="/docs" target="_blank">&#128214; Interactive Swagger API Docs</a>
      <a href="/redoc" target="_blank">&#128220; ReDoc API Specs</a>
    </div>
    <div class="translate-bar">
      <label for="world-lang-select" style="font-size: 0.95rem; color: #93c5fd; font-weight: 600; display: flex; align-items: center; gap: 0.4rem;">
        🌐 All World Languages (180+ Google Translate):
      </label>
      <select id="world-lang-select" onchange="changeSiteLanguage(this.value)" style="background: #1f2937; color: #f9fafb; border: 1px solid #3b82f6; padding: 0.45rem 0.8rem; border-radius: 6px; font-size: 0.9rem; cursor: pointer; outline: none; font-weight: 500;">
        <option value="original">🌐 मूल भाषा: हिन्दी / Tech-Hinglish (Original)</option>
        <optgroup label="⭐ प्रमुख भाषाएं (Major World Languages)">
          <option value="en">English (अंग्रेज़ी)</option>
          <option value="es">Español (Spanish)</option>
          <option value="fr">Français (French)</option>
          <option value="de">Deutsch (German)</option>
          <option value="ar">العربية (Arabic)</option>
          <option value="ru">Русский (Russian)</option>
          <option value="zh-CN">中文 简体 (Chinese Simplified)</option>
          <option value="zh-TW">中文 繁體 (Chinese Traditional)</option>
          <option value="ja">日本語 (Japanese)</option>
          <option value="ko">한국어 (Korean)</option>
          <option value="pt">Português (Portuguese)</option>
          <option value="it">Italiano (Italian)</option>
          <option value="nl">Nederlands (Dutch)</option>
          <option value="tr">Türkçe (Turkish)</option>
          <option value="pl">Polski (Polish)</option>
          <option value="uk">Українська (Ukrainian)</option>
          <option value="vi">Tiếng Việt (Vietnamese)</option>
          <option value="id">Bahasa Indonesia</option>
          <option value="ms">Bahasa Melayu</option>
          <option value="th">ไทย (Thai)</option>
        </optgroup>
        <optgroup label="🇮🇳 भारतीय भाषाएं (Indian Regional Languages)">
          <option value="hi">हिन्दी (Hindi)</option>
          <option value="bn">বাংলা (Bengali)</option>
          <option value="mr">मराठी (Marathi)</option>
          <option value="te">తెలుగు (Telugu)</option>
          <option value="ta">தமிழ் (Tamil)</option>
          <option value="gu">ગુજરાતી (Gujarati)</option>
          <option value="ur">اردو (Urdu)</option>
          <option value="kn">ಕನ್ನಡ (Kannada)</option>
          <option value="ml">മലയാളം (Malayalam)</option>
          <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
          <option value="or">ଓଡ଼ିଆ (Odia)</option>
          <option value="as">অসমীয়া (Assamese)</option>
          <option value="ne">नेपाली (Nepali)</option>
          <option value="bho">भोजपुरी (Bhojpuri)</option>
          <option value="mai">मैथिली (Maithili)</option>
          <option value="sa">संस्कृतम् (Sanskrit)</option>
          <option value="gom">कोंकणी (Konkani)</option>
          <option value="doi">डोगरी (Dogri)</option>
          <option value="si">සිංහල (Sinhala)</option>
          <option value="my">မြန်မာ (Burmese)</option>
        </optgroup>
        <optgroup label="🌍 यूरोपीय एवं अन्य भाषाएं (European & Global Languages)">
          <option value="af">Afrikaans</option>
          <option value="sq">Shqip (Albanian)</option>
          <option value="am">አማርኛ (Amharic)</option>
          <option value="hy">Հայերեն (Armenian)</option>
          <option value="az">Azərbaycan (Azerbaijani)</option>
          <option value="eu">Euskara (Basque)</option>
          <option value="be">Беларуская (Belarusian)</option>
          <option value="bs">Bosanski (Bosnian)</option>
          <option value="bg">Български (Bulgarian)</option>
          <option value="ca">Català (Catalan)</option>
          <option value="ceb">Cebuano</option>
          <option value="ny">Chichewa</option>
          <option value="co">Corsu (Corsican)</option>
          <option value="hr">Hrvatski (Croatian)</option>
          <option value="cs">Čeština (Czech)</option>
          <option value="da">Dansk (Danish)</option>
          <option value="eo">Esperanto</option>
          <option value="et">Eesti (Estonian)</option>
          <option value="tl">Filipino (Tagalog)</option>
          <option value="fi">Suomi (Finnish)</option>
          <option value="fy">Frysk (Frisian)</option>
          <option value="gl">Galego (Galician)</option>
          <option value="ka">ქართული (Georgian)</option>
          <option value="el">Ελληνικά (Greek)</option>
          <option value="ht">Kreyòl Ayisyen (Haitian Creole)</option>
          <option value="ha">Hausa</option>
          <option value="haw">ʻŌlelo Hawaiʻi (Hawaiian)</option>
          <option value="he">עברית (Hebrew)</option>
          <option value="hmn">Hmong</option>
          <option value="hu">Magyar (Hungarian)</option>
          <option value="is">Íslenska (Icelandic)</option>
          <option value="ig">Igbo</option>
          <option value="ilo">Ilokano</option>
          <option value="ga">Gaeilge (Irish)</option>
          <option value="jw">Basa Jawa (Javanese)</option>
          <option value="kk">Қазақ (Kazakh)</option>
          <option value="km">ខ្មែរ (Khmer)</option>
          <option value="rw">Kinyarwanda</option>
          <option value="ku">Kurdî (Kurdish)</option>
          <option value="ky">Кыргызча (Kyrgyz)</option>
          <option value="lo">ພາສາລາວ (Lao)</option>
          <option value="la">Latina (Latin)</option>
          <option value="lv">Latviešu (Latvian)</option>
          <option value="lt">Lietuvių (Lithuanian)</option>
          <option value="lb">Lëtzebuergesch (Luxembourgish)</option>
          <option value="mk">Македонски (Macedonian)</option>
          <option value="mg">Malagasy</option>
          <option value="mt">Malti (Maltese)</option>
          <option value="mi">Māori</option>
          <option value="mn">Монгол (Mongolian)</option>
          <option value="no">Norsk (Norwegian)</option>
          <option value="ps">پښتو (Pashto)</option>
          <option value="fa">فارسی (Persian)</option>
          <option value="ro">Română (Romanian)</option>
          <option value="sm">Gagana Samoa (Samoan)</option>
          <option value="gd">Gàidhlig (Scots Gaelic)</option>
          <option value="sr">Српски (Serbian)</option>
          <option value="st">Sesotho</option>
          <option value="sn">Shona</option>
          <option value="sd">سنڌي (Sindhi)</option>
          <option value="sk">Slovenčina (Slovak)</option>
          <option value="sl">Slovenščina (Slovenian)</option>
          <option value="so">Soomaali (Somali)</option>
          <option value="su">Basa Sunda (Sundanese)</option>
          <option value="sw">Kiswahili (Swahili)</option>
          <option value="sv">Svenska (Swedish)</option>
          <option value="tg">Тоҷикӣ (Tajik)</option>
          <option value="tt">Татар (Tatar)</option>
          <option value="tk">Türkmen (Turkmen)</option>
          <option value="ug">ئۇيغۇرچە (Uyghur)</option>
          <option value="uz">Oʻzbek (Uzbek)</option>
          <option value="cy">Cymraeg (Welsh)</option>
          <option value="xh">isiXhosa (Xhosa)</option>
          <option value="yi">ייִדיש (Yiddish)</option>
          <option value="yo">Yorùbá</option>
          <option value="zu">isiZulu (Zulu)</option>
        </optgroup>
      </select>
      <div id="google_translate_element" style="display:inline-block;"></div>
    </div>
  </header>

  <div class="grid">
    <!-- Chapter 4: Rate Limiter -->
    <div class="card">
      <h2>&#9201; Ch 04: Rate Limiter (दर नियंत्रक)</h2>
      <p class="desc">Token Bucket एल्गोरिदम (Capacity: 10 tokens, Refill: 2 tokens/sec)। अत्यधिक और तीव्र क्लिक करने पर HTTP 429 थ्रॉटलिंग सक्रिय होगी।</p>
      <button onclick="testRateLimiter()">🚀 Rapid Request भेजें</button>
      <div id="rate-out" class="output">Ready...</div>
    </div>

    <!-- Chapter 5: Consistent Hashing -->
    <div class="card">
      <h2>&#9774; Ch 05: Consistent Hashing (कंसिस्टेंट हैशिंग)</h2>
      <p class="desc">Virtual Nodes के साथ 2^32 हैश रिंग पर Keys को सर्वर्स पर मैप करें (न्यूनतम डेटा माइग्रेशन और कैश चर्न)।</p>
      <input id="hash-key" placeholder="Enter key (e.g. user_999)" value="user_999">
      <button onclick="lookupHash()">🔍 Responsible Node खोजें</button>
      <div id="hash-out" class="output">Ready...</div>
    </div>

    <!-- Chapter 7: Snowflake Generator -->
    <div class="card">
      <h2>&#10052; Ch 07: Snowflake ID Generator (यूनिक आईडी)</h2>
      <p class="desc">Twitter Snowflake 64-bit समय-क्रम में व्यवस्थित (monotonically ordered) ID जनरेटर (Timestamp, Datacenter, Worker, Sequence)।</p>
      <button onclick="generateSnowflake()">⚡ 64-bit ID जनरेट करें</button>
      <div id="snowflake-out" class="output">Ready...</div>
    </div>

    <!-- Chapter 8: URL Shortener -->
    <div class="card">
      <h2>&#128279; Ch 08: URL Shortener (शॉर्ट यूआरएल)</h2>
      <p class="desc">100k+ req/sec के लिए Base62 एन्कोडिंग + Bloom Filter प्री-चेक + LRU Cache रीडायरेक्ट्स।</p>
      <input id="long-url" placeholder="Long URL दर्ज करें" value="https://bytebytego.com/courses/system-design-interview">
      <button onclick="shortenUrl()">✂️ Short URL बनाएं</button>
      <div id="url-out" class="output">Ready...</div>
    </div>

    <!-- Chapter 13: Search Autocomplete -->
    <div class="card">
      <h2>&#128269; Ch 13: Search Autocomplete (सर्च ऑटो-कम्प्लीट)</h2>
      <p class="desc">O(1) लुकअप के लिए Prefix Trie और Top-5 प्री-कैश्ड फ्रीक्वेंसी (जैसे: sys, red, snow टाइप करें)।</p>
      <input id="search-prefix" placeholder="टाइप करके खोजें (e.g. sys, red, snow)..." oninput="autocompleteSearch(this.value)">
      <div id="auto-out" class="output">Type something...</div>
    </div>

    <!-- Chapter 25: Real-Time Leaderboard -->
    <div class="card">
      <h2>&#127942; Ch 25: Gaming Leaderboard (गेमिंग लीडरबोर्ड)</h2>
      <p class="desc">O(log N) अपडेट्स और रैंक क्वेरीज़ के लिए इन-मेमोरी SkipList + Hash Table (Redis ZSET आर्किटेक्चर)।</p>
      <button onclick="fetchLeaderboard()">🥇 Top 5 पोडियम देखें</button>
      <div id="leader-out" class="output">Click to load...</div>
    </div>

    <!-- Chapter 27: Digital Wallet -->
    <div class="card">
      <h2>&#128179; Ch 27: Digital Wallet (डिजिटल वॉलेट ACID)</h2>
      <p class="desc">बैलेंस इनवेरिएंट और ऑर्डर्ड लॉकिंग के साथ डेडलॉक-फ्री फंड ट्रांसफर।</p>
      <button onclick="transferWallet()">💸 $10 ट्रांसफर करें (Alice -> Bob)</button>
      <div id="wallet-out" class="output">Ready...</div>
    </div>

    <!-- Chapter 20: Metrics Monitoring -->
    <div class="card">
      <h2>&#128200; Ch 20: Metrics & Alerting (सिस्टम मॉनिटरिंग)</h2>
      <p class="desc">Prometheus-स्टाइल टाइम-सीरीज़ इंजन और डायनामिक अलर्टिंग रूल्स (यदि CPU > 85% तो अलर्ट ट्रिगर होगा)।</p>
      <input id="cpu-val" type="number" placeholder="CPU % दर्ज करें (e.g. 92)" value="92">
      <button onclick="recordMetric()">📊 Metric रिकॉर्ड करें</button>
      <div id="metric-out" class="output">Ready...</div>
    </div>
  </div>

  <script>
    function setGoogleTransCookie(lang) {
      if (!lang || lang === 'original') {
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax;";
        if (location.hostname && location.hostname.indexOf('.') !== -1) {
          document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=" + location.hostname + "; SameSite=Lax;";
          document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=." + location.hostname + "; SameSite=Lax;";
        }
      } else {
        document.cookie = "googtrans=/auto/" + lang + "; path=/; SameSite=Lax;";
        document.cookie = "googtrans=/hi/" + lang + "; path=/; SameSite=Lax;";
        if (location.hostname && location.hostname.indexOf('.') !== -1) {
          document.cookie = "googtrans=/auto/" + lang + "; path=/; domain=" + location.hostname + "; SameSite=Lax;";
          document.cookie = "googtrans=/hi/" + lang + "; path=/; domain=" + location.hostname + "; SameSite=Lax;";
          document.cookie = "googtrans=/auto/" + lang + "; path=/; domain=." + location.hostname + "; SameSite=Lax;";
          document.cookie = "googtrans=/hi/" + lang + "; path=/; domain=." + location.hostname + "; SameSite=Lax;";
        }
      }
    }

    function changeSiteLanguage(targetLang) {
      setGoogleTransCookie(targetLang);

      if (!targetLang || targetLang === 'original') {
        var combo = document.querySelector('.goog-te-combo');
        if (combo) {
          combo.value = '';
          combo.dispatchEvent(new Event('change'));
        }
        setTimeout(function() {
          window.location.reload();
        }, 150);
        return;
      }

      function triggerCombo() {
        var combo = document.querySelector('.goog-te-combo');
        if (combo) {
          combo.value = targetLang;
          combo.dispatchEvent(new Event('change'));
          return true;
        }
        return false;
      }

      if (!triggerCombo()) {
        var attempts = 0;
        var timer = setInterval(function() {
          attempts++;
          if (triggerCombo() || attempts >= 15) {
            clearInterval(timer);
          }
        }, 200);
      }
    }

    // Sync changes from native Google dropdown back to our 180+ dropdown
    document.addEventListener('change', function(e) {
      if (e.target && e.target.classList.contains('goog-te-combo')) {
        var val = e.target.value;
        var sel = document.getElementById('world-lang-select');
        if (sel && val) {
          sel.value = val;
        }
        setGoogleTransCookie(val || 'original');
      }
    });

    window.addEventListener('DOMContentLoaded', function() {
      var match = document.cookie.match(/(?:^|;\s*)googtrans=([^;]+)/);
      if (match) {
        var parts = match[1].split('/');
        var currentLang = parts[parts.length - 1];
        var sel = document.getElementById('world-lang-select');
        if (sel && currentLang) {
          sel.value = currentLang;
        }
      }
    });

    async function testRateLimiter() {
      const res = await fetch('/api/v1/rate-limiter/check?client_id=demo_user');
      const data = await res.json();
      const statusBadge = data.allowed ? '<span class="badge badge-ok">ALLOWED</span>' : '<span class="badge badge-danger">429 THROTTLED</span>';
      document.getElementById('rate-out').innerHTML =
        `${statusBadge} Remaining Tokens: ${data.remaining_tokens}/${data.limit}\\n` +
        (data.retry_after_seconds ? `Retry after: ${data.retry_after_seconds}s` : 'OK');
    }

    async function lookupHash() {
      const k = document.getElementById('hash-key').value;
      const res = await fetch(`/api/v1/consistent-hashing/lookup?key=${encodeURIComponent(k)}&replicas=3`);
      const data = await res.json();
      document.getElementById('hash-out').innerText = JSON.stringify(data, null, 2);
    }

    async function generateSnowflake() {
      const res = await fetch('/api/v1/unique-id/snowflake');
      const data = await res.json();
      document.getElementById('snowflake-out').innerText =
        `ID: ${data.snowflake_id} (Base62: ${data.base62_code})\\n` +
        `Time: ${data.components.utc_datetime}\\n` +
        `DC: ${data.components.datacenter_id} | Worker: ${data.components.worker_id} | Seq: ${data.components.sequence}`;
    }

    async function shortenUrl() {
      const url = document.getElementById('long-url').value;
      const res = await fetch('/api/v1/url/shorten', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
      });
      const data = await res.json();
      document.getElementById('url-out').innerText =
        `Short Code: ${data.short_code}\\n` +
        `Short URL: ${data.short_url}\\n` +
        `Redirects to: ${data.long_url}`;
    }

    async function autocompleteSearch(val) {
      if (!val) {
        document.getElementById('auto-out').innerText = 'टाइप करके खोजें...';
        return;
      }
      const res = await fetch(`/api/v1/autocomplete/search?prefix=${encodeURIComponent(val)}`);
      const data = await res.json();
      if (data.length === 0) {
        document.getElementById('auto-out').innerText = 'कोई परिणाम नहीं मिला।';
      } else {
        document.getElementById('auto-out').innerText =
          data.map(item => `[${item.frequency}] ${item.query}`).join('\\n');
      }
    }

    async function fetchLeaderboard() {
      const res = await fetch('/api/v1/leaderboard/top?limit=5');
      const data = await res.json();
      document.getElementById('leader-out').innerText =
        data.map(e => `#${e.rank} ${e.player_id.padEnd(10)} Score: ${e.score}`).join('\\n');
    }

    async function transferWallet() {
      const res = await fetch('/api/v1/wallet/transfer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          from_account: 'user_alice',
          to_account: 'user_bob',
          amount_cents: 1000
        })
      });
      const data = await res.json();
      document.getElementById('wallet-out').innerText =
        `Tx: ${data.transaction_id} [${data.status}]\\n` +
        `Alice Balance: $${data.from_balance_usd}\\n` +
        `Bob Balance:   $${data.to_balance_usd}`;
    }

    async function recordMetric() {
      const val = parseFloat(document.getElementById('cpu-val').value);
      const res = await fetch('/api/v1/metrics/record', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({metric_name: 'cpu_usage', value: val})
      });
      const data = await res.json();
      document.getElementById('metric-out').innerText =
        `Recorded: ${val}%\\n` +
        `Rolling 60s Avg: ${data.aggregate.avg}%\\n` +
        `Alerts Firing: ${data.firing_alerts.length ? data.firing_alerts.join(', ') : 'None (OK)'}`;
    }
  </script>
  <script type="text/javascript">
    function googleTranslateElementInit() {
      new google.translate.TranslateElement({
        pageLanguage: 'auto',
        autoDisplay: false
      }, 'google_translate_element');
    }
  </script>
  <script type="text/javascript" src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
</body>
</html>
"""

