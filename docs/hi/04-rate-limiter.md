# Chapter 4: Rate Limiter Design करना (Rate Limiter System Design)

## Introduction (भूमिका)
इस चैप्टर में हम एक **Rate Limiter** का आर्किटेक्चर और डिज़ाइन समझेंगे। Rate Limiter नेटवर्क और डिस्ट्रीब्यूटेड सिस्टम्स का एक बेहद महत्वपूर्ण कंपोनेंट है, जिसका काम क्लाइंट (Client) या सर्विस द्वारा भेजे जाने वाले नेटवर्क ट्रैफिक की दर (Request Rate) को नियंत्रित करना होता है। 

अगर कोई यूजर या बॉट तय सीमा से ज्यादा रिक्वेस्ट भेजता है, तो Rate Limiter अतिरिक्त कॉल्स को ब्लॉक कर देता है और **HTTP 429 (Too Many Requests)** स्टेटस कोड लौटाता है।

### Rate Limiting के मुख्य फायदे
- **DoS / DDoS Attacks से बचाव:** अतिरिक्त और दुर्भावनापूर्ण (malicious) कॉल्स को रोककर सर्वर के CPU और Memory को सुरक्षित रखना।
- **Cost Reduction (लागत में कमी):** थर्ड-पार्टी APIs (जैसे Twilio, OpenAI, Stripe) की अनपेक्षित कॉल्स को सीमित करके बिलिंग को बजट में रखना।
- **Preventing Server Overload:** सर्वर को उसकी क्षमता से अधिक लोड आने पर क्रैश होने से बचाना और हाई ट्रैफिक के दौरान भी सिस्टम की स्टेबिलिटी बनाए रखना।

---

## Step 1: Requirements और Scope समझना (Problem Understanding)

### Functional Requirements
- सर्वर-साइड (Server-side) API Rate Limiter तैयार करना।
- विभिन्न प्रकार के थ्रॉटलिंग नियमों (Throttling Rules) का समर्थन करना (जैसे: प्रति सेकंड Requests, प्रति मिनट IP लिमिट, प्रति यूजर लॉगिन लिमिट)।
- बड़े पैमाने पर डिस्ट्रीब्यूटेड सिस्टम (Large-scale Distributed Environment) में काम करना।
- जब रिक्वेस्ट थ्रॉटल हो, तो क्लाइंट को स्पष्ट एरर मैसेज और `Retry-After` हेडर लौटाना।

### Non-Functional Requirements
- **Low Latency:** Rate Limiter चेक में 1-2 मिलीसेकंड से भी कम समय लगना चाहिए ताकि यूज़र एक्सपीरियंस प्रभावित न हो।
- **Accurate Throttling:** रिक्वेस्ट की गिनती सटीक होनी चाहिए।
- **Low Memory Usage:** करोड़ों एक्टिव यूज़र्स के लिए मेमोरी की खपत बहुत कम होनी चाहिए।
- **High Fault Tolerance:** अगर Rate Limiter सर्विस में कोई गड़बड़ी (Outage) आ जाए, तो पूरी मुख्य एप्लिकेशन ठप नहीं होनी चाहिए (Graceful Degradation)।

---

## Step 2: High-Level Design (Rate Limiter कहाँ रखें?)

<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/rate_limiter_architecture.png" alt="Rate Limiting Middleware Architecture" width="550">
</div>

### 1. Client-Side Implementation (क्लाइंट-साइड)
- **विश्वसनीय नहीं है:** क्लाइंट-साइड कोड (जैसे मोबाइल ऐप या जावास्क्रिप्ट) को हैकर्स आसानी से बायपास कर सकते हैं या रिवर्स-इंजीनियर कर सकते हैं। इसलिए इसे प्रोडक्शन सिस्टम में अनुशंसित नहीं किया जाता।

### 2. Server-Side Implementation (सर्वर-साइड)
- बिज़नेस लॉजिक कोड के अंदर ही रेट लिमिटिंग लागू करना। यह फुल कंट्रोल देता है, लेकिन मॉड्यूलरिटी कम कर देता है।

### 3. Middleware / API Gateway (सबसे पसंदीदा विकल्प)
- आज के मॉडर्न Microservices आर्किटेक्चर में Rate Limiter को **API Gateway** (जैसे Kong, Envoy, AWS API Gateway) के मिडलवेयर के रूप में तैनात किया जाता है।
- क्लाइंट की रिक्वेस्ट सबसे पहले API Gateway पर आती है, जहाँ Rate Limiter चेक करता है:
  - यदि सीमा के अंदर है: रिक्वेस्ट मुख्य बैकएंड माइक्रो-सर्विसेज को फॉरवर्ड कर दी जाती है।
  - यदि सीमा पार हो चुकी है: तुरंत **HTTP 429 Too Many Requests** रिस्पॉन्स वापस भेज दिया जाता है।

