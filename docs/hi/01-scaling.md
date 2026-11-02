# Chapter 1: Zero से Millions of Users तक System Scale करना (Scale from 0 to Millions)

## Introduction (भूमिका)
किसी भी वेब या मोबाइल एप्लिकेशन को Zero से लाखों-करोड़ों (Millions) यूज़र्स के लिए Scale करना एक दिन का काम नहीं होता। यह एक निरंतर चलने वाली **Iterative Engineering Journey** है, जिसमें जैसे-जैसे ट्रैफिक बढ़ता है, आर्किटेक्चर के अलग-अलग बॉटलनेक्स (Bottlenecks) को पहचानकर सिस्टम को री-आर्किटेक्ट करना पड़ता है।

इस चैप्टर में हम एक साधारण **Single Server Setup** से शुरुआत करेंगे और step-by-step एक ऐसा Highly Available, Scalable, और Fault-Tolerant आर्किटेक्चर बनाएंगे जो करोड़ों यूज़र्स का ट्रैफिक आसानी से संभाल सके।

---

## Section 1: Single Server Setup (शुरुआती सेटअप)
शुरुआत में सब कुछ (Web Application, Database, Cache, Files) एक ही फिजिकल या वर्चुअल सर्वर पर चलता है।

<div style="margin-left:3rem">
<img src="/images/01-scaling/single-server.png" width="400" />
</div>

### Request Flow (रिक्वेस्ट का प्रवाह)
1. **DNS Lookup:** यूज़र ब्राउज़र में `mysite.com` डालता है। DNS सर्वर डोमेन नाम को सर्वर के पब्लिक IP Address में बदल देता है।
2. **HTTP Request:** ब्राउज़र उस IP Address पर HTTP/HTTPS GET या POST रिक्वेस्ट भेजता है।
3. **Response:** वेब सर्वर बिज़नेस लॉजिक रन करता है और क्लाइंट को HTML (वेबसाइट के लिए) या JSON (मोबाइल ऐप के लिए) रिस्पॉन्स लौटा देता है।

---

## Section 2: Database Separation (डेटाबेस को अलग करना)
जैसे ही ट्रैफिक थोड़ा बढ़ता है, सिंगल सर्वर का CPU और Memory दोनों घुटने टेकने लगते हैं। 
पहला कदम: **Web Tier** और **Data Tier** को अलग-अलग फिजिकल सर्वर्स पर अलग कर देना।

<div style="margin-left:3rem">
<img src="/images/01-scaling/database.png" width="400" />
</div>

### Database का चुनाव: SQL vs NoSQL
1. **Relational Databases (SQL):** 
   - *उदाहरण:* MySQL, PostgreSQL.
   - *उपयोग:* जब डेटा स्ट्रक्चर्ड हो, रिलेशंस हों, और ACID ट्रांजेक्शन्स (जैसे बैंकिंग, ई-कॉमर्स ऑर्डर्स) की सख्त जरूरत हो।
2. **Non-Relational Databases (NoSQL):**
   - *कैटेगरी:* Key-Value (Redis, DynamoDB), Document (MongoDB), Column-Family (Cassandra), Graph (Neo4j).
   - *उपयोग कब करें:* 
     - जब अल्ट्रा-लो लेटेंसी (Sub-millisecond latency) चाहिए।
     - जब डेटा अनस्ट्रक्चर्ड हो या स्कीमा लगातार बदल रहा हो।
     - जब भारी मात्रा में डेटा (Petabytes) को हॉरिजॉन्टली डिस्ट्रीब्यूट करना हो।

---

## Section 3: Vertical Scaling vs Horizontal Scaling

### Vertical Scaling (Scale Up)
- मौजूदा सर्वर में ही और अधिक CPU cores, RAM या डिस्क जोड़ना।
- **कमियां:** 
  - हार्डवेयर की एक भौतिक सीमा (Hardware Limit) होती है।
  - कोई Redundancy नहीं होती। यदि वह एक सर्वर डाउन हुआ, तो पूरा सिस्टम ऑफलाइन हो जाता है (**Single Point of Failure**)।

### Horizontal Scaling (Scale Out)
- एक शक्तिशाली मशीन खरीदने के बजाय क्लस्टर में कई सामान्य और सस्ती मशीनें (Nodes) जोड़ते जाना।
- लार्ज-स्केल डिस्ट्रीब्यूटेड सिस्टम्स के लिए यह एकमात्र टिकाऊ समाधान है।

---

## Section 4: Load Balancer (लोड बैलेंसर)

<div style="margin-left:3rem">
<img src="/images/01-scaling/load-balancer.png" width="400" />
</div>

