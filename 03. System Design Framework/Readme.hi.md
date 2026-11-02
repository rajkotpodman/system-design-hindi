# Chapter 3: System Design Interview Framework (4-स्टेप इंटरव्यू गाइड)

## Introduction (भूमिका)
System Design Interview किसी भी सीनियर सॉफ्टवेयर इंजीनियर या आर्किटेक्ट के चयन का सबसे महत्वपूर्ण राउंड होता है। यह इंटरव्यू केवल आपकी कोडिंग स्किल्स नहीं, बल्कि यह जांचता है कि आप:
- अस्पष्ट (Ambiguous) आवश्यकताओं को कैसे स्पष्ट करते हैं,
- इंटरव्यूअर के साथ एक टीममेट की तरह कैसे कम्युनिकेट करते हैं,
- ट्रेड-ऑफ्स (Trade-offs: जैसे Latency vs Consistency) का मूल्यांकन कैसे करते हैं।

इस चैप्टर में हम **jigsi_karia** द्वारा सुझाया गया **4-Step Proven Framework** समझेंगे जिससे आप 45 मिनट के इंटरव्यू में सबसे प्रभावशाली प्रदर्शन कर सकें।

---

## 45-Minute Time Allocation (समय का सही प्रबंधन)

एक 45-मिनट के इंटरव्यू को 4 हिस्सों में बांटना सबसे सुरक्षित रणनीति है:

| Step | चरण का नाम | अनुशंसित समय | मुख्य उद्देश्य |
| :--- | :--- | :--- | :--- |
| **Step 1** | Understand Problem & Scope | **3 - 8 मिनट** | सवाल पूछना, स्कोप तय करना, नॉन-फंक्शनल जरूरतें |
| **Step 2** | High-Level Design & Buy-in | **10 - 15 मिनट** | कोर API, एंड-टू-एंड ब्लॉक डायग्राम, इंटरव्यूअर की सहमति |
| **Step 3** | Design Deep Dive | **15 - 25 मिनट** | बॉटलनेक्स, डेटा स्ट्रक्चर्स, डीप एल्गो, फॉल्ट टॉलरेंस |
| **Step 4** | Wrap-Up & Trade-offs | **3 - 5 मिनट** | सिस्टम समरी, मॉनिटरिंग, फ्यूचर इम्प्रूवमेंट्स |

---

## Step 1: Understand the Problem & Establish Design Scope (समस्या को समझना)

> [!CAUTION]
> **सबसे बड़ी गलती (Premature Design):**
> इंटरव्यूअर के सवाल खत्म होते ही तुरंत व्हाइटबोर्ड पर बॉक्स बनाना कभी शुरू न करें! सिस्टम डिज़ाइन में जानबूझकर सवाल अस्पष्ट (Open-ended) पूछे जाते हैं ताकि देखा जा सके कि आप सही सवाल पूछते हैं या गलत धारणाएं बना लेते हैं।

### इंटरव्यूअर से क्या पूछें?
1. **Specific Features:** *"इस सिस्टम के कौन से 2-3 मुख्य फीचर्स हैं जिन पर आज हमें फोकस करना चाहिए?"*
2. **Scale & Traffic:** *"सिस्टम का DAU (Daily Active Users) कितना है? क्या यह Read-heavy है या Write-heavy?"*
3. **Clients:** *"क्या यह मोबाइल ऐप है, वेब ऐप है, या दोनों?"*
4. **Constraints:** *"डेटा प्राइवेसी या लेटेंसी के कोई विशेष नियम हैं?"*

### Functional vs Non-Functional Requirements स्पष्ट करें
- **Functional:** सिस्टम क्या करेगा (उदा. यूज़र लिंक शॉर्ट कर सके, 1000 दोस्तों को न्यूज़फीड दिखे)।
- **Non-Functional:** सिस्टम की गुणवत्ता कैसी होगी (उदा. 99.99% Availability, <50ms Read Latency, Eventual vs Strong Consistency)।

---

## Step 2: High-Level Design & Get Buy-in (हाई-लेवल आर्किटेक्चर)

