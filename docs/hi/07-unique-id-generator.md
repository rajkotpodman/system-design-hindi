# Chapter 7: Distributed Unique ID Generator Design करना (Snowflake ID)

## Introduction (भूमिका)
इस चैप्टर में हम डिस्ट्रीब्यूटेड सिस्टम्स के लिए एक **Unique ID Generator** डिज़ाइन करना सीखेंगे। 

पारंपरिक रिलेशनल डेटाबेस (जैसे MySQL) का सिंगल `AUTO_INCREMENT` प्राइमरी की फ़ीचर एक सिंगल सर्वर पर तो ठीक काम करता है, लेकिन जब आपका सिस्टम कई डेटा सेंटर्स और दर्जनों सर्वर्स में फैल जाता है, तो सिंगल डेटाबेस एक भारी **Single Point of Failure (SPOF)** और **Performance Bottleneck** बन जाता है।

### सिस्टम की मुख्य जरूरतें (Requirements)
- **Global Uniqueness:** पूरे विश्व में किसी भी दो रिकॉर्ड्स को एक जैसी ID नहीं मिलनी चाहिए।
- **64-bit Numerical ID:** ID को 64-bit पूर्णांक (integer) में फिट होना चाहिए (64-bit integer डेटाबेस इंडेक्सिंग और स्टोरेज में UUID से कहीं ज्यादा कुशल होते हैं)।
- **Roughly Ordered by Time:** नई बनने वाली ID का मान पुरानी ID से बड़ा होना चाहिए ताकि डेटाबेस B-Tree इंडेक्स पर राइट्स हमेशा अपेंड-ओनली (Append-only) रहें और पेज स्प्लिट्स (Page Splits) न हों।
- **High Throughput:** सिस्टम को प्रति सेकंड 10,000 से अधिक IDs जनरेट करने में सक्षम होना चाहिए, वो भी शून्य नेटवर्क कोऑर्डिनेशन के साथ।

---

## 4 आर्किटेक्चर विकल्प (High-Level Architecture Options)

### 1. Multi-Master Replication (मल्टी-मास्टर ऑटो-इंक्रीमेंट)
- **तरीका:** यदि क्लस्टर में $k$ डेटाबेस सर्वर्स हैं, तो प्रत्येक सर्वर `+k` के स्टेप से इंक्रीमेंट करता है। उदाहरण के लिए, सर्वर 1 जनरेट करेगा (1, 4, 7), सर्वर 2 जनरेट करेगा (2, 5, 8), और सर्वर 3 जनरेट करेगा (3, 6, 9)।
- **समस्याएं:** 
  - जब नए सर्वर जोड़े या हटाए जाते हैं, तो स्टेप साइज बदलना बहुत मुश्किल होता है।
  - यह समय के अनुसार क्रमबद्ध (Time-Sorted) नहीं रहता।
  - मल्टीपल डेटा सेंटर्स के बीच स्केल करना बेहद जटिल है।

<p align="left">
<img src="/images/07-unique-id-generator/multi-master.png" alt="Multi Master" width="400">
</p>

---

### 2. UUID (Universally Unique Identifier - 128-bit)
- **तरीका:** प्रत्येक वेब सर्वर स्वतंत्र रूप से बिना किसी सेंट्रल अथॉरिटी के 128-bit UUID (जैसे `123e4567-e89b-12d3-a456-426614174000`) जनरेट करता है।
- **फायदे:** सर्वर्स के बीच शून्य कोऑर्डिनेशन की जरूरत होती है।
- **कमियां:** 
  - 128 bits आकार (64-bit की सीमा से दोगुना बड़ा)।
  - स्ट्रिंग्स होने के कारण इंडेक्सिंग बहुत धीमी होती है।
  - समय के साथ ऑर्डर (Sortable by time) नहीं होते।

<p align="left">
<img src="/images/07-unique-id-generator/uuid.png" alt="UUID generator" width="600">
</p>

---