---

## Step 3: Top Rate Limiting Algorithms (मुख्य एल्गोरिदम)

### 1. Token Bucket Algorithm (टोकन बकेट)
<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/token-bucket.png" alt="Token Bucket Algorithm" width="550">
</div>

- **कार्यप्रणाली (How it works):**
  - एक बकेट (Bucket) होती है जिसकी निश्चित क्षमता (Capacity $b$) होती है।
  - एक स्थिर दर (Refill Rate $r$) से प्रति सेकंड बकेट में नए टोकन गिरते रहते हैं। यदि बकेट पूरी भर जाए, तो अतिरिक्त टोकन डिस्कार्ड हो जाते हैं।
  - जब भी कोई नई रिक्वेस्ट आती है, तो बकेट से 1 टोकन लिया जाता है और रिक्वेस्ट आगे बढ़ जाती है।
  - यदि बकेट खाली है (0 टोकन), तो रिक्वेस्ट ड्रॉप (Drop) कर दी जाती है।
- **Pros (फायदे):** लागू करना आसान, कम मेमोरी की आवश्यकता, और अचानक आने वाले छोटे ट्रैफिक बर्स्ट (Traffic Bursts) को भी बिना रिजेक्ट किए संभाल लेता है।
- **Cons (कमियां):** बकेट साइज और रिफिल रेट के 2 पैरामीटर्स को सही ढंग से ट्यून करना पड़ता है।
- *इंटरनेट पर सबसे लोकप्रिय:* Amazon AWS और Stripe इसी एल्गोरिदम का मुख्य रूप से उपयोग करते हैं।

---

### 2. Leaking Bucket Algorithm (लीकिंग बकेट)
<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/leaking-bucket.png" alt="Leaking Bucket Algorithm" width="550">
</div>

- **कार्यप्रणाली (How it works):**
  - एक FIFO (First-In-First-Out) कतार (Queue) होती है। रिक्वेस्ट कतार में जुड़ती जाती हैं।
  - कतार के नीचे से एक निश्चित और स्थिर आउटफ्लो रेट (Constant Outflow Rate) पर रिक्वेस्ट प्रोसेस होती हैं।
  - यदि कतार पूरी भर जाए, तो नई रिक्वेस्ट ओवरफ्लो होकर ड्रॉप हो जाती हैं।
- **Pros:** आउटफ्लो ट्रैफिक हमेशा स्मूथ और स्थिर (Smooth & Stable) रहता है।
- **Cons:** यदि ट्रैफिक का अचानक बर्स्ट (Burst) आए, तो हाल की ताज़ा रिक्वेस्ट कतार में पुरानी रिक्वेस्ट्स की वजह से ब्लॉक या डिले हो सकती हैं।

---

### 3. Fixed Window Counter Algorithm (फिक्स्ड विंडो काउंटर)
<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/fixed-window-counter.png" alt="Fixed Window Counter" width="550">
</div>

- **कार्यप्रणाली:** समय को निश्चित टाइम विंडो (जैसे 1:00-1:01, 1:01-1:02) में बांट दिया जाता है। हर विंडो में एक काउंटर होता है। यदि काउंटर सीमा पार कर जाए, तो विंडो समाप्त होने तक रिक्वेस्ट रिजेक्ट होती हैं।
- **गंभीर समस्या (Window Boundary Spike Issue):** 
<img src="/images/04-rate-limiter/fixed-window-issue.png" alt="Fixed Window Issue" width="550">
  - यदि विंडो के बिल्कुल आखिर (1:00:50) में 1 मिनट का कोटा आ जाए और अगली विंडो के शुरुआती सेकेंड (1:01:10) में फिर से कोटा आ जाए, तो 20 सेकंड के छोटे से अंतराल में अनुमत सीमा से दोगुना (2x) ट्रैफिक सर्वर पर आ जाएगा, जिससे सर्वर क्रैश हो सकता है!

---

### 4. Sliding Window Log Algorithm (स्लाइडिंग विंडो लॉग)
<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/sliding-window-log.png" alt="Sliding Window Log" width="550">
</div>