ब्लूप्रिंट तैयार करें और इंटरव्यूअर के साथ विचार साझा करें:
1. **Core APIs डिफाइन करें:** REST या gRPC एंडपॉइंट्स (Parameters, Payloads, Response Codes).
2. **High-Level Box Diagram बनाएं:**
   - Client (Mobile/Web) $\to$ CDN / DNS
   - Load Balancer $\to$ Stateless API Servers
   - In-Memory Cache (Redis) $\to$ Primary Database (SQL/NoSQL)
   - Async Workers & Message Queues (Kafka)
3. **Data Flow समझाइए:** एक आम यूज़र की रिक्वेस्ट सिस्टम में कैसे प्रवेश करती है और कैसे रिस्पॉन्स लौटाया जाता है।
4. **इंटरव्यूअर से सहमति लें (Buy-in):** *"क्या यह ओवरऑल फ्लो ठीक लग रहा है, या हम किसी विशेष कंपोनेंट पर गहराई से चर्चा करें?"*

---

## Step 3: Design Deep Dive (गहराई में उतरना)

अब आपको सिस्टम के सबसे नाज़ुक और दिलचस्प कंपोनेंट्स में जाना है। अलग-अलग सिस्टम्स के लिए Deep Dive अलग होता है:
- **URL Shortener में:** Base62 Conversion और ID जनरेशन में टकराव (Hash Collisions) से कैसे निपटें?
- **Rate Limiter में:** Race Conditions कैसे रोकें? (Redis Lua Scripts vs Token Bucket).
- **Chat System में:** WebSockets का स्टेट कैसे मैनेज करें और जब यूज़र डिस्कनेक्ट हो तो मैसेज डिलीवरी गारंटी (At-least-once) कैसे दें?
- **Consistent Hashing में:** वर्चुअल नोड्स (Virtual Nodes) के जरिए हॉटस्पॉट्स कैसे खत्म करें?

---

## Step 4: Wrap-Up & Trade-offs (समापन)

इंटरव्यू के अंतिम 5 मिनट में:
1. **कोई भी सिस्टम 'परफेक्ट' नहीं होता:** हर आर्किटेक्चर में ट्रेड-ऑफ्स होते हैं (जैसे: CAP Theorem में Consistency बनाम Availability का चुनाव)। इंटरव्यूअर को बताएं कि आपने यह चुनाव क्यों किया।
2. **Single Point of Failure (SPOF) पहचानें:** अगर कोई मुख्य नोड क्रैश हो जाए, तो सिस्टम कैसे रिकवर होगा?
3. **Monitoring & Alerting:** सिस्टम को प्रोडक्शन में कैसे ट्रैक करेंगे (CPU/Memory metrics, Latency percentiles like p99/p95, Error rates)?
4. **Next Scale Level:** *"अगर हमारा ट्रैफिक 10 गुना (10x) बढ़ जाए, तो हम डेटाबेस Sharding और Multi-Region Active-Active रेप्लिकेशन कैसे करेंगे?"*

---

## इंटरव्यू के क्या करें और क्या न करें (Dos and Don'ts)

### ✅ अवश्य करें (Dos)
- इंटरव्यूअर को अपना सहयोगी (Collaborator/Teammate) मानें।
- अपने दिमाग की सोच (Thinking Process) को ज़ोर से बोलकर व्यक्त करें (Think Out Loud)।
- जहां भी गणना की आवश्यकता हो, Back-of-the-envelope नंबर्स इस्तेमाल करें।
- विकल्पों की तुलना करें (जैसे: *"हम SQL भी ले सकते हैं क्योंकि हमें ACID चाहिए, लेकिन NoSQL इसलिए चुन रहे हैं क्योंकि स्कीमा फ्लेक्सिबल है"*).

### ❌ कभी न करें (Don'ts)
- चुप रहकर मन ही मन सोचते न रहें।
- बिना सोचे-समझे ओवर-इंजीनियरिंग (Over-engineering) न करें (100 यूज़र्स के लिए सीधे Kubernetes और Kafka न लगाएं)।
- इंटरव्यूअर के हिंट्स को नजरअंदाज न करें। यदि इंटरव्यूअर किसी दिशा में संकेत दे रहा है, तो उस ओर मुड़ें।
