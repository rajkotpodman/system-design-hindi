# Chapter 2: Back-of-the-Envelope Estimation (अनुमान लगाने की कला)

## Introduction (भूमिका)
**Back-of-the-envelope estimation** सिस्टम डिज़ाइन इंटरव्यू का एक सबसे महत्वपूर्ण हिस्सा है। इसका मतलब होता है: बिना कैलकुलेटर के, मन में या एक कागज़ के टुकड़े पर त्वरित और मोटे तौर पर (Rough Calculations) गणना करना ताकि सिस्टम की **Capacity, QPS (Queries Per Second), Bandwidth, और Storage** की आवश्यकताओं का सही अंदाज़ा लगाया जा सके।

Google के सीनियर फेलो **Jeff Dean** के अनुसार: *"ये अनुमान हमें यह जांचने में मदद करते हैं कि हमारा प्रस्तावित आर्किटेक्चर असल दुनिया की आवश्यकताओं को पूरा कर पाएगा या नहीं।"*

---

## Section 1: बुनियादी गणना नियम (Power of Two)

डेटा साइज की गणना के लिए $2$ की घातों (Powers of Two) को याद रखना बहुत ज़रूरी है:

| Power ($2^n$) | Approximate Value | Data Unit |
| :--- | :--- | :--- |
| $2^{10}$ | $1,000$ (1 Thousand) | 1 Kilobyte (KB) |
| $2^{20}$ | $1,000,000$ (1 Million) | 1 Megabyte (MB) |
| $2^{30}$ | $1,000,000,000$ (1 Billion) | 1 Gigabyte (GB) |
| $2^{40}$ | $1,000,000,000,000$ (1 Trillion) | 1 Terabyte (TB) |
| $2^{50}$ | $1,000,000,000,000,000$ | 1 Petabyte (PB) |

<img src="/images/02-back-of-the-envelope-estimation/power-of-two.png" alt="power-of-two" width="500" />

---

## Section 2: लेटेंसी के आंकड़े जो हर इंजीनियर को पता होने चाहिए (Latency Numbers)

सिस्टम डिज़ाइन में यह समझना अनिवार्य है कि कौन सा ऑपरेशन कितना समय लेता है:

| कम्प्यूटिंग ऑपरेशन | Latency (समय) | तुलनात्मक समझ |
| :--- | :--- | :--- |
| **L1 Cache Reference** | 0.5 ns | पलक झपकने से 10 लाख गुना तेज |
| **Branch Mispredict** | 5 ns | |
| **L2 Cache Reference** | 7 ns | L1 से 14x धीमा |
| **Main Memory (RAM) Access** | 100 ns | L1 से 200x धीमा |
| **SSD Random Read** | 150 µs (माइक्रोसेकंड) | RAM से 1,500x धीमा |
| **1 MB Sequential Read from RAM**| 250 µs | |
| **Data Center Round Trip (LAN)** | 500 µs | |
| **HDD Disk Seek (यांत्रिक डिस्क)** | 10 ms (मिलीसेकंड) | RAM से 100,000x धीमा! |
| **Cross-Continent Network Packet** | 150 ms | एक डेटा सेंटर से दूसरे तक |

### 3 सुनहरे नियम (Golden Rules):
1. **Memory (RAM) बहुत तेज है, Disk बहुत धीमी है:** हमेशा हॉट डेटा को Redis/Memcached जैसी इन-मेमोरी लेयर में रखें।
2. **Disk Seeks से बचें:** रैंडम डिस्क रीड्स सबसे धीमे होते हैं, सीक्वेंशियल राइट्स (जैसे Kafka commit log, LSM Tree) हमेशा तेज होते हैं।
3. **डेटा कंप्रेस करें:** इंटरनेट पर डेटा भेजने से पहले उसे कंप्रेस (Gzip/Brotli) करें; नेटवर्क बैंडविड्थ बचाना CPU कम्प्रेशन से ज्यादा मूल्यवान है।

---

## Section 3: High Availability और SLA (Availability Numbers in Nines)

सिस्टम की उपलब्धता (Uptime) को "Nines" में मापा जाता है:

