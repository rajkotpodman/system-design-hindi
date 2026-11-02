# Chapter 9: Distributed Web Crawler Design करना (Googlebot Architecture)

## Introduction (भूमिका)
एक **Web Crawler** (जिसे स्पाइडर या बॉट भी कहा जाता है) एक ऑटोमेटेड प्रोग्राम होता है जो पूरे इंटरनेट पर घूमकर नए और अपडेटेड वेब पेजेस, इमेजेस और लिंक्स को खोजता है और डाउनलोड करता है।

इसका सबसे बड़ा उदाहरण **Googlebot** है, जो दुनिया भर के अरबों वेब पेजों को क्रॉल करके Google Search Engine के लिए इंडेक्स (Search Index) तैयार करता है।

### मुख्य उपयोग (Applications)
1. **Search Engine Indexing:** सर्च इंजन के लिए वेब डेटा एकत्र करना।
2. **Web Archiving:** इंटरनेट के इतिहास को भविष्य के लिए संरक्षित करना (जैसे Internet Archive / Wayback Machine).
3. **Web Mining:** वित्तीय रिपोर्ट, रिसर्च पेपर या मार्केट ट्रेंड्स का डेटा माइनिंग करना।
4. **Web Monitoring:** कॉपीराइट या ट्रेडमार्क उल्लंघन पकड़ना।

---

## Step 1: Requirements और Scope समझना

- **Scale:** प्रति माह **1 Billion (100 करोड़) वेब पेजेस** क्रॉल करना।
  - $\frac{1,000,000,000}{30 \times 86400} \approx 400 \text{ Pages / Second}$ (Peak QPS: ~800).
- **Scope:** केवल HTML कंटेंट डाउनलोड करना (मीडिया फाइल्स जैसे MP4 आउट-ऑफ-स्कोप हैं)।
- **Storage:** औसतन 1 वेब पेज = 500 KB $\implies 1 \text{ Billion} \times 500 \text{ KB} = 500 \text{ TB / Month}$। 5 वर्षों के लिए $\approx 30 \text{ Petabytes (PB)}$ स्टोरेज।
- **Non-Functional Requirements:**
  - **Scalability:** हज़ारों क्रॉलर थ्रेड्स को पैरेलल में चलाना।
  - **Robustness:** क्रैश, टूटे हुए HTML लिंक्स, और स्पाइडर ट्रैप्स को संभालना।
  - **Politeness (विनम्रता):** किसी एक वेबसाइट के सर्वर पर अचानक हज़ारों रिक्वेस्ट्स भेजकर उसे डाउन (DoS) नहीं करना!
  - **Extensibility:** भविष्य में PDF या इमेज क्रॉलर जोड़ना आसान होना।

---

## Step 2: High-Level Architecture (सिस्टम कंपोनेंट्स)

<p align="center">
<img src="/images/09-web-crawler/web-crawler-architecture.png" alt="Web Crawler Architecture" width="700">
</p>

1. **Seed URLs:** क्रॉलर के शुरुआती शुरुआती बिंदु (जैसे Wikipedia, Yahoo Directory या विषयवार टॉप साइट्स)।
2. **URL Frontier:** डाउनलोड किए जाने वाले URLs की कतार (Priority + Politeness Queue)।
3. **HTML Downloader:** वेब सर्वर से HTTP GET रिक्वेस्ट के ज़रिए HTML पेज डाउनलोड करता है।
4. **DNS Resolver:** डोमेन नाम (जैसे `wikipedia.org`) को IP Address में बदलता है।
5. **Content Parser:** HTML को पार्स करता है और चेक करता है कि पेज वेल-फॉर्म्ड है या नहीं।
6. **Content Seen? (Duplicate Detection):** दो वेब पेजों के कंटेंट हैश (MD5 / SimHash) की तुलना करता है ताकि डुप्लिकेट पेज दोबारा स्टोर न हों।
7. **Content Storage:** असली HTML डेटा को डिस्क/ऑब्जेक्ट स्टोरेज में सेव करता है।
8. **URL Extractor:** डाउनलोड किए गए पेज से नए `<a>` लिंक्स निकालता है।
9. **URL Filter:** ब्लैकलिस्टेड या अवांछित डोमेन्स को हटाता है।
10. **URL Seen? (Visited URL Cache):** **Bloom Filter** का उपयोग करके चेक करता है कि यह लिंक पहले क्रॉल हो चुका है या नहीं।

---

## Step 3: Deep Dive into Critical Components

### 1. BFS vs DFS Traversal
वेब को एक डायरेक्टेड ग्राफ (Directed Graph) माना जा सकता है जहाँ पेजेस नोड्स हैं और हाइपरलिंक्स एजेस हैं:
- DFS (Depth-First Search) बहुत गहरे रास्तों में फंस सकता है।
- इसलिए हमेशा **BFS (Breadth-First Search)** का उपयोग किया जाता है।
- लेकिन स्टैंडर्ड BFS में दो कमियां होती हैं:
  1. हर पेज की क्वालिटी समान नहीं होती (Priority की कमी)।
  2. एक ही होस्ट (Host) पर एक साथ 100 रिक्वेस्ट्स जा सकती हैं (Politeness की कमी)।

---

### 2. URL Frontier: Politeness & Prioritization

<img src="/images/09-web-crawler/politeness.png" alt="Politeness" width="500">

#### a. Politeness (विनम्रता - DoS से बचाव)
- एक ही डोमेन (जैसे `example.com`) के सभी URLs को एक ही कतार में रखा जाता है।
- एक वर्कर थ्रेड एक समय में केवल एक ही डोमेन से पेज डाउनलोड करता है, और दो डाउनलोड्स के बीच एक निश्चित डिले (Delay) रखता है।
- **Robots.txt:** डाउनलोड करने से पहले साइट की `robots.txt` फाइल को पढ़ा और सम्मान किया जाता है।

#### b. Prioritization (प्राथमिकता)
<img src="/images/09-web-crawler/prioritizer.png" alt="Politeness" width="500">

- **PageRank** और अपडेट फ्रीक्वेंसी के आधार पर महत्वपूर्ण पेजेस (जैसे CNN, Wikipedia) को उच्च प्राथमिकता (High Priority Queue) में डाला जाता है।

---

### 3. Spider Traps और डेटा लूप्स से बचाव
- कुछ वेबसाइट्स डायनेमिक URL जनरेट करके बॉट्स को अनंत लूप (Infinite Loop) में फंसा देती हैं:
  - उदा. `example.com/foo/bar/foo/bar/foo/bar...`
- **बचाव:** 
  - URL स्ट्रिंग की अधिकतम लंबाई (जैसे 255 वर्ण) सीमित करना।
  - एक ही डोमेन से क्रॉल किए जाने वाले पेजेस की सीमा तय करना।

---

## इंटरव्यू समरी (Interview Summary)
- URL Frontier में **Front Queues** प्रायोरिटी संभालती हैं और **Back Queues** विनम्रता (Politeness) सुनिश्चित करती हैं।
- यूआरएल डुप्लीकेशन चेक करने के लिए **Bloom Filter** का उपयोग किया जाता है जिससे अरबों लिंक्स रैम में मात्र कुछ GB में चेक हो जाते हैं।
