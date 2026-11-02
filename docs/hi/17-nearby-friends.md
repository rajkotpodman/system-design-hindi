# Chapter 17: Nearby Friends System Design (रियल-टाइम आस-पास के दोस्त)

## Introduction (भूमिका)
इस चैप्टर में हम एक ऐसा रियल-टाइम लोकेशन शेयरिंग सिस्टम डिज़ाइन करेंगे जो यूज़र्स को अपने उन दोस्तों की दूरी और लोकेशन दिखाता है जो इस समय उनके **आस-पास (5 मील या 8 किमी के दायरे में)** मौजूद हैं।

> **Proximity Service और Nearby Friends में क्या अंतर है?**
> - Proximity Service (Ch 16) में दुकानों या रेस्तरां की लोकेशन स्थिर (Static) रहती है।
> - Nearby Friends में **यूज़र्स लगातार चल रहे होते हैं (Dynamic Real-time Locations)**, इसलिए डेटा सेकंड-दर-सेकंड बदलता है।

---

## Step 1: Requirements और Scale (क्षमता का अनुमान)

### Scale & Constraints
- **100 Million Daily Active Users (DAU)**, जिसमें से 10% (10 Million) समवर्ती (Concurrent) यूज़र्स हैं।
- औसतन हर यूज़र के 400 दोस्त हैं।
- **लोकेशन अपडेट फ्रीक्वेंसी:** हर **30 सेकंड** में 1 बार (क्योंकि इंसान की चलने की गति धीमी होती है, मिलीसेकंड्स में अपडेट की जरूरत नहीं होती)।
- **Location Update QPS:**
  $$\text{Update QPS} = \frac{10,000,000 \text{ Users}}{30 \text{ Seconds}} \approx \mathbf{334,000\text{ Updates / Second}}$$
- **Forwarding QPS:** यदि हर यूज़र के 40 दोस्त इस समय ऑनलाइन हैं, तो प्रति सेकंड लगभग **13.3 Million Location Updates** दोस्तों को फॉरवर्ड करने होंगे!

---

## Step 2: High-Level Architecture (WebSockets + Redis Pub/Sub)

<div style="margin-left:3rem">
<img src="/images/17-nearby-friends/simple-high-level-design.png" alt="Simple HLD" width="500">
</div>

### मुख्य कंपोनेंट्स:
1. **WebSocket Servers:** मोबाइल क्लाइंट्स और बैकएंड के बीच निरंतर खुला हुआ डुप्लेक्स कनेक्शन रखते हैं ताकि लेटेंसी न्यूनतम रहे।
2. **Redis Location Cache:** प्रत्येक एक्टिव यूज़र की सबसे ताज़ा लोकेशन `(latitude, longitude, timestamp)` रखता है। हर एंट्री पर **10 मिनट का TTL** सेट होता है; यदि 10 मिनट तक कोई पिंग न आए, तो यूज़र अपने आप ऑफलाइन मान लिया जाता है।
3. **Redis Pub/Sub (पब्लिश/सब्सक्राइब बस):** हर यूज़र का एक समर्पित चैनल (`channel_user_123`) होता है। जब भी यूज़र लोकेशन अपडेट करता है, उसके चैनल पर पब्लिश होता है। उसके ऑनलाइन दोस्त उस चैनल को सब्सक्राइब करके तुरंत ताज़ा लोकेशन प्राप्त कर लेते हैं।

<div style="margin-left:3rem">
<img src="/images/17-nearby-friends/redis-pubsub-usage.png" alt="Redis PubSub" width="500">
</div>

---

## Step 3: Detailed Location Update Flow (डेटा प्रवाह)

<div style="margin-left:3rem">
<img src="/images/17-nearby-friends/detailed-periodic-location-update.png" alt="Detailed Flow" width="500">
</div>

1. मोबाइल फोन हर 30 सेकंड में लोड बैलेंसर के ज़रिए अपने WebSocket सर्वर को नया GPS कोऑर्डिनेट भेजता है।
2. WebSocket सर्वर **Redis Location Cache** में यूज़र की लोकेशन अपडेट करता है।
3. WebSocket सर्वर यूज़र के समर्पित **Redis Pub/Sub चैनल** में मैसेज पब्लिश करता है: `{"user_id": "alice", "lat": 28.61, "long": 77.20}`।
4. Redis Pub/Sub यह मैसेज उन सभी WebSocket सर्वर्स को ब्रॉडकास्ट करता है जहाँ एलिस के दोस्त (जैसे बॉब, चार्ली) कनेक्टेड हैं।
5. बॉब का WebSocket सर्वर दूरी (Distance Formula) मापता है:
   - यदि दूरी $\le 5\text{ miles}$ है: बॉब के फोन पर नया डिस्टेंस और टाइमस्टैम्प भेज दिया जाता है।
   - यदि दूरी $> 5\text{ miles}$ है: मैसेज छोड़ दिया जाता है।

---

## Step 4: 14 Million Pub/Sub Updates को कैसे स्केल करें?

14 Million प्रति सेकंड मैसेज डिलीवर करने के लिए एक अकेला Redis सर्वर काफी नहीं है (एक Redis नोड ~100k मैसेज/सेकंड हैंडल करता है):
- **Redis Pub/Sub Cluster Sharding:** कम से कम **140 Redis नोड्स** का क्लस्टर बनाया जाता है।
- **Consistent Hashing:** यूज़र ID के हैश (`hash(user_id) % num_shards`) के आधार पर चैनल को विशिष्ट Redis पब/सब सर्वर पर असाइन किया जाता है।
- **Service Discovery (ZooKeeper):** WebSocket सर्वर्स को यह ट्रैक करने में मदद करता है कि कौन सा चैनल किस Redis नोड पर स्थित है।
