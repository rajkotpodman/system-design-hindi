# Chapter 8: URL Shortener Design करना (जैसे TinyURL / Bitly)

## Introduction (भूमिका)
इस चैप्टर में हम एक अत्यधिक स्केलेबल **URL Shortening Service** (जैसे TinyURL या Bitly) का सिस्टम डिज़ाइन समझेंगे। 

किसी भी लंबे URL (जैसे `https://example.com/products/item?id=98726&ref=campaign_summer_2026`) को एक छोटे, याद रखने योग्य URL (जैसे `https://tiny.url/zn9edcu`) में बदलना और जब यूज़र उस छोटे लिंक पर क्लिक करे तो तुरंत असली लंबे URL पर रीडायरेक्ट करना इसका मुख्य काम होता है।

### सिस्टम की जरूरतें (Requirements & Estimates)
- **High Availability & Low Latency:** लिंक पर क्लिक करते ही रीडायरेक्शन मिलीसेकंड्स में होना चाहिए।
- **Traffic Estimates:** 
  - प्रतिदिन **100 Million URLs** जनरेट होते हैं।
  - Read-to-Write Ratio: **10:1** (यानी हर 1 यूआरएल बनने पर 10 बार क्लिक किया जाता है)।
  - 10 वर्षों में लगभग **365 Billion URLs** स्टोर करने होंगे (~365 TB स्टोरेज)।

---

## Step 1: High-Level API Design

### 1. URL Shorten Endpoint
```http
POST /api/v1/url/shorten
Content-Type: application/json

{
  "long_url": "https://example.com/very/long/path/name"
}
```
**Response:**
```json
{
  "short_code": "zn9edcu",
  "short_url": "https://tiny.url/zn9edcu",
  "long_url": "https://example.com/very/long/path/name"
}
```

### 2. URL Redirection Endpoint
```http
GET /{short_code}
```
**Response:** HTTP 301 / 302 Redirect to `long_url`.

<p align="center">
<img src="/images/08-url-shortener/url-redirection.png" alt="URL Redirection" width="600">
</p>

### 301 Redirect vs 302 Redirect (इंटरव्यू का सबसे पसंदीदा सवाल)
- **HTTP 301 (Moved Permanently):** 
  - इसका मतलब है कि यह यूआरएल हमेशा के लिए नए पते पर चला गया है। 
  - **ब्राउज़र कैशिंग:** ब्राउज़र इस मैपिंग को अपनी लोकल मेमोरी में हमेशा के लिए कैश कर लेता है। अगली बार यूज़र जब भी क्लिक करेगा, तो रिक्वेस्ट हमारे TinyURL सर्वर पर नहीं जाएगी, बल्कि सीधे ब्राउज़र से ओरिजिनल लिंक खुलेगा।
  - *फायदा:* सर्वर पर लोड न्यूनतम रहता है।
- **HTTP 302 (Found / Temporary Redirect):**
  - ब्राउज़र इसे कैश नहीं करता। हर एक क्लिक की रिक्वेस्ट पहले हमारे सर्वर पर आएगी और फिर वहां से रीडायरेक्ट होगी।
  - *फायदा:* यदि आपको **Click Analytics, Tracking, और Referrer Logs** ट्रैक करने हैं, तो 302 रीडायरेक्ट का उपयोग किया जाता है।

---

## Step 2: Shortening एल्गोरिदम (Base62 vs Hash)

<p align="center">
<img src="/images/08-url-shortener/url-shortening.png" alt="URL Shortening" width="400">
</p>

लंबे URL से 7 कैरेक्टर का शॉर्ट कोड बनाने के 2 मुख्य तरीके हैं:

### 1. Base 62 Encoding (सर्वश्रेष्ठ और सुरक्षित तरीका)
- कैरेक्टर सेट में कुल **62 कैरेक्टर्स** होते हैं:
  - `0-9` (10 अंक)
  - `a-z` (26 छोटे अक्षर)
  - `A-Z` (26 बड़े अक्षर)
- यदि हम 7 कैरेक्टर्स की स्ट्रिंग लें, तो कुल यूनीक कॉम्बिनेशन्स:
  $$62^7 = 3,521,614,606,208 \approx 3.5 \text{ Trillion URLs}$$
  यह 365 बिलियन की जरूरत से 10 गुना ज्यादा है!
- **कार्यप्रणाली:**
  1. जब कोई नया URL आता है, तो हम डिस्ट्रीब्यूटेड ID Generator (जैसे Snowflake ID) से एक यूनीक 64-bit पूर्णांक ID लेते हैं।
  2. उस ID को Base 10 से **Base 62** में बदल देते हैं।
  3. उदाहरण: ID `2009215674938` $\to$ Base62 में `zn9edcu` बन जाता है।
  - *सबसे बड़ा फायदा:* **Zero Hash Collisions** (कोई टकराव नहीं होता, क्योंकि हर ID पहले से ही यूनीक होती है)।

---

### 2. Hash + Collision Resolution (MD5 / SHA-1 + Base62)
- लंबे URL का MD5 हैश निकाला जाता है, और पहले 7 कैरेक्टर्स लिए जाते हैं।
- **समस्या:** दो अलग-अलग लंबे URLs का 7-कैरेक्टर हैश समान हो सकता है (Hash Collision)।
- टकराव सुलझाने के लिए डेटाबेस में चेक करना पड़ता है, और टकराव होने पर एक प्रीफिक्स जोड़कर दोबारा हैश करना पड़ता है। यह बहुत धीमा हो सकता है।

---

## Step 3: Data Model और Caching Architecture

### Relational / NoSQL Data Schema
चूंकि `<short_code, long_url>` मैपिंग में कोई जटिल रिलेशंस नहीं होते, इसलिए इसे Relational DB (MySQL) या Key-Value NoSQL Store (DynamoDB / Cassandra) दोनों में बहुत तेजी से स्टोर किया जा सकता है:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | Primary Key (Snowflake ID) |
| `short_code` | VARCHAR(7) | Unique Index (Base62) |
| `long_url` | VARCHAR(2048) | मूल लंबा यूआरएल |
| `created_at` | TIMESTAMP | रिकॉर्ड बनने का समय |

### Read Heavy System में Caching (Redis)
चूंकि Read vs Write अनुपात 10:1 है, इसलिए 80-20 नियम (Pareto Principle) के अनुसार 20% टॉप URLs 80% रीड ट्रैफिक लाते हैं:
- सभी टॉप URLs को **Redis Cache** में रखा जाता है।
- **Cache Eviction Policy:** मेमोरी पूरी भरने पर **LRU (Least Recently Used)** पॉलिसी से पुराने लिंक्स हटाए जाते हैं।

<p align="center">
<img src="/images/08-url-shortener/url-lookup.png" alt="URL Lookup" width="500">
</p>
