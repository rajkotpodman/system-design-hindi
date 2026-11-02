# Chapter 21: Ad Click Event Aggregation (Facebook / Google Scale)

## Introduction (भूमिका)
डिजिटल विज्ञापन उद्योग (Google Ads, Meta/Facebook Ads, TikTok) की रीढ़ **Ad Click Aggregation Engine** पर टिकी होती है। 

जब भी कोई यूज़र किसी विज्ञापन पर क्लिक करता है, तो उस क्लिक को रिकॉर्ड करना, वैलिडेट करना और रियल-टाइम में एग्रीगेट करना होता है ताकि:
- विज्ञापनदाता (Advertisers) को सटीक बिलिंग भेजी जा सके।
- हर 1 मिनट में **Top 100 Most Clicked Ads** की गणना की जा सके।
- **Click Fraud (फर्जी क्लिक्स)** और बॉट हमलों से बचा जा सके।

### सिस्टम की मुख्य आवश्यकताएं (Requirements)
- **1 Billion Ad Clicks** प्रति दिन $\implies$ Average QPS: 10,000, Peak QPS: **50,000 Clicks / Second**।
- **Strict Data Correctness:** वित्तीय बिलिंग दांव पर होती है, इसलिए किसी भी क्लिक की डुप्लिकेट गिनती या मिसिंग स्वीकार्य नहीं है।
- **End-to-End Latency:** 1 से 2 मिनट के अंदर डैशबोर्ड पर एग्रीगेटेड डेटा उपलब्ध होना चाहिए।

---

## Step 1: Raw Data vs Aggregated Data (डेटा मॉडल रणनीति)

<div style="margin-left:3rem">
<img src="/images/21-ad-click-aggregation/digital-advertising-example.png" alt="Digital Advertising" width="500">
</div>

1. **Raw Click Data (रॉ डेटा):**
   - हर क्लिक का कच्चा लॉग: `[ad_id, click_timestamp, user_id, ip, country]`.
   - **फायदा:** 100% ऑडिट ट्रेल। यदि किसी कोड बग के कारण एग्रीगेशन गलत हुआ, तो 6 महीने बाद भी बैकफिल (Backfill) किया जा सकता है।
   - **कमी:** भारी स्टोरेज (~3 TB प्रति माह)। इसे सस्ती S3 कोल्ड स्टोरेज में सुरक्षित रखा जाता है।
2. **Aggregated Data (संसाधित डेटा):**
   - 1-मिनट के टाइम विंडो में संक्षेप: `[ad_id, click_minute, country, click_count]`.
   - **फायदा:** अत्यंत तेज़ डैशबोर्ड क्वेरीज़ (Cassandra / DynamoDB में स्टोर)।

---

## Step 2: Stream Processing Pipeline (MapReduce & DAG Framework)

50,000 प्रति सेकंड क्लिक्स को प्रोसेस करने के लिए **Apache Kafka + Apache Flink / Spark Streaming** का उपयोग किया जाता है:

<div style="margin-left:3rem">
<img src="/images/21-ad-click-aggregation/ad-count-map-reduce.png" alt="MapReduce DAG" width="500">
</div>

### DAG (Directed Acyclic Graph) के 3 मुख्य नोड्स:
1. **Map Node:** Kafka से रॉ इवेंट्स पढ़ता है, अमान्य क्लिक्स फ़िल्टर करता है, और `ad_id % num_partitions` के आधार पर डेटा को डाउनस्ट्रीम एग्रीगेटर्स में बांटता है।
2. **Aggregate Node:** इन-मेमोरी टंबलिंग विंडो (Tumbling Window) में हर 1 मिनट के क्लिक्स को जोड़ता है ($O(1)$ हैश मैप में)।
3. **Reduce Node:** विभिन्न एग्रीगेटर नोड्स के परिणामों को समेटता है और **Min-Heap** डेटा स्ट्रक्चर की मदद से **Top 100 Most Clicked Ads** निकालता है।

<div style="margin-left:3rem">
<img src="/images/21-ad-click-aggregation/top-100-map-reduce.png" alt="Top 100 MapReduce" width="500">
</div>

---

## Step 3: टाइम विंडो की अवधारणा (Tumbling vs Sliding Windows)

स्ट्रीम प्रोसेसिंग में समय को कैसे मापा जाए?
1. **Tumbling Window (फिक्स्ड विंडो - गैर-ओवरलैपिंग):**
   - उदाहरण: 1:00 - 1:01, 1:01 - 1:02. प्रत्येक इवेंट ठीक 1 विंडो में गिना जाता है।
2. **Sliding Window (स्लाइडिंग विंडो - ओवरलैपिंग):**
   - उदाहरण: *"पिछले 5 मिनट में हुए क्लिक्स, जो हर 1 मिनट पर अपडेट हों"*।
3. **Watermarking (देर से आने वाले इवेंट्स को संभालना):**
   - यदि मोबाइल फोन टनल में नेटवर्क खोने के बाद 3 मिनट पुराने क्लिक भेजता है, तो **Watermark Threshold (जैसे 5 मिनट)** तय किया जाता है। थ्रेशोल्ड के अंदर के इवेंट्स विंडो में शामिल कर लिए जाते हैं; उससे ज्यादा पुराने इवेंट्स डेड-लेटर कतार (DLQ) में डाल दिए जाते हैं।

---

## Step 4: Exactly-Once Processing Semantics (सटीक गिनती की गारंटी)

वित्तीय रिपोर्टिंग के लिए डुप्लिकेट क्लिक्स रोकना अनिवार्य है:
1. **Kafka Idempotent Producer:** नेटवर्क री-ट्राई पर ब्रोकर डुप्लिकेट मैसेज को ड्रॉप कर देता है।
2. **Flink Distributed Checkpointing (Chandy-Lamport Algorithm):** नियमित अंतराल पर स्टेट का स्नैपशॉट S3 में सेव होता है। यदि कोई वर्कर क्रैश हो जाए, तो सिस्टम पिछले चेकपॉइंट से रीस्टार्ट होता है।
3. **Idempotent Storage Write:** डाउनस्ट्रीम डेटाबेस (Cassandra / ClickHouse) में अपडेट्स को `ad_id + minute` की यूनिक प्राइमरी की के साथ स्टोर किया जाता है।
