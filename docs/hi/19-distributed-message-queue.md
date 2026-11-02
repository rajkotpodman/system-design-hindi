# Chapter 19: Distributed Message Queue Design करना (Apache Kafka Architecture)

## Introduction (भूमिका)
एक **Distributed Message Queue** (जैसे Apache Kafka, RabbitMQ, या Apache Pulsar) आधुनिक माइक्रो-सर्विसेज आर्किटेक्चर की रीढ़ है। यह विभिन्न सर्विसेज को एक-दूसरे से पूरी तरह डीकपल (Decouple) करता है, ट्रैफिक के अचानक आने वाले बर्स्ट्स को बफर करता है, और डेटा को बिना खोए सुरक्षित डिलीवर करता है।

### Message Queues के मुख्य लाभ
- **Decoupling:** प्रोड्यूसर और कंज्यूमर एक-दूसरे की आंतरिक कार्यप्रणाली से पूरी तरह स्वतंत्र रहते हैं।
- **Traffic Buffering:** यदि अचानक 10x ट्रैफिक आए, तो कतार में मैसेज जमा हो जाते हैं और बैकएंड डेटाबेस क्रैश होने से बच जाता है।
- **Asynchronous Processing:** प्रोड्यूसर को भारी प्रोसेस खत्म होने का इंतज़ार नहीं करना पड़ता।

---

## Step 1: Requirements और Scope समझना

- **Message Retention:** संदेशों को कम से कम **2 सप्ताह (14 दिन)** तक डिस्क पर सुरक्षित रखना।
- **Repeated Consumption:** एक ही मैसेज को कई अलग-अलग कंज्यूमर्स (जैसे बिलिंग, एनालिटिक्स, एमएल मॉडल) बार-बार स्वतंत्र रूप से पढ़ सकें।
- **Strict Ordering:** एक पार्टिशन के अंदर संदेश उसी क्रम में पढ़े जाने चाहिए जिस क्रम में वे भेजे गए थे (FIFO Guarantee)।
- **Delivery Semantics:** At-least-once (कम से कम एक बार) अनिवार्य, और कॉन्फ़िगरेशन द्वारा Exactly-once का समर्थन।
- **Ultra-High Throughput:** प्रति सेकंड लाखों इवेंट्स प्रोसेस करने की क्षमता।

---

## Step 2: High-Level Core Concepts (Topics, Partitions, Brokers)

<div style="margin-left:3rem">
<img src="/images/19-distributed-message-queue/partitions.png" alt="Partitions" width="500">
</div>

1. **Topic (टॉपिक):** संदेशों की एक लॉजिकल कैटेगरी (जैसे `order_events`, `user_clicks`).
2. **Partitions (पार्टिशन्स - Sharding का रहस्य):**
   - एक अकेला सर्वर अरबों संदेश नहीं संभाल सकता। इसलिए प्रत्येक टॉपिक को कई **Partitions** में बांट दिया जाता है।
   - प्रत्येक पार्टिशन एक अलग सर्वर (**Broker**) पर रहता है।
   - **पार्टिशन के अंदर मैसेज ऑर्डर 100% गारंटीड रहता है।**
3. **Offset (ऑफसेट):** पार्टिशन के अंदर प्रत्येक मैसेज का एक बढ़ता हुआ क्रम संख्यांक (Monotonically Increasing Sequence Number)।
   - किसी भी मैसेज का पता = `(Topic, Partition_ID, Offset)`.
4. **Consumer Groups (कंज्यूमर ग्रुप्स):**
<div style="margin-left:3rem">
<img src="/images/19-distributed-message-queue/consumer-groups.png" alt="Consumer Groups" width="500">
</div>
   - एक कंज्यूमर ग्रुप के अंदर कई कंज्यूमर्स मिलकर एक टॉपिक के विभिन्न पार्टिशन्स से समानांतर (Parallel) मैसेज पढ़ते हैं।
   - **गोल्डन रूल:** एक पार्टिशन को एक समय में एक कंज्यूमर ग्रुप का केवल एक ही कंज्यूमर प्रोसेस कर सकता है (ताकि ऑर्डर कभी न बिगड़े)।

---

## Step 3: Kafka की सुपर-स्पीड का रहस्य (Performance Under the Hood)

पारंपरिक डेटाबेस की तुलना में Kafka प्रति सेकंड 100x ज्यादा थ्रूपुट कैसे देता है?

### 1. Sequential Disk Writes (Append-Only Commit Log)
<div style="margin-left:3rem">
<img src="/images/19-distributed-message-queue/wal-example.png" alt="WAL Example" width="500">
</div>
- Kafka कभी भी डिस्क पर डेटा अपडेट या डिलीट नहीं करता। 
- यह फाइल के अंत में सिर्फ **सीक्वेंशियल अपेंड (Sequential Append)** करता है।
- यांत्रिक हार्ड डिस्क (HDD) पर भी सीक्वेंशियल राइट्स 600 MB/s से अधिक की स्पीड दे सकते हैं, जो रैंडम रैम राइट्स से भी तेज़ साबित हो सकता है!

### 2. Zero-Copy Data Transfer (OS PageCache)
पारंपरिक सिस्टम में जब फाइल डिस्क से नेटवर्क पर भेजी जाती है:
$$\text{Disk} \xrightarrow{(1)} \text{OS Buffer} \xrightarrow{(2)} \text{App Memory} \xrightarrow{(3)} \text{Socket Buffer} \xrightarrow{(4)} \text{NIC}$$
यह 4 बार मेमोरी कॉपी और कई कॉन्टेक्स्ट स्विचेस लेता है।

**Kafka का Zero-Copy (`sendfile()` Syscall):**
$$\text{OS PageCache} \xrightarrow{\text{Direct DMA Copy}} \text{Network Interface Card (NIC)}$$
डेटा कभी भी Java / App मेमोरी में नहीं आता, जिससे CPU उपयोग लगभग शून्य रहता है!

---

## Step 4: Push vs Pull Architecture

| मॉडल | कार्यप्रणाली | ट्रेड-ऑफ्स |
| :--- | :--- | :--- |
| **Push Model** | ब्रोकर तेज़ी से कंज्यूमर को मैसेज धकेलता है। | यदि कंज्यूमर धीमा है, तो उसका बफर ओवरफ्लो होकर क्रैश हो जाएगा। |
| **Pull Model (Kafka का चुनाव)** | कंज्यूमर अपनी क्षमता के अनुसार ब्रोकर से मैसेज मांगता है। | कंज्यूमर कभी ओवरलोड नहीं होता। कंज्यूमर अपनी गति से बैच बनाकर पढ़ता है। |

---

## Step 5: Fault Tolerance और ISR (In-Sync Replicas)
- प्रत्येक पार्टिशन का एक **Leader Broker** और कई **Follower Replicas** होते हैं।
- प्रोड्यूसर हमेशा लीडर को लिखता है, और फॉलोअर्स लीडर से डेटा कॉपी करते हैं।
- यदि लीडर क्रैश हो जाता है, तो **ZooKeeper / KRaft** सबसे ताज़ा इन-सिंक फॉलोअर (ISR) को तुरंत नया लीडर चुन लेता है।