जब हमारे पास एक से ज्यादा वेब सर्वर्स होते हैं, तो ट्रैफिक को समान रूप से बांटने के लिए हम **Load Balancer** (जैसे NGINX, HAProxy, AWS ALB) लगाते हैं।
- **Failover / Redundancy:** यदि Server 1 क्रैश हो जाए, तो Load Balancer तुरंत सारा ट्रैफिक Server 2 पर डाइवर्ट कर देता है। यूज़र को कोई डाउनटाइम महसूस नहीं होता।
- **Scalability:** ट्रैफिक बढ़ने पर बिना किसी डाउनटाइम के बैकएंड में 5 नए सर्वर्स और जोड़े जा सकते हैं।

---

## Section 5: Database Replication (डेटाबेस रेप्लिकेशन - Master/Slave)

<div style="margin-left:3rem">
<img src="/images/01-scaling/database-replication.png" width="400" />
</div>

ज्यादातर वेब एप्लिकेशन्स **Read-Heavy** होती हैं (यानी Reads vs Writes का अनुपात अक्सर 10:1 या 100:1 होता है)।
डेटाबेस को स्केल करने के लिए हम **Primary-Secondary (Master-Slave)** मॉडल अपनाते हैं:
- **Master Database:** केवल डेटा मॉडिफाई करने वाली राइट ऑपरेशन्स (INSERT, UPDATE, DELETE) हैंडल करता है।
- **Slave Databases:** मास्टर से डेटा रेप्लिकेट करते हैं और सभी रीड ऑपरेशन्स (SELECT) हैंडल करते हैं।

### Failover Scenario (फेलियर कैसे संभालें?)
- यदि कोई स्लेव डेटाबेस डाउन होता है, तो रीड क्वेरीज़ बाकी स्वस्थ स्लेव्स या अस्थायी रूप से मास्टर पर भेज दी जाती हैं।
- यदि मास्टर डेटाबेस डाउन होता है, तो एक स्लेव डेटाबेस को प्रमोट करके नया मास्टर बना दिया जाता है। (Replication Lag का ध्यान रखना आवश्यक होता है)।

---

## Section 6: Cache Tier (कैश लेयर)
बार-बार होने वाले भारी डेटाबेस रीड्स को कम करने के लिए हम मेमोरी-बेस्ड कैश (जैसे **Redis** या **Memcached**) लगाते हैं।

### Cache-Aside (Lazy Loading) पैटर्न
1. जब भी कोई डेटा चाहिए, वेब सर्वर पहले कैश चेक करता है।
2. **Cache Hit:** यदि डेटा कैश में मिल जाए, तो तुरंत वहीं से लौटा दिया जाता है (1ms से कम में)।
3. **Cache Miss:** यदि डेटा कैश में नहीं है, तो डेटाबेस से पढ़ा जाता है, कैश में स्टोर किया जाता है, और फिर क्लाइंट को भेजा जाता है।

---

## Section 7: Content Delivery Network (CDN)
स्टैटिक एसेट्स (HTML, CSS, JS, Images, Videos) को ओरिजिन सर्वर से दूर यूज़र के सबसे करीबी एज लोकेशन (Edge Servers - जैसे Cloudflare, CloudFront) पर कैश किया जाता है ताकि लेटेंसी न्यूनतम हो सके।

---

## Section 8: Stateless Web Tier (स्टेटलेस आर्किटेक्चर)
हॉरिजॉन्टली स्केल करने के लिए सबसे महत्वपूर्ण नियम है कि **वेब सर्वर को स्टेटलेस (Stateless) होना चाहिए**।
- यूज़र के सेशन डेटा (Session State) को कभी भी वेब सर्वर की लोकल मेमोरी में न रखें।
- सेशन डेटा को एक शेयर्ड पर्सिस्टेंट स्टोर (जैसे Redis Cluster या NoSQL Database) में रखें ताकि यूज़र की अगली रिक्वेस्ट क्लस्टर के किसी भी वेब सर्वर पर जाए, उसे दोबारा लॉगिन न करना पड़े।

---

## सम्पूर्ण आर्किटेक्चर सारांश (Final Architecture Summary)
लाखों यूज़र्स तक पहुँचने का फॉर्मूला:
1. Web Tier को **Stateless** रखें।
2. हर स्तर पर **Redundancy** (Load Balancers, Database Slaves) लागू करें।
3. जितना हो सके डेटा **Cache** करें (Redis + CDN)।
4. मल्टीपल डेटा सेंटर्स का उपयोग करें।
5. डेटाबेस को **Sharding / Partitioning** के जरिए स्केल करें।
6. बड़े मोनोलिथ को **Microservices** और **Message Queues** (Kafka/RabbitMQ) में विभाजित करें।