### 3. Ticket Server (Flickr Approach)
- **तरीका:** एक या दो डेडिकेटेड डेटाबेस सर्वर्स रखे जाते हैं जो केवल आईडी जनरेट करने के लिए `REPLACE INTO Tickets64 ...` क्वेरी चलाते हैं।
- **कमियां:** सिंगल पॉइंट ऑफ फेलियर (Single Point of Failure) और नेटवर्क लेटेंसी। यदि टिकट सर्वर डाउन हुआ, तो पूरा सिस्टम ठप हो जाएगा।

<p align="left">
<img src="/images/07-unique-id-generator/ticket-server.png" alt="Ticket Server" width="500">
</p>

---

### 4. Twitter Snowflake Approach (उद्योग मानक - सबसे बेहतरीन समाधान)

Twitter का **Snowflake** आर्किटेक्चर 64-bit ID को विभिन्न बिट-सेगमेंट्स (Bit Segments) में बांट देता है:

<div style="margin-left:3rem">
<img src="/images/07-unique-id-generator/twitter-snowflake.png" alt="Snowflake approach" width="500">
</div>
<div style="margin-left:3rem">
<img src="/images/07-unique-id-generator/snowflake-id-breakdown.png" alt="Snowflake ID breakdown" width="500">
</div>

#### 64 Bits का सटीक विभाजन:
1. **Sign Bit (1 bit):** हमेशा `0` रहता है। यह सुनिश्चित करता है कि ID हमेशा एक पॉजिटिव (धनात्मक) पूर्णांक रहे।
2. **Timestamp (41 bits):** कस्टम एपोक (Custom Epoch) से बीते हुए मिलीसेकंड्स (Milliseconds)।
   - $2^{41} - 1 \approx 2,199,023,255,551\text{ ms} \approx 69\text{ वर्ष}$। यानी यह सिस्टम 69 साल तक बिना रीसेट किए चल सकता है!
3. **Datacenter ID (5 bits):** अधिकतम $2^5 = 32$ अलग-अलग डेटा सेंटर्स को सपोर्ट करता है।
4. **Worker / Machine ID (5 bits):** प्रत्येक डेटा सेंटर के अंदर $2^5 = 32$ अलग-अलग मशीनों को सपोर्ट करता है। (कुल $32 \times 32 = 1024$ नोड्स)।
5. **Sequence Number (12 bits):** एक ही मशीन पर, उसी एक मिलीसेकंड के अंदर बनने वाली प्रत्येक आईडी के लिए काउंटर `0` से `4095` ($2^{12}$) तक बढ़ता है। हर नए मिलीसेकंड में यह काउंटर दोबारा `0` पर रीसेट हो जाता है।

$$\text{Capacity per Node} = 4096 \text{ IDs / millisecond} = 4,096,000 \text{ IDs / second}$$

---

## डिस्ट्रीब्यूटेड एज-केस: Clock Synchronization (क्लाक ड्रिफ्ट)
- **चुनौती:** Snowflake एल्गोरिदम मानता है कि क्लस्टर के सभी सर्वर्स की घड़ियां (Hardware Clocks) आपस में सिंक्रनाइज़्ड हैं। यदि किसी सर्वर की घड़ी पीछे चली जाती है (NTP Clock Drift / Leap Second), तो डुप्लिकेट आईडी बनने का खतरा हो सकता है।
- **समाधान:** 
  - **NTP (Network Time Protocol)** का उपयोग करें।
  - यदि कोड डिटेक्ट करे कि `current_timestamp < last_timestamp`, तो सिस्टम को एरर फेंकना चाहिए या घड़ी के आगे बढ़ने तक इंतज़ार (Wait / Spin) करना चाहिए।

---

## इंटरव्यू समरी (Interview Key Points)
- 64-bit integer IDs डेटाबेस (MySQL InnoDB / PostgreSQL B-tree) में कैश और पेजिंग के लिहाज से सबसे कुशल होती हैं।
- Snowflake IDs समय के अनुसार मोनोथॉनिकली बढ़ती हैं (Monotonically Increasing), जिससे डेटा हमेशा डिस्क पर सीक्वेंशियल राइट (Sequential Write) होता है और रैंडम I/O से बचा जा सकता है।