| Availability % | Uptime SLA | प्रति वर्ष डाउनटाइम (Downtime per Year) |
| :--- | :--- | :--- |
| **99% (Two Nines)** | सामान्य सर्विस | 3.65 दिन डाउन |
| **99.9% (Three Nines)** | मानक क्लाउड सर्विस | 8.76 घंटे डाउन |
| **99.99% (Four Nines)** | एंटरप्राइज / ई-कॉमर्स | 52.6 मिनट डाउन |
| **99.999% (Five Nines)** | टेलीकॉम / बैंक कोर | केवल 5.26 मिनट डाउन! |
| **99.9999% (Six Nines)** | मिशन क्रिटिकल | मात्र 31.5 सेकंड डाउन |

---

## Section 4: इंटरव्यू केस स्टडी — Twitter QPS और Storage का अनुमान

### बुनियादी धारणाएं (Assumptions):
- **300 Million** Monthly Active Users (MAU).
- **50%** Daily Active Users (DAU) = **150 Million DAU**.
- प्रति यूजर प्रतिदिन औसतन **2 ट्वीट्स** पोस्ट करता है।
- औसतन 10% ट्वीट्स में मीडिया (Photos/Videos) होती हैं।
- 1 दिन में 86,400 सेकंड होते हैं (गणना को आसान बनाने के लिए हम इसे **~100,000 सेकंड** मान लेते हैं)।

### 1. Write QPS (Queries Per Second) की गणना:
$$\text{Daily Tweets} = 150 \text{ Million} \times 2 = 300 \text{ Million Tweets / Day}$$
$$\text{Average QPS} = \frac{300,000,000 \text{ Tweets}}{100,000 \text{ Seconds}} = 3,000 \text{ Tweets / Second}$$
$$\text{Peak QPS} = \text{Average QPS} \times 2 = 6,000 \text{ QPS}$$

### 2. Read QPS की गणना:
ट्विटर एक **Read-Heavy** सिस्टम है (यूज़र्स ट्वीट कम करते हैं, पढ़ते बहुत ज्यादा हैं)।
मान लीजिए हर यूज़र दिन में औसतन 50 ट्वीट्स देखता है:
$$\text{Daily Read Requests} = 150 \text{ Million} \times 50 = 7.5 \text{ Billion Reads / Day}$$
$$\text{Read QPS} = \frac{7,500,000,000}{100,000} = 75,000 \text{ QPS}$$

### 3. Storage (स्टोरेज) की गणना:
- **टेक्स्ट डेटा:** मान लीजिए 1 ट्वीट औसतन 140 बाइट्स टेक्स्ट + 160 बाइट्स मेटाडेटा = 300 Bytes.
  $$\text{Daily Text Storage} = 300 \text{ Million} \times 300 \text{ Bytes} \approx 90 \text{ GB / Day}$$
- **मीडिया डेटा (Photos/Videos):** 10% ट्वीट्स में मीडिया है (30 Million मीडिया ट्वीट्स/दिन)। मान लीजिए 1 मीडिया का औसत साइज 1 MB है:
  $$\text{Daily Media Storage} = 30 \text{ Million} \times 1 \text{ MB} = 30 \text{ TB / Day}$$
- **5 वर्षों के लिए कुल स्टोरेज:**
  $$\text{5 Years Storage} = 30 \text{ TB/day} \times 365 \times 5 \approx 55 \text{ Petabytes (PB)}$$

---

## इंटरव्यू के लिए टिप्स (Tips for the Interview)
1. **परफेक्ट सटीकता की जरूरत नहीं है:** इंटरव्यूअर यह नहीं देख रहा कि आपने दशमलव तक सही किया या नहीं, वह आपकी **तार्किक सोच (Structured Thinking)** देख रहा है।
2. **संख्याओं को गोल (Round) करें:** 86,400 को 100,000 मान लें, 1 मिलियन को $10^6$ लिखकर गणना आसान बनाएं।
3. **हमेशा यूनिट्स लिखें:** MB, GB, QPS, Latency को स्पष्ट रूप से लिखें।