- **कार्यप्रणाली:** हर रिक्वेस्ट का सटीक टाइमस्टैम्प (Timestamp) इन-मेमोरी स्टोर (जैसे Redis Sorted Set) में सेव किया जाता है। जब नई रिक्वेस्ट आती है, तो `Current Time - Window Size` से पुराने सभी टाइमस्टैम्प हटा दिए जाते हैं और बचे हुए लॉग्स की संख्या से निर्णय लिया जाता है।
- **Pros:** 100% सटीक रेट लिमिटिंग, विंडो बाउंड्री की कोई समस्या नहीं।
- **Cons:** भारी मेमोरी की खपत (High Memory Footprint), क्योंकि रिजेक्ट हुई रिक्वेस्ट्स का भी टाइमस्टैम्प स्टोर करना पड़ता है।

---

### 5. Sliding Window Counter Algorithm (स्लाइडिंग विंडो काउंटर - हाइब्रिड)
<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/sliding-window-counter.png" alt="Fixed Window Counter" width="550">
</div>

- **कार्यप्रणाली:** यह फिक्स्ड विंडो और स्लाइडिंग लॉग दोनों का बेहतरीन मिश्रण है।
  $$\text{Requests in Window} = \text{Current Window Requests} + (\text{Previous Window Requests} \times \text{Overlap Percentage})$$
- **Pros:** बहुत कम मेमोरी खपत और ट्रैफिक बर्स्ट को स्मूथ करता है। Cloudflare अपने सिस्टम में इसे व्यापक रूप से उपयोग करता है।

---

## High-Level Architecture (डिस्ट्रीब्यूटेड आर्किटेक्चर)

<div style="margin-left:2rem">
<img src="/images/04-rate-limiter/architecture.png" style="margin-left: 40px; margin-top: 40px; margin-bottom: 20px;" alt="Architecture" width="550">
</div>

### डेटाबेस का चुनाव: In-Memory Cache (Redis)
डिस्क आधारित रिलेशनल डेटाबेस (जैसे MySQL) का उपयोग रेट लिमिटिंग के लिए नहीं किया जा सकता, क्योंकि डिस्क I/O बहुत धीमा होता है। इसके लिए **Redis** का उपयोग किया जाता है:
- **Redis In-Memory Speed:** मेमोरी में रीडिंग और राइटिंग सब-मिलीसेकंड में होती है।
- **TTL (Time-To-Live):** कुंजियों (Keys) पर ऑटो-एक्सपायर सेट किया जा सकता है।
- **Atomic Operations:** `INCR` और `EXPIRE` ऑपरेशन्स परमाणु (Atomic) होते हैं।

---

## डिस्ट्रीब्यूटेड वातावरण की चुनौतियाँ (Distributed Challenges)

### 1. Race Conditions (रेस कंडीशंस)
जब दो अलग-अलग वेब सर्वर एक ही यूजर की रिक्वेस्ट एक ही मिलीसेकंड में प्रोसेस करते हैं, तो दोनों Redis से पुराना काउंटर पढ़ सकते हैं और गलत तरीके से रिक्वेस्ट को अनुमति दे सकते हैं।
- **समाधान:** **Redis Lua Scripts** का उपयोग करें। लुआ स्क्रिप्ट Redis इंजन के सिंगल-थ्रेड में एक साथ (Atomics) रन होती है, जिससे रेस कंडीशन पूरी तरह खत्म हो जाती है।

### 2. Synchronization (सिंक्रोनाइज़ेशन)
यदि कई अलग-अलग Rate Limiter सर्वर्स हैं, तो उन्हें एक सेंट्रलाइज्ड Redis क्लस्टर शेयर करना चाहिए, या Sticky Sessions / Consistent Hashing के जरिए एक यूजर की रिक्वेस्ट उसी रेट लिमिटर नोड पर रूट करनी चाहिए।

---

## इंटरव्यू के लिए मुख्य टेकअवे (Interview Summary)
1. **एल्गोरिदम चयन:** ज्यादातर जनरल-पर्पज APIs के लिए **Token Bucket** या **Sliding Window Counter** सबसे बेस्ट हैं।
2. **लोकेशन:** माइक्रो-सर्विसेज में Rate Limiting को हमेशा **API Gateway** पर रखें।
3. **HTTP हेडर मानक:**
   - `X-Ratelimit-Remaining`: बची हुई अनुमत रिक्वेस्ट्स।
   - `X-Ratelimit-Limit`: कुल कोटा।
   - `X-Ratelimit-Retry-After`: कितने सेकंड बाद दोबारा रिक्वेस्ट भेज सकते हैं।
