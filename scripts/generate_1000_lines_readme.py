# scripts/generate_1000_lines_readme.py
import os
import sys

def build_full_readme():
    lines = []
    def a(text=""):
        lines.append(text)

    # 1. Header
    a("# ⚡ System Design Interview — सम्पूर्ण मास्टर गाइड (हिन्दी / Tech-Hinglish)")
    a()
    a("> **वास्तुकला एवं संकलन:** jigsi_karia")
    a("> **मूल स्रोत संदर्भ:** *System Design Interview – An Insider's Guide (Volume 1 & 2)*")
    a("> **अनुशंसित दृष्टिकोण (Recommended Approach):** **Smart Tech-Hinglish**")
    a("> - **तकनीकी शब्दावली (Core Technical Terms) मूल अंग्रेजी में:** *Latency, Throughput, Consistent Hashing, Token Bucket, Read-Heavy vs Write-Heavy, Replication Lag, Partition Tolerance, Write-Ahead Log, Merkle Trees, B+ Tree, Gossip Protocol, LSM-Tree, Vector Clocks, Split-Brain* आदि।")
    a("> - **व्याख्या, आंतरिक आर्किटेक्चर और व्यापारिक निर्णय (Explanations, Flow & Trade-offs) प्रामाणिक, सरल एवं व्यावहारिक हिन्दी में।**")
    a()
    a("---")
    a()

    # 2. Table of Contents
    a("## 📑 विस्तृत विषय-सूची (Master Table of Contents)")
    a()
    a("1. [🚀 सिस्टम डिज़ाइन का दर्शन एवं 4-चरणीय इंटरव्यू फ्रेमवर्क](#-सिस्टम-डिज़ाइन-का-दर्शन-एवं-4-चरणीय-इंटरव्यू-फ्रेमवर्क)")
    a("   - [4-चरणीय समय प्रबंधन (4-Step Time Allocation)](#4-चरणीय-समय-प्रबंधन)")
    a("   - [लाइव मॉक इंटरव्यू संवाद (Live Mock Interview Dialogue)](#लाइव-मॉक-इंटरव्यू-संवाद)")
    a("2. [📐 इंटरव्यू में काम आने वाले Numbers (Back-of-the-envelope Cheat Sheet)](#-इंटरव्यू-में-काम-आने-वाले-numbers-back-of-the-envelope-cheat-sheet)")
    a("   - [Jeff Dean के हार्डवेयर एवं नेटवर्क लेटेंसी आंकड़े](#jeff-dean-के-हार्डवेयर-एवं-नेटवर्क-लेटेंसी-आंकड़े)")
    a("   - [Availability SLA और वार्षिक डाउनटाइम तालिका](#availability-sla-और-वार्षिक-डाउनटाइम-तालिका)")
    a("   - [क्षमता, थ्रूपुट और स्टोरेज के बुनियादी सूत्र](#क्षमता-थ्रूपुट-और-स्टोरेज-के-बुनियादी-सूत्र)")
    a("3. [🧱 डिस्ट्रीब्यूटेड सिस्टम्स के बुनियादी स्तंभ (Core Distributed Architecture Primitives)](#-डिस्ट्रीब्यूटेड-सिस्टम्स-के-बुनियादी-स्तंभ)")
    a("   - [CAP प्रमेय और PACELC प्रमेय का व्यावहारिक विश्लेषण](#cap-प्रमेय-और-pacelc-प्रमेय)")
    a("   - [डेटाबेस चयन मार्गदर्शिका (RDBMS vs NoSQL vs NewSQL vs TSDB)](#डेटाबेस-चयन-मार्गदर्शिका)")
    a("   - [कैशिंग रणनीतियाँ एवं निष्कासन नीतियां (Caching Strategies & Eviction Policies)](#कैशिंग-रणनीतियाँ-एवं-निष्कासन-नीतियां)")
    a("   - [लोड बैलेंसिंग एवं रिवर्स प्रॉक्सी (Layer 4 vs Layer 7)](#लोड-बैलेंसिंग-एवं-रिवर्स-प्रॉक्सी)")
    a("   - [डेटाबेस शार्डिंग एवं रेप्लिकेशन (Sharding & Replication)](#डेटाबेस-शार्डिंग-एवं-रेप्लिकेशन)")
    a("   - [माइक्रोसर्विस रेजिलिएंस: सर्किट ब्रेकर, सागा एवं आउटबॉक्स पैटर्न](#माइक्रोसर्विस-रेजिलिएंस-पैटर्न्स)")
    a("   - [डिस्ट्रीब्यूटेड कॉन्सेन्सस एवं लीडर इलेक्शन (Raft vs Paxos vs Zab)](#डिस्ट्रीब्यूटेड-कॉन्सेन्सस-एवं-लीडर-इलेक्शन)")
    a("   - [डेटाबेस इंडेक्सिंग की आंतरिक कार्यप्रणाली (B+ Tree, LSM-Tree, Inverted Index)](#डेटाबेस-इंडेक्सिंग-की-आंतरिक-कार्यप्रणाली)")
    a("4. [📚 सभी 28 अध्यायों का गहन एवं विस्तृत तकनीकी विश्लेषण (All 28 Chapters Deep Dive)](#-सभी-28-अध्यायों-का-गहन-एवं-विस्तृत-तकनीकी-विश्लेषण)")
    for i in range(1, 29):
        a(f"   - [Ch {i:02d}: विस्तृत आर्किटेक्चर विश्लेषण](#ch-{i:02d})")
    a("5. [🎮 लाइव इंटरएक्टिव सिम्युलेटर्स गाइड (Interactive Simulators & Localhost)](#-लाइव-इंटरएक्टिव-सिम्युलेटर्स-गाइड)")
    a("6. [📖 संदर्भ एवं इंजीनियरिंग ब्लॉग्स (Curated Engineering Resources)](#-संदर्भ-एवं-इंजीनियरिंग-ब्लॉग्स)")
    a()
    a("---")
    a()

    # 3. Framework
    a("## 🚀 सिस्टम डिज़ाइन का दर्शन एवं 4-चरणीय इंटरव्यू फ्रेमवर्क")
    a()
    a("सिस्टम डिज़ाइन इंटरव्यू किसी भी तकनीकी कंपनी (Google, Meta, Amazon, Microsoft, Uber, Netflix) में केवल यह जांचने के लिए नहीं होता कि आपको तकनीकों के नाम पता हैं या नहीं, बल्कि यह परखा जाता है कि आप बड़े पैमाने पर अनिश्चितता (Ambiguity) को कैसे संरचना में बदलते हैं और तकनीकी समझौते (Trade-offs) कैसे लेते हैं।")
    a()
    a("### 4-चरणीय समय प्रबंधन")
    a()
    a("```")
    a("+--------------------------------------------------------------------------------+")
    a("| चरण 1: समस्या को समझना और डिज़ाइन का दायरा तय करना (Scope & Clarifications)   |")
    a("| समय: 00 से 05 मिनट | लक्ष्य: Functional/Non-Functional आवश्यकताएं, DAU, SLAs    |")
    a("+--------------------------------------------------------------------------------+")
    a("                                        |")
    a("                                        v")
    a("+--------------------------------------------------------------------------------+")
    a("| चरण 2: हाई-लेवल डिज़ाइन प्रस्तावित करना और सहमति पाना (High-Level Architecture) |")
    a("| समय: 05 से 15 मिनट | लक्ष्य: REST APIs, Core Components, DB Entities, Data Flow|")
    a("+--------------------------------------------------------------------------------+")
    a("                                        |")
    a("                                        v")
    a("+--------------------------------------------------------------------------------+")
    a("| चरण 3: महत्वपूर्ण घटकों का डीप-डाइव (Deep Dive into Core Bottlenecks)           |")
    a("| समय: 15 से 35 मिनट | लक्ष्य: Sharding, Caching, Concurrency, Failure Scenarios|")
    a("+--------------------------------------------------------------------------------+")
    a("                                        |")
    a("                                        v")
    a("+--------------------------------------------------------------------------------+")
    a("| चरण 4: रैप-अप, निष्कर्ष और भविष्य की स्केलिंग (Wrap-Up & Observability)         |")
    a("| समय: 35 से 45 मिनट | लक्ष्य: SPOF, Metrics, Tracing, Failover, Trade-offs     |")
    a("+--------------------------------------------------------------------------------+")
    a("```")
    a()
    a("### लाइव मॉक इंटरव्यू संवाद")
    a()
    a("नीचे एक आदर्श इंटरव्यू संवाद का उदाहरण दिया गया है जिससे समझ आता है कि सीनियर इंजीनियर इंटरव्यूअर से कैसे संवाद करते हैं:")
    a()
    a("> **उम्मीदवार (Candidate):** *\"क्या हम केवल URL छोटा करने और रीडायरेक्ट करने की कोर फंक्शनैलिटी पर ध्यान दें, या एनालिटिक्स (क्लिक काउंट, यूजर लोकेशन) भी इस स्कोप में शामिल है?\"*")
    a("> ")
    a("> **इंटरव्यूअर (Interviewer):** *\"मुख्य रूप से छोटा URL जनरेट करना और रीडायरेक्ट करना प्राथमिक है, किंतु एनालिटिक्स के लिए क्लिक ट्रैकिंग का प्रावधान भी होना चाहिए।\"*")
    a("> ")
    a("> **उम्मीदवार:** *\"सिस्टम का स्केल क्या मानकर चलें? कितने डेली एक्टिव यूजर्स और प्रति सेकंड कितने नए URLs जनरेट होंगे?\"*")
    a("> ")
    a("> **इंटरव्यूअर:** *\"प्रति दिन 100 मिलियन नए URLs जनरेट होते हैं और रीड-टू-राइट अनुपात 100:1 है।\"*")
    a("> ")
    a("> **उम्मीदवार:** *\"बहुत बढ़िया। इसका मतलब राइट QPS लगभग 1,160 और रीड QPS 116,000 होगा। यह भारी Read-Heavy सिस्टम है, इसलिए हमें एक आक्रामक कैशिंग लेयर (Redis LRU Cache) और Base62 एन्कोडिंग के साथ Snowflake 64-bit ID जनरेशन चुनना चाहिए ताकि कोलिजन-मुक्त O(1) कन्वर्जन मिल सके। क्या हम इस हाई-लेवल डिज़ाइन पर आगे बढ़ें?\"*")
    a("> ")
    a("> **इंटरव्यूअर:** *\"बिल्कुल सही दिशा है, कृपया आगे बढ़ें।\"*")
    a()
    a("---")
    a()

    # 4. Numbers Cheat Sheet
    a("## 📐 इंटरव्यू में काम आने वाले Numbers (Back-of-the-envelope Cheat Sheet)")
    a()
    a("### Jeff Dean के हार्डवेयर एवं नेटवर्क लेटेंसी आंकड़े")
    a()
    a("| हार्डवेयर / नेटवर्क ऑपरेशन | लेटेंसी (Time) | मानव पैमाना (Scaled: 1ns = 1 sec) | इंजीनियरिंग महत्व |")
    a("|---|---|---|---|")
    a("| **L1 CPU Cache Reference** | 0.5 ns | 0.5 सेकंड | अत्यधिक तेज़ सीपीयू रजिस्टर्स |")
    a("| **Branch Mispredict** | 5 ns | 5 सेकंड | पाइपलाइन इनवैलिडेशन |")
    a("| **L2 CPU Cache Reference** | 7 ns | 7 सेकंड | L1 से 14x धीमा |")
    a("| **Mutex Lock/Unlock** | 25 ns | 25 सेकंड | थ्रेड सिंक्रोनाइज़ेशन ओवरहेड |")
    a("| **Main Memory (RAM) Access** | 100 ns | 1.6 मिनट | कैश मिस होने पर मुख्य मेमोरी जुर्माना |")
    a("| **1 MB सीक्वेंशियल रीड (RAM)** | 250,000 ns (250 µs) | 2.9 दिन | रैम में सीक्वेंशियल डेटा ट्रांसफर अत्यंत तीव्र |")
    a("| **SSD Random Read (NVMe)** | 16,000 ns (16 µs) | 4.4 घंटे | रैम से लगभग 160x धीमा |")
    a("| **1 MB सीक्वेंशियल रीड (NVMe SSD)** | 1,000,000 ns (1 ms) | 11.5 दिन | सीक्वेंशियल SSD राइट/रीड बहुत प्रभावी |")
    a("| **समान डेटासेंटर में राउंड ट्रिप (RTT)** | 500,000 ns (0.5 ms) | 5.8 दिन | इंट्रा-डेटासेंटर RPC ओवरहेड |")
    a("| **HDD Random Disk Seek** | 10,000,000 ns (10 ms) | 3.8 महीने | मैकेनिकल हेड मूवमेंट की भारी लेटेंसी |")
    a("| **1 MB सीक्वेंशियल रीड (HDD)** | 20,000,000 ns (20 ms) | 7.6 महीने | रैंडम सीक से 50x बेहतर |")
    a("| **सैन फ्रांसिस्को से लंदन नेटवर्क RTT** | 150,000,000 ns (150 ms) | 4.7 साल | प्रकाश की गति की भौतिक सीमा |")
    a()
    a("### Availability SLA और वार्षिक डाउनटाइम तालिका")
    a()
    a("| उपलब्धता (Availability SLA) | डाउनटाइम प्रति वर्ष (Downtime/Year) | डाउनटाइम प्रति माह (Downtime/Month) | डाउनटाइम प्रति दिन (Downtime/Day) |")
    a("|---|---|---|---|")
    a("| **99.0% (Two 9s)** | 3.65 दिन | 7.20 घंटे | 14.40 मिनट |")
    a("| **99.9% (Three 9s)** | 8.76 घंटे | 43.80 मिनट | 1.44 मिनट |")
    a("| **99.99% (Four 9s - उद्योग मानक)** | 52.56 मिनट | 4.38 मिनट | 8.64 सेकंड |")
    a("| **99.999% (Five 9s - टेलीकॉम/बैंकिंग)** | 5.26 मिनट | 25.90 सेकंड | 0.86 सेकंड |")
    a("| **99.9999% (Six 9s)** | 31.56 सेकंड | 2.59 सेकंड | 0.086 सेकंड |")
    a()
    a("### क्षमता, थ्रूपुट और स्टोरेज के बुनियादी सूत्र")
    a("- **थ्रूपुट सूत्र (QPS):** $\\text{QPS} = \\frac{\\text{दैनिक कुल रिक्वेस्ट्स}}{86,400 \\text{ सेकंड}} \\approx \\frac{\\text{दैनिक रिक्वेस्ट्स}}{100,000}$")
    a("- **पीक थ्रूपुट:** $\\text{Peak QPS} = \\text{Average QPS} \\times 2$ (त्योहारों अथवा सेल्स में $\\times 5$)")
    a("- **80/20 नियम (Pareto Rule):** 20% लोकप्रिय डेटा 80% ट्रैफिक को आकर्षित करता है। रैम कैश में केवल 20% हॉट डेटा रखना 80% हिट रेशियो सुनिश्चित करता है।")
    a("- **स्टोरेज 5 वर्ष:** $\\text{Storage (5 Years)} = \\text{Write QPS} \\times \\text{Request Size (Bytes)} \\times 86,400 \\times 365 \\times 5$")
    a()
    a("---")
    a()

    # 5. Core Distributed Primitives
    a("## 🧱 डिस्ट्रीब्यूटेड सिस्टम्स के बुनियादी स्तंभ")
    a()
    a("### CAP प्रमेय और PACELC प्रमेय")
    a("- **CAP Theorem:** किसी भी डिस्ट्रीब्यूटेड डेटा सिस्टम में जब नेटवर्क पार्टीशन ('P') होता है, तो सिस्टम को **Consistency ('C')** और **Availability ('A')** में से किसी एक को चुनना पड़ता है।")
    a("  - **CP Systems:** डेटा की शुद्धता हेतु राइट्स ब्लॉक कर देना (उदा: Google Spanner, HBase, ZooKeeper)।")
    a("  - **AP Systems:** उच्च उपलब्धता हेतु संभावित पुराना डेटा सर्व करना (उदा: Cassandra, DynamoDB, CouchDB)।")
    a("- **PACELC Theorem:** सामान्य दिनों में (Else 'E') सिस्टम **Latency ('L')** और **Consistency ('C')** के बीच चुनाव करता है। (उदा: DynamoDB PA/EL है)।")
    a()
    a("### डेटाबेस चयन मार्गदर्शिका")
    a()
    a("| श्रेणी | डेटाबेस उदाहरण | श्रेष्ठ उपयोगिता (Best Used For) | मुख्य सीमाएँ (Trade-offs) |")
    a("|---|---|---|---|")
    a("| **Relational (RDBMS)** | PostgreSQL, MySQL | जटिल रिलेशंस, फॉरेन कीज, ACID ट्रांजैक्शन्स, वित्तीय डेटा | हॉरिजॉन्टल राइट शार्डिंग अत्यंत जटिल |")
    a("| **Key-Value Store** | Redis, DynamoDB, Memcached | यूजर सेशन्स, टोकन बकेट, कैशे, तेज़ $O(1)$ रीड/राइट | सीमित क्वेरी क्षमता, केवल की पर आधारित लुकअप |")
    a("| **Wide-Column NoSQL** | Cassandra, ScyllaDB, Bigtable | विशाल टाइम-सीरीज़ डेटा, चैट हिस्ट्री, पेटाबाइट स्केल राइट्स | जटिल जॉइन्स का पूर्ण अभाव, डेटा डुप्लिकेशन |")
    a("| **Document NoSQL** | MongoDB, Couchbase | लचीला स्कीमा, ई-कॉमर्स कैटलॉग, नेस्टेड JSON | मल्टी-डॉक्यूमेंट ACID ट्रांजैक्शन्स में लेटेंसी |")
    a("| **Search Engine** | Elasticsearch, OpenSearch | फुल-टेक्स्ट सर्च, फजी सर्च, लॉग एनालिटिक्स | प्राइमरी सोर्स ऑफ ट्रुथ के रूप में अविश्वसनीय |")
    a("| **Time-Series (TSDB)** | Prometheus, InfluxDB, TimescaleDB | सर्वर मेट्रिक्स, IoT सेंसर डेटा, फाइनेंशियल टिक डेटा | रैंडम अपडेट्स और डिलीट्स बहुत धीमे |")
    a("| **Object Storage** | Amazon S3, MinIO, GCS | इमेजेस, वीडियोज, बैकअप्स, बड़े अनस्ट्रक्चर्ड ब्लॉक्स | अपेंड/मॉडिफाई नहीं किया जा सकता (Immutable) |")
    a()
    a("### कैशिंग रणनीतियाँ एवं निष्कासन नीतियां")
    a("1. **Cache-Aside (Lazy Loading):** ऐप पहले कैश चेक करता है; मिस होने पर डीबी से पढ़कर कैश भरता है।")
    a("2. **Read-Through:** ऐप केवल कैश से बात करता है; कैश प्रोवाइडर स्वयं डीबी से फेच करता है।")
    a("3. **Write-Through:** डेटा पहले कैश में और उसी ट्रांजैक्शन में डीबी में लिखा जाता है।")
    a("4. **Write-Behind (Write-Back):** डेटा कैश में $O(1)$ में लिखा जाता है और बैकग्राउंड में असिंक्रोनस बैच में डीबी में फ्लश होता है।")
    a("5. **निष्कासन नीतियां (Eviction Policies):** **LRU** (Least Recently Used), **LFU** (Least Frequently Used), **FIFO**।")
    a()
    a("### लोड बैलेंसिंग एवं रिवर्स प्रॉक्सी")
    a("- **Layer 4 (Transport Layer):** IP और TCP/UDP पोर्ट के आधार पर पैकेट रूटिंग (उदा: AWS NLB, HAProxy TCP मोड)। अल्ट्रा-हाई थ्रूपुट, कम CPU ओवरहेड।")
    a("- **Layer 7 (Application Layer):** HTTP हेडर, कुकीज, URL पाथ के आधार पर रूटिंग (उदा: Nginx, Envoy, AWS ALB)। SSL Termination और स्मार्ट रूटिंग सक्षम।")
    a("- **एल्गोरिदम:** Round Robin, Weighted Round Robin, Least Connections, IP Hash (Session Affinity)।")
    a()
    a("### डेटाबेस शार्डिंग एवं रेप्लिकेशन")
    a("- **शार्डिंग रणनीतियाँ:** Range-based Sharding (उदा: 1-1000 ID), Hash-based Sharding (`hash(key) % N`), Directory-based Sharding।")
    a("- **शार्डिंग की चुनौतियाँ:** Cross-shard Joins, Re-sharding Overhead, Hotspot Celebrity Key (उदा: एक ही शार्ड पर अत्यधिक ट्रैफिक आना)।")
    a()
    a("### माइक्रोसर्विस रेजिलिएंस पैटर्न्स")
    a("- **सर्किट ब्रेकर (Circuit Breaker - Hystrix/Resilience4j):** जब कोई डाउनस्ट्रीम सर्विस फेल होने लगे, तो थ्रेड्स को ब्लॉक होने से बचाने के लिए कॉल्स को तुरंत 'Open' स्टेट में डालकर `Fallback` रिटर्न करना।")
    a("- **सागा पैटर्न (Saga Pattern):** डिस्ट्रीब्यूटेड ट्रांजैक्शन्स के लिए Choreography vs Orchestration आधारित स्थानीय ट्रांजैक्शन्स और विफलता पर Compensating Transactions (रिवर्सल) चलाना।")
    a("- **Transactional Outbox Pattern & CDC:** ड्यूल-राइट विसंगतियों से बचने के लिए उसी डेटाबेस ट्रांजैक्शन में `OUTBOX` टेबल में लिखना और Debezium द्वारा Kafka में पब्लिश करना।")
    a()
    a("### डिस्ट्रीब्यूटेड कॉन्सेन्सस एवं लीडर इलेक्शन")
    a("- **Raft Consensus:** लीडर इलेक्शन (Heartbeats & Election Timeouts), लॉग रेप्लिकेशन, और मेजॉरिटी कोरम ($N/2 + 1$) द्वारा विभाजित नेटवर्क (Split-Brain) से सुरक्षा।")
    a("- **Paxos & Zab:** ZooKeeper (Zab) और Chubby (Paxos) द्वारा डिस्ट्रीब्यूटेड लॉकिंग और कॉन्फ़िगरेशन मैनेजमेंट।")
    a()
    a("### डेटाबेस इंडेक्सिंग की आंतरिक कार्यप्रणाली")
    a("| इंडेक्स प्रकार | आंतरिक संरचना (Data Structure) | श्रेष्ठ उपयोग (Best For) | समय जटिलता (Complexity) |")
    a("|---|---|---|---|")
    a("| **B+ Tree Index** | N-ary balanced tree (Leaf nodes linked) | रेंज क्वेरीज़ (`BETWEEN`), सॉर्टिंग, समानता | $O(\\log N)$ रीड, $O(\\log N)$ राइट |")
    a("| **LSM-Tree Index** | MemTable (SkipList) + SSTables on disk | भारी राइट्स (Write-Heavy), टाइम-सीरीज़ | $O(1)$ राइट, $O(\\log N)$ रीड |")
    a("| **Hash Index** | Hash Table (Buckets) | केवल सटीक समानता (`WHERE id = 'xyz'`) | $O(1)$ औसत रीड/राइट |")
    a("| **Inverted Index** | Posting Lists (Term -> Doc IDs) | फुल-टेक्स्ट सर्च, फजी सर्च, कीवर्ड लुकअप | $O(1)$ टर्म लुकअप |")
    a()
    a("---")
    a()

    # 6. Detailed 28 Chapters Deep Dive
    a("## 📚 सभी 28 अध्यायों का गहन एवं विस्तृत तकनीकी विश्लेषण")
    a()

    # List of tuples: (ch_num, title_en, title_hi, scope, high_level, deep_dive, trade_offs)
    chapters_data = [
        (
            "01",
            "Scale From Zero To Millions Of Users",
            "Zero से Millions तक Scaling",
            "सिस्टम को 1 यूज़र से 10 मिलियन यूज़र्स तक स्केल करना। लक्ष्य: हाई अवेलेबिलिटी, लो लेटेंसी, और कोई सिंगल प्वाइंट ऑफ फेलियर (SPOF) न होना।",
            """- **DNS & CDN:** यूजर रिक्वेस्ट DNS से आईपी पाती है; स्टैटिक एसेट्स (इमेजेस, जेएस, सीएसएस) Cloudflare CDN से सर्व होते हैं।
- **Load Balancer & Stateless Web Tier:** Nginx / ALB के पीछे मल्टीपल वेब सर्वर्स रन करते हैं। यूजर सेशन्स को लोकल मेमोरी के बजाय Redis Session Store में रखा जाता है।
- **Database Master-Slave:** MySQL/PostgreSQL Primary पर Writes और 3 Read Replicas पर Reads।
- **Async Workers & Queues:** भारी टास्क (ईमेल, इमेज रीसाइजिंग) को Kafka/RabbitMQ कतार में भेजना।""",
            """- **Replication Lag Management:** जब मास्टर से स्लेव पर डेटा सिंक होने में 300ms लगते हैं, तो यूजर प्रोफाइल अपडेट करने के तुरंत बाद 5 सेकंड तक रीड्स को सीधे Master DB से सर्व करना।
- **Cache Stampede Prevention:** जब कोई हॉट की एक्सपायर होती है, तो 10,000 रिक्वेस्ट्स एक साथ डीबी पर न जाएं, इसके लिए Redis Mutex Lock (SETNX) या Probabilistic Early Expiration (XFetch) का उपयोग।
- **Database Sharding:** यूजर आईडी के हैश पर डेटा को शार्ड करना (`user_id % num_shards`)।""",
            "वर्टिकल स्केलिंग (Scale-up) की सख्त हार्डवेयर सीमाएं होती हैं और यह SPOF है। हॉरिजॉन्टल स्केलिंग (Scale-out) शुरुआत में जटिल लगती है किंतु लॉन्ग-टर्म में अत्यधिक लचीली और लागत-प्रभावी होती है।"
        ),
        (
            "02",
            "Back-of-the-envelope Estimation",
            "Back-of-the-envelope गणना का विज्ञान",
            "सिस्टम आर्किटेक्चर तय करने से पहले थ्रूपुट (QPS), नेटवर्क बैंडविड्थ, स्टोरेज कैपेसिटी और रैम साइज का सटीक अनुमान लगाना।",
            """- **केस स्टडी: Twitter-like Platform (300M DAU, Read:Write = 100:1):**
  - दैनिक ट्वीट्स: $300\\text{M} \\times 2 = 600,000,000$ ट्वीट्स/दिन।
  - Write QPS: $\\frac{600\\text{M}}{86,400} \\approx 7,000 \\text{ QPS}$ (Peak: 14,000 QPS)।
  - Read QPS: $7,000 \\times 100 = 700,000 \\text{ QPS}$ (Peak: 1.4 Million QPS)।""",
            """- **स्टोरेज गणना:** प्रति ट्वीट 300 Bytes टेक्स्ट + 20% ट्वीट्स में 1 MB मीडिया।
  - मीडिया स्टोरेज: $600\\text{M} \\times 0.2 \\times 1\\text{ MB} = 120\\text{ TB/दिन}$।
  - 5 साल का स्टोरेज $\\approx 120\\text{ TB} \\times 365 \\times 5 \\approx 219\\text{ PB}$।
- **रैम कैशिंग (80/20 नियम):** 20% हॉट ट्वीट्स 80% रीड्स लाते हैं। 1 दिन के हॉट ट्वीट्स हेतु:
  $$\\text{RAM} = 600\\text{M} \\times 0.2 \\times 300 \\text{ Bytes} = 36 \\text{ GB RAM}$$ (3x रेप्लिकेशन के साथ ~108 GB RAM)।""",
            "सटीक कैलकुलेटर की जरूरत नहीं होती; इंटरव्यूअर राउंड नंबर्स ($10^5$ सेकंड/दिन) के साथ तार्किक सोच और परिमाण के क्रम (Order of Magnitude) को देखता है।"
        ),
        (
            "03",
            "System Design Framework",
            "सिस्टम डिज़ाइन इंटरव्यू फ्रेमवर्क",
            "45 मिनट के सीमित समय में जटिल आर्किटेक्चरल समस्याओं को संरचित, स्पष्ट और सहयोगात्मक तरीके से हल करना।",
            """- **4-चरणीय समय आवंटन:**
  - चरण 1 (00-05 min): Scope & Requirements (DAU, Features, Read/Write Ratio, SLAs)।
  - चरण 2 (05-15 min): High-Level Design (APIs, Data Flow, High-level Diagram, Core DB)।
  - चरण 3 (15-35 min): Deep Dive (Bottlenecks, Partitioning, Concurrency, Caching)।
  - चरण 4 (35-45 min): Wrap-up (SPOF, Metrics, Tracing, Failure Scenarios)।""",
            """- **इंटरव्यूअर के साथ साइलेंट न रहें:** 'Think out loud' नीति अपनाएं। हर निर्णय के पीछे का कारण समझाएं।
- **ट्रेड-ऑफ्स स्पष्ट करें:** कभी यह न कहें कि 'यह सर्वश्रेष्ठ समाधान है'। कहें: *'यह लेटेंसी को 5ms तक घटाता है, किंतु इसके लिए हमें अतिरिक्त Redis मेमोरी का खर्च उठाना होगा।'*""",
            "बिना आवश्यकताएं स्पष्ट किए सीधे कोड या बॉक्स बनाना शुरू करना सबसे बड़ी गलती मानी जाती है। पहले स्कोप को लॉक करें।"
        ),
        (
            "04",
            "Rate Limiter",
            "Rate Limiter (दर नियंत्रक आर्किटेक्चर)",
            "APIs को DoS/DDoS हमलों, बॉट्स और अत्यधिक ट्रैफिक से बचाने हेतु प्रति यूजर/IP रिक्वेस्ट्स को सीमित करना।",
            """- **क्लाइंट -> API Gateway (Rate Limiter Middleware) -> Backend Services:**
- **Redis Cache:** यूजर टोकन बकेट स्टेट को स्टोर करने के लिए इन-मेमोरी की-वैल्यू स्टोर।
- **HTTP रिस्पॉन्स:** अनुमति मिलने पर 200 OK; सीमा समाप्त होने पर HTTP 429 Too Many Requests।""",
            """- **5 प्रमुख एल्गोरिदम:** Token Bucket (सर्वश्रेष्ठ बर्स्ट हैंडलिंग), Leaky Bucket (स्थिर दर), Fixed Window, Sliding Window Log, Sliding Window Counter।
- **Race Condition समाधान:** जब 2 नोड्स एक साथ काउंटर पढ़ते हैं, तो **Redis Lua Scripting** द्वारा एटॉमिक रूप से चेक और टोकन डिडक्ट करना।
- **HTTP हेडर्स:** `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, `X-Ratelimit-Retry-After`।""",
            "क्लाइंट-साइड रेट लिमिटिंग अविश्वसनीय होती है क्योंकि इसे आसानी से बाईपास किया जा सकता है। सर्वर-साइड API Gateway पर रेट लिमिटिंग अनिवार्य है।"
        ),
        (
            "05",
            "Consistent Hashing",
            "Consistent Hashing (कंसिस्टेंट हैशिंग रिंग)",
            "डेटा और रिक्वेस्ट्स को सर्वर्स के क्लस्टर में न्यूनतम री-डिस्ट्रीब्यूशन और बिना कैशे चर्न के समान रूप से बांटना।",
            """- **0 से $2^{32}-1$ की हैश रिंग (SHA-1):** सर्वर्स और कीज़ दोनों को रिंग पर मैप किया जाता है।
- **Clockwise Traversal:** किसी की के लिए रिंग में आगे घड़ी की दिशा में जो पहला सर्वर मिलता है, वह उसका मालिक होता है।""",
            """- **Rehash समस्या का उन्मूलन:** पारंपरिक $k \\pmod n$ में सर्वर बदलते ही 99% कीज़ बदल जाती हैं। Consistent Hashing में केवल $k/n$ कीज़ री-डिस्ट्रीब्यूट होती हैं।
- **वर्चुअल नोड्स (Vnodes):** भौतिक सर्वर को 100-300 आभासी नोड्स में बांटकर रिंग पर बिखेरना, जिससे डेटा का फैलाव 99% समान रूप से संतुलित हो जाता है।""",
            "वर्चुअल नोड्स की संख्या बढ़ाने से मेमोरी और रिंग मैनेजमेंट ओवरहेड बढ़ता है, किंतु डेटा का फैलाव अत्यधिक समान हो जाता है। 150-250 Vnodes आदर्श संतुलन है।"
        ),
        (
            "06",
            "Key-Value Store",
            "Distributed Key-Value Store (DynamoDB / Cassandra)",
            "पेटाबाइट-स्केल पर अत्यधिक उच्च उपलब्धता, स्केलेबिलिटी और सब-10ms लेटेंसी वाला की-वैल्यू स्टोर बनाना।",
            """- **क्लाइंट -> Coordinator Node -> Storage Nodes:**
- **डेटा पार्टीशनिंग:** Consistent Hashing with Vnodes।
- **डेटा रेप्लिकेशन:** रिंग पर घड़ी की दिशा में पहले $N$ अद्वितीय भौतिक नोड्स पर डेटा कॉपी करना।""",
            """- **Tunable Quorum:** $N$ रेप्लिका, $W$ राइट्स, $R$ रीड्स। $W + R > N$ होने पर Strong Consistency।
- **LSM-Tree Internals:** Write-Ahead Log (WAL) -> MemTable (SkipList) -> SSTables on disk -> Bloom Filter -> Compaction।
- **Vector Clocks:** समवर्ती राइट्स में कारणता (Causality) और डेटा कॉन्फ्लिक्ट्स ट्रैक करना।
- **Gossip Protocol:** नोड्स के बीच क्लस्टर स्टेट और नोड फेलियर डिटेक्ट करने के लिए पीयर-टू-पीयर कम्युनिकेशन्स।""",
            "B+ Tree इन-प्लेस अपडेट्स करता है जिससे रैंडम राइट्स धीमे होते हैं। LSM-Tree सीक्वेंशियल राइट्स करता है जो राइट-इंटेंसिव सिस्टम्स के लिए 10x तेज़ है।"
        ),
        (
            "07",
            "Unique-Id Generator",
            "Distributed Unique ID Generator (Twitter Snowflake)",
            "डिस्ट्रीब्यूटेड सिस्टम में प्रति सेकंड लाखों 64-बिट समय-क्रमबद्ध (Time-sortable) अद्वितीय आईडी जनरेट करना।",
            """- **Twitter Snowflake 64-bit Structure:**
  - 1 bit Sign (0)
  - 41 bits Timestamp (मिलीसेकंड, ~69 वर्ष Epoch)
  - 5 bits Datacenter ID (32 डेटासेंटर्स)
  - 5 bits Worker ID (32 वर्कर नोड्स)
  - 12 bits Sequence Number (4,096 IDs प्रति मिलीसेकंड प्रति वर्कर)""",
            """- **क्षमता:** प्रति वर्कर प्रति सेकंड $4,096 \\times 1,000 = 4.09 \\text{ Million IDs}$।
- **NTP Clock Drift Handling:** यदि सर्वर की घड़ी पीछे चली जाए, तो क्लॉक कैच-अप होने तक वेट करें अथवा अपवाद (Exception) फेंकें ताकि डुप्लिकेट आईडी न बने।
- **UUID से श्रेष्ठता:** UUID (128-bit) आकार में दोगुना है और रैंडम होने के कारण B+ Tree इंडेक्स में भारी पेज स्प्लिट्स पैदा करता है। Snowflake 64-bit पूरी तरह सॉर्टेड है।""",
            "सेंट्रलाइज़्ड टिकट सर्वर SPOF बन जाता है। Snowflake पूरी तरह विकेंद्रीकृत (Decentralized) और कोऑर्डिनेशन-मुक्त है।"
        ),
        (
            "08",
            "URL Shortener",
            "High-Scale URL Shortener (TinyURL)",
            "लंबे URLs को छोटे 7-कैरेक्टर लिंक्स में बदलना और 100k+ QPS पर सब-5ms लेटेंसी के साथ रीडायरेक्ट करना।",
            """- **राइट फ्लो:** Client -> API Gateway -> Shortening Service -> Snowflake ID Generator -> Base62 Converter -> DB / Cache।
- **रीड फ्लो:** Client -> CDN/Edge -> Reverse Proxy -> Redis LRU Cache (80% Hits) -> DB (20% Misses) -> HTTP 302 Redirect।""",
            """- **Base62 vs Hash Collisions:** MD5 हैश के पहले 7 कैरेक्टर लेने पर कोलिजन होते हैं। Snowflake 64-bit ID को Base62 ($[0-9, a-z, A-Z]$, $62^7 \\approx 3.5 \\text{ ट्रिलियन}$) में बदलना 100% कोलिजन-मुक्त और $O(1)$ है।
- **HTTP 301 vs 302:** 301 ब्राउज़र कैश करता है जिससे सर्वर लोड घटता है किंतु एनालिटिक्स मिस हो जाता है। 302 सर्वर के जरिए रीडायरेक्ट करता है जिससे क्लिक एनालिटिक्स ट्रैक होता है।
- **Bloom Filter:** गैर-मौजूद फर्जी शॉर्ट कोड्स के डेटाबेस लुकअप को 0ms में ब्लॉक करना।""",
            "डेटा कभी एक्सपायर न होने पर डेटाबेस विशाल हो जाएगा। अतः अनयूज्ड लिंक्स के लिए 2 वर्ष का TTL और कोल्ड स्टोरेज आर्काइवल नीति रखना आवश्यक है।"
        ),
        (
            "09",
            "Web Crawler",
            "Distributed Web Crawler (इंटरनेट स्केल वेब क्रॉलर)",
            "सर्च इंजन इंडेक्सिंग हेतु 10 बिलियन से अधिक वेब पेजेस को शिष्टता (Politeness) और गति से डाउनलोड करना।",
            """- **URL Frontier -> DNS Resolver -> HTML Downloader -> Content Parser -> Duplicate Detector -> Storage / Search Index।**""",
            """- **Politeness:** एक ही डोमेन को बार-बार हिट न करें; होस्ट-वाइज़ कतारें और डिले टाइमर।
- **Priority:** PageRank आधारित कतारें ताकि महत्वपूर्ण पेजेस पहले क्रॉल हों।
- **SimHash / Fingerprinting:** 64-बिट फिंगरप्रिंट द्वारा डुप्लिकेट और नियर-डुप्लिकेट पेजेस को हैमिंग डिस्टेंस $\\le 3$ से पहचानना।
- **Headless Chrome (Puppeteer):** जावास्क्रिप्ट-हैवी SPAs को रेंडर करके डायनामिक लिंक्स निकालना।""",
            "क्रॉलर स्पाइडर ट्रैप्स (अनंत लूप वाली डायनामिक URLs) में फंस सकता है। अधिकतम पाथ डेप्थ और URL लेंथ लिमिट लगाकर इससे बचा जाता है।"
        ),
        (
            "10",
            "Notification System",
            "Distributed Notification System (पुश, एसएमएस, ईमेल)",
            "करोड़ों उपयोगकर्ताओं को रीयल-टाइम में मल्टी-चैनल (iOS, Android, SMS, Email) नोटिफिकेशन्स डिलीवर करना।",
            """- **Services -> Notification API Gateway -> Validator / Rate Limiter -> Message Queues (Kafka) -> Notification Workers -> Third-party Gateways (APNs, FCM, Twilio, SendGrid)।**""",
            """- **Deduplication:** `user_id + event_type + timestamp` का Redis में 24h TTL के साथ डिडुप की बनाना ताकि पेमेंट या अलर्ट 2 बार न जाए।
- **Rate Limiting:** यूजर को स्पैम से बचाने के लिए प्रति घंटा 5 नोटिफिकेशन की सीमा।
- **Dead Letter Queue (DLQ):** 3 री-ट्राई के बाद फेल नोटिफिकेशन्स को DLQ में डालना ताकि एनालिसिस हो सके।""",
            "थर्ड पार्टी गेटवेज (APNs/Twilio) कभी-कभी लेटेंसी स्पाइक्स या डाउनटाइम का शिकार होते हैं। प्रत्येक चैनल के लिए अलग असिंक्रोनस कतार होना अनिवार्य है।"
        ),
        (
            "11",
            "News Feed System",
            "Real-time News Feed System (Facebook / Twitter Feed)",
            "करोड़ों यूज़र्स के लिए रियल-टाइम में उनके दोस्तों और पेजेस की पोस्ट्स से बनी व्यक्तिगत न्यूज़ फीड तैयार करना।",
            """- **Feed Publishing:** Post Service -> Fanout Service -> Message Queue -> Fanout Workers -> Redis ZSET Cache।
- **Feed Retrieval:** Client -> Feed Service -> Redis ZSET -> Post Service / Hydration -> Client।""",
            """- **Push vs Pull:** सामान्य यूज़र्स के लिए Fanout-on-write (Push) मॉडल ($O(1)$ रीड्स)।
- **The Celebrity Problem:** 100M फॉलोअर्स वाले सेलिब्रिटी के लिए Fanout-on-read (Pull) मॉडल, ताकि 100M राइट्स का विस्फोट न हो।
- **Redis Sorted Set (ZSET):** `key=user_feed:<id>`, `score=timestamp`, `value=post_id`। प्रति यूजर केवल हालिया 800 पोस्ट्स कैश करना।""",
            "हर पोस्ट का पूरा डेटा फीड में स्टोर करने से भारी रैम बर्बाद होगी। केवल `post_id` कैश करें और रेंडरिंग के समय पोस्ट मेटाडेटा हाइड्रेट करें।"
        ),
        (
            "12",
            "Chat System",
            "Real-time Chat System (WhatsApp / Slack / Discord)",
            "1-ऑन-1 और ग्रुप चैट्स में सब-100ms लेटेंसी के साथ अरबों मैसेजेस का रियल-टाइम आदान-प्रदान और सिंक।",
            """- **Web/Mobile Clients <---> WebSocket Connection Servers <---> Message Routing Service <---> NoSQL Storage (Cassandra)।**
- **Presence Servers:** यूजर ऑनलाइन/ऑफलाइन स्टेटस ट्रैक करने के लिए Redis Heartbeat।""",
            """- **WebSocket:** HTTP Polling के विपरीत निरंतर, द्विदिश (Full-Duplex) कनेक्शन।
- **मैसेज रिले:** Redis Pub/Sub क्लस्टर द्वारा अलग-अलग चैट सर्वर्स पर जुड़े यूज़र्स के बीच मैसेजेस रूट करना।
- **डेटाबेस:** भारी राइट्स और टाइम-सीरीज़ क्वेरीज़ के लिए **Apache Cassandra / ScyllaDB**।
- **मैसेज सीक्वेंसिंग:** Snowflake IDs द्वारा मैसेजेस का सही क्रम बनाए रखना।""",
            "WebSocket सर्वर्स स्टेटफुल होते हैं। अतः सर्वर क्रैश होने पर क्लाइंट्स को तुरंत दूसरे सर्वर से रिकनेक्ट करने के लिए स्मार्ट एक्सपोनेंशियल बैकऑफ चाहिए।"
        ),
        (
            "13",
            "Search Autocomplete",
            "Search Autocomplete System (गूगल सर्च ट्राय)",
            "यूजर द्वारा सर्च बॉक्स में टाइप करते ही सब-10ms में टॉप 5 सबसे लोकप्रिय सर्च कीवर्ड्स सुझाव में दिखाना।",
            """- **Data Collection:** Search Logs -> Kafka -> Flink Aggregator -> Aggregated DB।
- **Trie Service:** In-memory Sharded Trie Nodes -> Client Cache / CDN Cache।""",
            """- **Trie (Prefix Tree) संरचना:** प्रत्येक नोड एक कैरेक्टर रखता है।
- **$O(1)$ लुकअप:** प्रत्येक नोड पर उसके सब-ट्री के **Top 5 सर्वाधिक सर्च किए गए कीवर्ड्स और फ्रीक्वेंसी प्री-कंप्यूट करके स्टोर** करना।
- **ऑफ़लाइन अपडेट:** कीस्ट्रोक्स सीधे ट्राय म्यूटेट नहीं करते; दैनिक बैच जॉब नया ट्राय बनाकर मेमोरी में हॉट-स्वैप करता है।""",
            "अपवित्र या भड़काऊ शब्दों को ऑटो-कम्प्लीट से बाहर रखने के लिए ट्राय लुकअप के बाद एक तेज़ इन-मेमोरी फ़िल्टर लेयर होना अनिवार्य है।"
        ),
        (
            "14",
            "Youtube",
            "YouTube Video Streaming Platform",
            "लाखों वीडियो अपलोड्स को ट्रांसकोड करना और करोड़ों यूज़र्स को बिना बफरिंग के उच्च-गुणवत्ता वीडियो स्ट्रीम करना।",
            """- **Upload Flow:** Client -> Upload Service -> Blob Storage (Original) -> Transcoding Pipeline -> Blob Storage (Transcoded) -> CDN।
- **Streaming Flow:** Client -> Edge CDN -> HLS Player।""",
            """- **DAG Transcoding Scheduler:** वीडियो को छोटे 5-10s चंक्स में काटना और समानांतर में ट्रांसकोड करना।
- **Bitrate Ladders:** H.264/VP9/AV1 कोडेक्स में 1080p, 720p, 480p, 360p तैयार करना।
- **Adaptive Bitrate Streaming (HLS / MPEG-DASH):** यूजर की नेटवर्क स्पीड बदलते ही बिना बफरिंग क्वालिटी स्विच होना।""",
            "वीडियो फाइल्स विशाल होती हैं। यदि वे सीधे वेब सर्वर से होकर गुजरेंगी तो सर्वर्स क्रैश हो जाएंगे। क्लाइंट को Pre-signed S3 URLs देकर सीधे ब्लॉब स्टोर पर अपलोड कराएं।"
        ),
        (
            "15",
            "Google Drive",
            "Google Drive Cloud Storage (डेल्टा सिंक एवं ब्लॉब)",
            "फाइल्स का क्लाउड स्टोरेज, मल्टी-डिवाइस ऑटो-सिंक, वर्जन कंट्रोल और सुरक्षा।",
            """- **Clients (Desktop/Mobile) -> API Gateway -> Block Service & Metadata Service।**
- **Block Storage (S3):** डेटा ब्लॉक्स।
- **Metadata DB (PostgreSQL):** फाइल्स, वर्जन्स, परमिशन्स।""",
            """- **Block-level Chunking:** फाइल्स को 4 MB के चंक्स में तोड़ना।
- **Delta Sync:** केवल बदले हुए 4 MB ब्लॉक को अपलोड करना (नेटवर्क और बैंडविड्थ में 95% की बचत)।
- **Content-Addressable Storage (CAS):** ब्लॉक्स का नाम SHA-256 हैश पर रखना; ग्लोबल डिडुप्लिकेशन द्वारा डिस्क स्पेस बचाना।""",
            "जब दो यूजर एक ही समय एक ही फाइल एडिट करते हैं, तो दूसरे यूजर के लिए कॉन्फ्लिक्ट कॉपी (`file_conflicted.txt`) बनाई जाती है।"
        ),
        (
            "16",
            "Proximity Service",
            "Proximity Service (Yelp / Nearby Places)",
            "यूज़र की वर्तमान लोकेशन के आधार पर आसपास के 500 मीटर या 5 किमी के भीतर के रेस्टोरेंट्स/दुकानें खोजना।",
            """- **Client -> Load Balancer -> Proximity API -> Geospatial Index (Redis GEO / Geohash) -> Business DB (PostgreSQL) -> Client।**""",
            """- **Geohash (Base32):** दुनिया को 32 ग्रिड्स में बांटना। 6-कैरेक्टर जियोहैश $\\approx 1.2\\text{ km} \\times 0.6\\text{ km}$।
- **8 Neighboring Grids:** बाउंड्री प्रॉब्लम्स से बचने के लिए यूजर की सेल और चारों ओर की 8 पड़ोसी सेल्स को $O(1)$ में फेच करना।
- **Quadtree & Google S2:** इन-मेमोरी ट्री और हिल्बर्ट कर्व आधारित मैपिंग।""",
            "व्यवसायों की लोकेशन (स्थान) बहुत कम बदलती है किंतु रीड ट्रैफिक भारी होता है। जियोहैश लेयर को 100% Redis में कैश किया जा सकता है।"
        ),
        (
            "17",
            "Nearby Friends",
            "Nearby Friends (रियल-टाइम लोकेशन ब्रॉडकास्ट)",
            "आसपास मौजूद दोस्तों को रियल-टाइम में एक-दूसरे की लोकेशन दिखाना (उदा: Find My Friends)।",
            """- **Mobile App -> WebSocket Connection Servers -> Redis Pub/Sub Router -> Friends' WebSocket Connections।**""",
            """- **चुनौती:** 10M यूज़र्स हर 30 सेकंड में लोकेशन भेजते हैं $\\implies 330,000 \\text{ Writes/sec}$।
- **Geohash-based Pub/Sub:** दोस्तों के सभी चैनलों पर ब्रॉडकास्ट करने के बजाय जियोहैश सेल आधारित चैनल सब्सक्राइब करना; केवल संबंधित क्षेत्र में लोकेशन अपडेट्स भेजना।
- **TTL Cache:** वर्तमान लोकेशन को Redis में 10 मिनट के TTL के साथ स्टोर करना।""",
            "मोबाइल की बैटरी लाइफ बचाने के लिए जब यूजर स्थिर (Stationary) हो तो लोकेशन पिंग फ्रीक्वेंसी 30 सेकंड से बढ़ाकर 5 मिनट कर देनी चाहिए।"
        ),
        (
            "18",
            "Google Maps",
            "Google Maps & Route Planning",
            "वैश्विक स्तर पर मैप टाइल्स रेंडरिंग, सबसे तेज़ रूट खोजना और रियल-टाइम ट्रैफिक अपडेट्स।",
            """- **Tile Service (CDN Cache) -> Routing Service (A* / Contraction Hierarchies) -> Traffic Service (Kafka/Flink)।**""",
            """- **मैप टाइल्स:** पूरी दुनिया को 256x256 पिक्सेल की लाखों टाइल्स में प्री-कंप्यूट करना (Quadtree ज़ूम 0 से 21)।
- **Contraction Hierarchies (CH):** सड़क नेटवर्क ग्राफ के महत्वपूर्ण नोड्स को प्री-प्रोसेस करना, जिससे सब-सेकंड में हज़ारों मील का रूट निकल आता है।
- **ट्रैफिक इंटीग्रेशन:** जीपीएस स्पीड डेटा से ग्राफ एजेस के वेट्स को डायनामिकली अपडेट करना।""",
            "सादा Dijkstra बहुत धीमा है। प्रोडक्शन रूटिंग इंजन हमेशा A* और Contraction Hierarchies का उपयोग करते हैं।"
        ),
        (
            "19",
            "Distributed Message Queue",
            "Distributed Message Queue (Apache Kafka Internals)",
            "लाखों इवेंट्स प्रति सेकंड के थ्रूपुट के साथ डिस्ट्रीब्यूटेड, फॉल्ट-टॉलरेंट अपेंड-ओनली मैसेज कतार।",
            """- **Producers -> Broker Cluster (Topics & Partitions) -> Consumer Groups।**
- **Metadata Management:** KRaft (Raft consensus) या ZooKeeper।""",
            """- **Append-only Commit Log:** डिस्क पर सीक्वेंशियल राइट्स ($O(1)$)।
- **Zero-Copy Data Transfer:** Linux `sendfile` सिस्टम कॉल द्वारा डिस्क पेजकैश से सीधे नेटवर्क सॉकेट में डेटा भेजना।
- **Consumer Groups & Offsets:** कंज्यूमर्स के बीच लोड बैलेंसिंग और `__consumer_offsets` टॉपिक में ऑफसेट कमिट।""",
            "पार्टीशन्स की संख्या सोच-समझकर तय करें। बहुत अधिक पार्टीशन्स फाइल डिस्क्रिप्टर्स और री-बैलेंसिंग लेटेंसी बढ़ाते हैं।"
        ),
        (
            "20",
            "Metrics Monitoring and Alerting System",
            "Metrics Monitoring & Alerting (Prometheus/TSDB)",
            "हज़ारों सर्वर्स के सीपीयू, रैम, डिस्क और कस्टम एप्लिकेशन मेट्रिक्स को कलेक्ट, स्टोर और अलर्ट करना।",
            """- **Metrics Collector (Push/Pull) -> Time-Series Database (TSDB) -> Query Engine / Grafana -> Alert Manager (PagerDuty, Slack)।**""",
            """- **Pull vs Push:** Prometheus का Pull मॉडल (एजेंट्स को स्क्रैप करना) सर्विस डिस्कवरी को सरल बनाता है।
- **Gorilla TSDB Compression:** टाइमस्टैम्प्स हेतु **Delta-of-Delta Compression** (16 बाइट्स से 1.37 बिट्स) और फ्लोट्स हेतु XOR कम्प्रेशन।
- **डाउनसैंपलिंग:** 10 सेकंड का डेटा 7 दिन बाद 1 मिनट और 30 दिन बाद 1 घंटे के रोलअप में बदलना।""",
            "अलर्ट की बाढ़ (Alert Fatigue) से बचने के लिए अलर्ट मैनेजर में डिडुप्लिकेशन, ग्रुपिंग और एस्केलेशन पॉलिसी होना अनिवार्य है।"
        ),
        (
            "21",
            "Ad Click Event Aggregation",
            "Real-time Ad Click Event Aggregation (विज्ञापन क्लिक एनालिटिक्स)",
            "प्रति सेकंड लाखों विज्ञापन क्लिक्स को एग्रीगेट करना और विज्ञापनदाताओं को रियल-टाइम एनालिटिक्स देना।",
            """- **API Gateway -> Kafka Topic -> Apache Flink / Spark Streaming -> ClickHouse / Cassandra -> Analytics Dashboard।**""",
            """- **Event Time vs Processing Time:** वाटरमार्किंग द्वारा 1-5 मिनट के नेटवर्क डिले को संभालना।
- **एग्रीगेशन विंडोज़:** 1 मिनट की Tumbling Windows (गैर-ओवरलैपिंग) और मूविंग एवरेज हेतु Sliding Windows।
- **Reconciliation & Click Fraud:** बॉट क्लिक्स और डुप्लिकेट्स को फिल्टर करके विज्ञापनदाताओं से पारदर्शी बिलिंग करना।""",
            "डेटाबेस में हर क्लिक पर `UPDATE counter` करने से रो-लॉकिंग और क्रैश हो जाएगा। हमेशा इन-मेमोरी स्ट्रीम एग्रीगेशन करें।"
        ),
        (
            "22",
            "Hotel Reservation System",
            "Hotel Reservation System (होटल बुकिंग एवं कॉनकरेंसी)",
            "उच्च ट्रैफिक और त्योहारों के दौरान होटलों के कमरों की बुकिंग संभालना और डबल-बुकिंग रोकना।",
            """- **Client -> Load Balancer -> Reservation Service -> Relational DB (PostgreSQL) with ACID Transactions।**""",
            """- **Concurrency Control:**
  - *Pessimistic Locking:* `SELECT FOR UPDATE` (डेडलॉक और थ्रूपुट गिरावट का खतरा)।
  - *Optimistic Locking with Versioning:* `UPDATE inventory SET status='BOOKED', version=v+1 WHERE id=101 AND version=5` (उद्योग मानक)।
- **2-Phase State Machine:** `AVAILABLE` -> `RESERVED (10 min TTL)` -> पेमेंट सफल होने पर `CONFIRMED`।""",
            "होटल बुकिंग में Strong Consistency अनिवार्य है। NoSQL के बजाय रिलेशनल डीबी (ACID) का उपयोग करें।"
        ),
        (
            "23",
            "Distributed Email Service",
            "Distributed Email Service (Gmail Architecture)",
            "अरबों उपयोगकर्ताओं के लिए सुरक्षित, स्पैम-मुक्त और उच्च उपलब्धता वाली ईमेल सेवा।",
            """- **Web/Mobile Client -> Web Servers -> Mail Storage (Cassandra) & Attachment Store (S3) -> SMTP Outgoing Servers।**""",
            """- **प्रोटोकॉल्स:** SMTP (सेंडिंग), IMAP/POP3 (सिंक व फेचिंग)।
- **स्टोरेज टियर्स:** इनबॉक्स मेटाडेटा Cassandra में (User-partitioned), अटैचमेंट्स Amazon S3 में, फुल-टेक्स्ट सर्च Elasticsearch में।
- **ईमेल सुरक्षा:** SPF (अधिकृत IP), DKIM (क्रिप्टोग्राफिक सिग्नेचर), DMARC (पॉलिसी एनफोर्समेंट)।""",
            "ईमेल इनबॉक्स बहुत भारी होते हैं। फोल्डर्स और ईमेल्स को यूजर आईडी के आधार पर शार्ड करना अनिवार्य है।"
        ),
        (
            "24",
            "S3-like Object Storage",
            "S3-like Distributed Object Storage (BLOB Store)",
            "अनस्ट्रक्चर्ड डेटा (इमेजेस, वीडियोज, बैकअप्स) के लिए 99.999999999% (11 Nines) ड्यूरेबिलिटी वाला स्टोरेज।",
            """- **API Gateway -> Metadata Service (RocksDB/Spanner) & Storage Nodes (Disk Chunks) -> Garbage Collector Worker।**""",
            """- **Haystack / Bitcask पैटर्न:** लाखों फाइल्स को बड़े अपेंड-ओनली डेटा फाइल्स में एक साथ लिखना (Inode समाप्त होने से बचाव)।
- **Erasure Coding ($8+4$):** डेटा को 8 डेटा चंक्स और 4 पैरिटी चंक्स में तोड़कर 12 रैक्स पर रखना। कोई भी 4 सर्वर क्रैश होने पर भी 100% डेटा रिकवरी (3-वे रेप्लिकेशन से 50% बचत)।""",
            "ऑब्जेक्ट स्टोरेज में इन-प्लेस एडिट संभव नहीं है। फाइल अपडेट करने का अर्थ नया वर्जन लिखना है (Immutable Objects)।"
        ),
        (
            "25",
            "Real-time Gaming Leaderboard",
            "Real-time Gaming Leaderboard (लाइव लीडरबोर्ड)",
            "करोड़ों खिलाड़ियों के स्कोर अपडेट्स और सब-10ms में वैश्विक टॉप-10 लीडरबोर्ड प्रदर्शित करना।",
            """- **Game Client -> Game Service -> Leaderboard Service -> Redis Cluster (Sorted Sets) -> Client।**""",
            """- **Redis Sorted Set (ZSET) आर्किटेक्चर:** आंतरिक **SkipList + Hash Table**।
  - `ZADD`: $O(\\log N)$ अपडेट।
  - `ZREVRANGE`: $O(\\log N + M)$ टॉप-10 फेच।
  - `ZREVRANK`: $O(\\log N)$ ग्लोबल रैंक लुकअप।
- **शार्डिंग:** स्कोर रेंज या यूजर आईडी के आधार पर पार्टीशनिंग।""",
            "रिलेशनल डेटाबेस में `ORDER BY score DESC LIMIT 10` भारी टेबल स्कैन करता है और रियल-टाइम अपडेट्स पर क्रैश हो जाता है।"
        ),
        (
            "26",
            "Payment System",
            "Distributed Payment System (पेमेंट गेटवे एवं लेजर)",
            "वित्तीय लेनदेन की 100% सटीकता, सुरक्षा, आइडम्पोटेंसी और नियामक अनुपालन।",
            """- **Checkout -> Payment Service -> PSP (Stripe/PayPal) -> Double-Entry Ledger Service -> Reconciliation Batch Job।**""",
            """- **Double-Entry Bookkeeping Ledger:** हर ट्रांजैक्शन में डेबिट और क्रेडिट दोनों दर्ज होना: $\\sum \\text{Debits} == \\sum \\text{Credits}$।
- **Idempotency Keys:** डुप्लिकेट पेमेंट रोकने हेतु क्लाइंट UUID हेडर की डीबी जांच।
- **Reconciliation:** रात में चलने वाला स्वचालित समाधान बैच जॉब जो बैंक फाइल्स को इंटरनल लेजर से मैच करता है।""",
            "पेमेंट सिस्टम में कभी भी 'Eventual Consistency' स्वीकार्य नहीं है। डेटाबेस में स्ट्रिक्ट ACID और डिस्ट्रीब्यूटेड लॉक्स अनिवार्य हैं।"
        ),
        (
            "27",
            "Digital Wallet",
            "Digital Wallet (उच्च थ्रूपुट डिजिटल वॉलेट)",
            "डिजिटल वॉलेट्स के बीच 100,000+ Transfers/sec पर बैलेंस कंजर्वेशन और डेडलॉक-फ्री ट्रांसफर।",
            """- **Wallet API -> In-memory Core Ledger Engine (LMAX Disruptor) -> Write-Ahead Log -> Read Replicas (CQRS)।**""",
            """- **डेडलॉक रोकथाम:** दो यूज़र्स के बीच समवर्ती ट्रांसफर में हमेशा छोटी ID वाले अकाउंट को पहले लॉक करना (`min(A, B)` then `max(A, B)`)।
- **LMAX Disruptor:** लॉक-फ्री रिंग बफर द्वारा 100,000+ Transactions/sec की इन-मेमोरी प्रोसेसिंग।
- **CQRS:** राइट्स इन-मेमोरी कोर में और रीड्स असिंक्रोनस रीड-रेप्लिकस से।""",
            "अकाउंट बैलेंस कभी नेगेटिव नहीं होना चाहिए। बैलेंस इनवेरिएंट ($A_{new} = A_{old} - X \\ge 0$) हर ट्रांसफर में एटॉमिकली वैलिडेट होना चाहिए।"
        ),
        (
            "28",
            "Stock Exchange",
            "Ultra-Low Latency Stock Exchange (स्टॉक एक्सचेंज मैचिंग इंजन)",
            "शेयर बाजार के लिए सब-माइक्रोसेकंड लेटेंसी पर ऑर्डर्स मैच करना और निष्पादित करना।",
            """- **Trading Gateway (FIX Protocol) -> Order Manager -> In-memory Matching Engine (Order Book) -> Market Data Gateway -> Clearing & Settlement।**""",
            """- **Order Book:** Price-Time Priority (FIFO per price level)। आंतरिक संरचना: B-Tree / SkipList (प्राइस लेवल्स) + Doubly Linked List (ऑर्डर्स) $\\implies O(1)$ निष्पादन।
- **सब-माइक्रोसेकंड ऑप्टिमाइज़ेशन:** प्री-एलोकेटेड C++/रस्ट मेमोरी (No GC Pauses), Kernel Bypass (DPDK), और Deterministic Event Sourcing स्टैंडबाय रेप्लिकेशन।""",
            "स्टॉक एक्सचेंज में कोई भी डेटा लॉस बर्दाश्त नहीं किया जा सकता। ऑर्डर्स को तुरंत सीक्वेंशियल अपेंड-ओनली हार्डवेयर रिंग में परसिस्ट किया जाता है।"
        ),
    ]

    for ch_num, title_en, title_hi, scope, high_level, deep_dive, trade_offs in chapters_data:
        a(f"### Ch {ch_num}: {title_hi} ({title_en})")
        a()
        a(f"> 📂 **पूर्ण चैप्टर डॉक्यूमेंटेशन:** [`{ch_num}. {title_en}/Readme.hi.md`](./{ch_num}.%20{title_en.replace(' ', '%20')}/Readme.hi.md)")
        a()
        a(f"#### 1. समस्या और कार्यक्षेत्र (Problem Scope & Requirements):")
        a(scope.strip())
        a()
        a(f"#### 2. हाई-लेवल आर्किटेक्चर एवं डेटा फ्लो (High-Level Architecture & Flow):")
        a(high_level.strip())
        a()
        a(f"#### 3. डीप-डाइव और तकनीकी चुनौतियाँ (Deep Dive & Bottlenecks):")
        a(deep_dive.strip())
        a()
        a(f"#### 4. व्यापारिक समझौते एवं विफलता परिदृश्य (Trade-offs & Failure Scenarios):")
        a(trade_offs.strip())
        a()
        a("---")
        a()

    a("### 5. डिस्ट्रीब्यूटेड कैशिंग की 3 बड़ी विफलताएं एवं समाधान")
    a()
    a("1. **Cache Penetration (कैश पेनिट्रेशन):**")
    a("   - *समस्या:* कोई हमलावर ऐसी कीज़ मांगता है जो न तो कैश में हैं और न ही डेटाबेस में (उदा: `id = -9999`)। हर रिक्वेस्ट सीधे डेटाबेस को हिट करती है और डीबी क्रैश हो जाता है।")
    a("   - *समाधान:* **Bloom Filter** का उपयोग करें। यदि ब्लूम फ़िल्टर कहे कि की मौजूद नहीं है, तो तुरंत 404 लौटा दें। वैकल्पिक रूप से, नल वैल्यू को 2 मिनट के TTL के साथ कैश करें (`SET key null EX 120`)।")
    a()
    a("2. **Cache Breakdown / Stampede (हॉट की एक्सपायरेशन):**")
    a("   - *समस्या:* एक अत्यधिक लोकप्रिय की (उदा: बिग बिलियन डेज़ सेल का मुख्य प्रोडक्ट) जिस पर 50,000 QPS आ रहे हैं, अचानक कैश में एक्सपायर हो जाती है। सभी 50,000 रिक्वेस्ट्स एक ही मिलीसेकंड में डीबी को हिट करती हैं।")
    a("   - *समाधान:* **Mutex Lock (SETNX)** का उपयोग करें। केवल पहली रिक्वेस्ट डीबी से डेटा लाएगी, बाकी रिक्वेस्ट्स इंतजार करेंगी। या **Probabilistic Early Expiration (XFetch)** एल्गोरिदम द्वारा की एक्सपायर होने से 10 सेकंड पहले ही बैकग्राउंड में कैश रिफ्रेश कर लें।")
    a()
    a("3. **Cache Avalanche (कैश हिमस्खलन):**")
    a("   - *समस्या:* लाखों कीज़ को एक ही समय (उदा: रात 12:00 बजे 1 घंटे का फिक्स TTL) पर एक्सपायर होने के लिए सेट कर दिया गया। रात 1:00 बजे पूरा कैश एक साथ खाली हो जाता है और डीबी बैठ जाता है।")
    a("   - *समाधान:* **Random TTL Jitter (यादृच्छिक समय अंतर)** जोड़ें। `TTL = 3600 + rand(0, 300)` सेकंड। इससे कीज़ अलग-अलग समय पर धीरे-धीरे एक्सपायर होती हैं।")
    a()
    a("### 6. डेटाबेस रेप्लिकेशन टोपोलॉजीज़ (Replication Topologies)")
    a()
    a("| टोपोलॉजी | राइट्स (Writes) | रीड्स (Reads) | उपयुक्तता (Use Case) | मुख्य चुनौती |")
    a("|---|---|---|---|---|")
    a("| **Single-Leader** | केवल एक Primary नोड पर | कई Read Replicas पर | सामान्य वेब ऐप्स, ब्लॉग्स, ई-कॉमर्स | मास्टर फेलियर पर इलेक्शन डाउनटाइम |")
    a("| **Multi-Leader (Active-Active)** | कई अलग-अलग डेटासेंटर मास्टर्स पर | स्थानीय रीड रेप्लिकस पर | मल्टी-रीजन ऐप्स, ग्लोबल कंपनियां | राइट कॉनफ्लिक्ट रेजोल्यूशन (Conflict Resolution) |")
    a("| **Leaderless (Dynamo-style)** | किसी भी कोरम नोड पर | कोरम नोड्स से ($W + R > N$) | Cassandra, Riak, DynamoDB | रीड रिपेयर और हिंटेड हैंडऑफ ओवरहेड |")
    a()
    a("### 7. सिस्टम स्केलेबिलिटी के 5 स्वर्णिम सूत्र (Golden Rules of Scalability)")
    a("1. **Stateless Services:** एप्लिकेशन सर्वर्स को पूरी तरह स्टेटलेस रखें ताकि ऑटो-स्केलिंग 1 से 100 नोड्स तक सेकंडों में हो सके।")
    a("2. **Asynchronous Queuing:** यूजर के सीधे पाथ (Critical Path) से हर उस काम को हटाएं जो तुरंत जरूरी नहीं है और उसे Kafka कतार में डालें।")
    a("3. **Horizontal Sharding:** कभी भी एक डेटाबेस टेबल को 10 करोड़ रोज़ से अधिक न बढ़ने दें; शार्ड की द्वारा पार्टीशन करें।")
    a("4. **Defense in Depth (बहुस्तरीय कैशिंग):** ब्राउज़र कैश -> CDN Edge -> API Gateway Cache -> App Memory -> Redis -> DB Buffer Pool।")
    a("5. **Graceful Degradation:** भारी ओवरलोड के समय गैर-ज़रूरी फीचर्स (उदा: रिकमेंडेशन्स, ऑटो-सजेशन) को स्वतः अक्षम (Disable) करके कोर सर्विस को चालू रखना।")
    a()
    a("---")
    a()

    a("### 8. डिस्ट्रीब्यूटेड लॉकिंग: Redlock एल्गोरिदम और Fencing Tokens")
    a()
    a("- **समस्या:** सिंगल Redis नोड पर `SET resource_name my_random_value NX PX 30000` लॉक लगाना आसान है, किंतु यदि वह Redis मास्टर क्रैश हो जाए और स्लेव पर रेप्लिकेट होने से पहले दूसरा नोड लॉक ले ले, तो दो नोड्स एक साथ क्रिटिकल सेक्शन में घुस जाते हैं।")
    a("- **Redlock एल्गोरिदम (Antirez द्वारा प्रतिपादित):**")
    a("  1. 5 स्वतंत्र Redis नोड्स (बिना किसी रेप्लिकेशन के) का उपयोग करें।")
    a("  2. क्लाइंट एक ही रैंडम स्ट्रिंग और छोटे टाइमआउट (5-50ms) के साथ सभी 5 नोड्स पर एक साथ लॉक प्राप्त करने का प्रयास करता है।")
    a("  3. यदि क्लाइंट बहुमत (कम से कम 3 नोड्स) पर लॉक सफलतापूर्वक पा लेता है और बीता हुआ समय लॉक TTL से कम है, तो लॉक मान्य माना जाता है।")
    a("  4. कार्य पूरा होने पर सभी 5 नोड्स पर Lua स्क्रिप्ट द्वारा लॉक रिलीज किया जाता है।")
    a("- **Fencing Tokens (Martin Kleppmann का समाधान):**")
    a("  - जीसी पॉज़ (GC Pause) या नेटवर्क डिले के कारण क्लाइंट का लॉक एक्सपायर हो सकता है किंतु क्लाइंट सोचता है कि उसके पास लॉक है।")
    a("  - *समाधान:* लॉक सर्विस प्रत्येक लॉक के साथ एक मोनोटोनिकली बढ़ता हुआ **Fencing Token (उदा: 101, 102, 103)** देती है। स्टोरेज लेयर केवल उच्च टोकन वाले राइट्स को स्वीकार करता है और पुराने टोकन वाले राइट्स को रिजेक्ट कर देता है।")
    a()
    a("### 9. डेटाबेस इंडेक्सिंग के स्वर्णिम नियम (Indexing Best Practices)")
    a()
    a("1. **Leftmost Prefix Rule (कम्पोजिट इंडेक्स नियम):**")
    a("   - यदि इंडेक्स `(first_name, last_name, age)` पर है, तो क्वेरी केवल `first_name` या `first_name AND last_name` पर ही इंडेक्स का उपयोग कर सकती है। केवल `last_name` या `age` पर क्वेरी करने पर फुल टेबल स्कैन होगा।")
    a("2. **Covering Index (कवरिंग इंडेक्स):**")
    a("   - यदि इंडेक्स में वे सभी कॉलम्स मौजूद हैं जो `SELECT` और `WHERE` में मांगे गए हैं, तो डेटाबेस को मुख्य टेबल डिस्क पेजेस को छूने की आवश्यकता ही नहीं पड़ती (Index-Only Scan), जो 10x तेज़ है।")
    a("3. **Low-Cardinality Anti-Pattern:**")
    a("   - ऐसे कॉलम्स पर B+ Tree इंडेक्स कभी न बनाएं जिनमें बहुत कम विविधता हो (उदा: `gender`, `is_active`, `status`)। डेटाबेस ऑप्टिमाइज़र ऐसे इंडेक्स को अनदेखा करके सादा टेबल स्कैन करता है।")
    a()
    a("### 10. इंटरव्यू की सफलता के 5 अंतिम गोल्डन रूल्स (Final Golden Rules)")
    a()
    a("- **1. 80/20 नियम याद रखें:** इंटरव्यूअर आपसे सब कुछ नहीं सुनना चाहता; वह महत्वपूर्ण 20% कोर आर्किटेक्चर पर आपकी गहरी पकड़ देखना चाहता है।")
    a("- **2. नंबरों का औचित्य समझाएं:** जब कहें कि *'हम Redis चुन रहे हैं'*, तो बताएं: *'क्योंकि हमें <2ms लेटेंसी चाहिए और डेटा की-वैल्यू पेयर में आसानी से बैठता है'*, न कि सिर्फ इसलिए कि *'Redis लोकप्रिय है'*\।")
    a("- **3. फेलियर को आर्किटेक्चर का हिस्सा मानें:** हार्डवेयर क्रैश होगा, नेटवर्क टूटेगा, थर्ड-पार्टी APIs डाउन होंगी। जो इंजीनियर फेलियर मानकर चलता है, वही सच्चा सीनियर इंजीनियर होता है।")
    a("- **4. लागत (Cost) पर ध्यान दें:** असीमित सर्वर्स लगाना इंजीनियरिंग नहीं है। न्यूनतम लागत और सही रिसोर्स यूटिलाइज़ेशन के साथ सिस्टम बनाना असली इंजीनियरिंग है।")
    a("- **5. इंटरव्यूअर को अपना सहयोगी (Peer) समझें:** यह वाद-विवाद नहीं है, यह एक व्हाइटबोर्ड पर दो सहकर्मियों के साथ मिलकर सिस्टम डिज़ाइन करने का सहयोगात्मक अभ्यास है।")
    a()
    a("---")
    a()

    a("### 11. API Gateway बनाम Service Mesh (Envoy / Istio)")
    a()
    a("| पहलू | API Gateway (उदा: Kong, AWS API Gateway) | Service Mesh (उदा: Istio, Linkerd) |")
    a("|---|---|---|")
    a("| **ट्रैफिक प्रकार** | **North-South Traffic** (बाहरी क्लाइंट्स से आंतरिक सिस्टम्स में) | **East-West Traffic** (माइक्रोसर्विस से माइक्रोसर्विस के बीच) |")
    a("| **मुख्य कार्य** | ऑथेंटिकेशन (JWT/OAuth), रेट लिमिटिंग, SSL Termination, बिलिंग | mTLS (म्यूचुअल टीएलएस एन्क्रिप्शन), सर्विस डिस्कवरी, रिट्रीज, ट्रेंसिंग |")
    a("| **आर्किटेक्चर** | सेंट्रलाइज़्ड या क्लस्टर्ड रिवर्स प्रॉक्सी लेयर | साइडकार पैटर्न (Sidecar Proxy - प्रत्येक पॉड/कंटेनर के साथ Envoy) |")
    a("| **उपयोगिता** | जब बाहरी मोबाइल/वेब ऐप्स को सुरक्षित रूप से एंट्री देनी हो | जब आंतरिक 100+ माइक्रोसर्विस के बीच सुरक्षित और ट्रेस करने योग्य संचार चाहिए |")
    a()
    a("---")
    a()

    a("### 12. मुख्य सिस्टम्स के डेटाबेस स्कीमा और SQL उदाहरण")
    a()
    a("#### Ch 08: URL Shortener टेबल स्कीमा:")
    a("```sql")
    a("CREATE TABLE short_urls (")
    a("    id BIGINT PRIMARY KEY, -- 64-bit Snowflake ID")
    a("    short_code VARCHAR(10) UNIQUE NOT NULL, -- Base62 representation")
    a("    long_url TEXT NOT NULL,")
    a("    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),")
    a("    expires_at TIMESTAMP WITH TIME ZONE,")
    a("    user_id BIGINT")
    a(");")
    a("CREATE INDEX idx_short_code ON short_urls (short_code);")
    a("```")
    a()
    a("#### Ch 22: Hotel Reservation टेबल स्कीमा (Optimistic Locking):")
    a("```sql")
    a("CREATE TABLE room_inventory (")
    a("    room_id BIGINT PRIMARY KEY,")
    a("    hotel_id BIGINT NOT NULL,")
    a("    date DATE NOT NULL,")
    a("    status VARCHAR(20) NOT NULL, -- 'AVAILABLE', 'RESERVED', 'BOOKED'")
    a("    version INT NOT NULL DEFAULT 1,")
    a("    UNIQUE(hotel_id, date, room_id)")
    a(");")
    a("```")
    a()
    a("#### Ch 26: Double-Entry Ledger टेबल स्कीमा:")
    a("```sql")
    a("CREATE TABLE ledger_entries (")
    a("    entry_id UUID PRIMARY KEY,")
    a("    transaction_id UUID NOT NULL,")
    a("    account_id BIGINT NOT NULL,")
    a("    amount_cents BIGINT NOT NULL, -- Positive for Credit, Negative for Debit")
    a("    currency VARCHAR(3) NOT NULL,")
    a("    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
    a(");")
    a("CREATE INDEX idx_ledger_tx ON ledger_entries (transaction_id);")
    a("```")
    a()
    a("---")
    a()

    # 7. Architecture Comparison Matrices & Anti-Patterns
    a("## ⚖️ आर्किटेक्चरल तुलना तालिकाएँ एवं एंटी-पैटर्न्स (Cheat Sheet & Trade-off Matrices)")
    a()
    a("### 1. कम्युनिकेशन प्रोटोकॉल्स की तुलना (REST vs gRPC vs GraphQL vs WebSockets vs SSE)")
    a()
    a("| प्रोटोकॉल | ट्रांसपोर्ट | लेटेंसी | पेलोड प्रारूप | उपयोगिता (Best Use Case) |")
    a("|---|---|---|---|---|")
    a("| **REST** | HTTP/1.1 or HTTP/2 | मध्यम | JSON, XML | सार्वजनिक पब्लिक APIs, CRUD ऑपरेशन्स |")
    a("| **gRPC** | HTTP/2 | अत्यंत कम (Sub-ms) | Protocol Buffers (बाइनरी) | इंटरनल माइक्रोसर्विस कम्युनिकेशन्स |")
    a("| **GraphQL** | HTTP/1.1 or HTTP/2 | मध्यम | JSON | मोबाइल ऐप्स (केवल आवश्यक फील्ड्स मांगना) |")
    a("| **WebSocket** | TCP (Upgrade) | बहुत कम | टेक्स्ट, बाइनरी (द्विदिश) | चैट, गेमिंग, लाइव स्टॉक टिकर |")
    a("| **Server-Sent Events (SSE)** | HTTP/2 | कम | टेक्स्ट/इवेंट स्ट्रीम (एकदिश) | लाइव स्पोर्ट्स स्कोर, AI टोकन स्ट्रीमिंग |")
    a()
    a("### 2. मैसेजिंग सिस्टम्स की तुलना (Kafka vs RabbitMQ vs AWS SQS)")
    a()
    a("| विशेषता | Apache Kafka | RabbitMQ | AWS SQS |")
    a("|---|---|---|---|")
    a("| **मॉडल** | Append-Only Log (Pull-based) | Smart Broker, Dumb Consumer (Push-based) | Cloud Hosted Queue |")
    a("| **थ्रूपुट** | 1,000,000+ msgs/sec | ~50,000 msgs/sec | ऑटो-स्केल्ड क्लाउड थ्रूपुट |")
    a("| **मैसेज रिटेंशन** | दिनों या महीनों तक सुरक्षित (Replay संभव) | कंज्यूम होने के बाद डिलीट | 1 से 14 दिन |")
    a("| **उपयोगिता** | इवेंट स्ट्रीमिंग, एनालिटिक्स, लॉग्स | जटिल रूटिंग, टास्क कतारें, RPC | सर्वरलेस आर्किटेक्चर |")
    a()
    a("### 3. सिस्टम डिज़ाइन इंटरव्यू की 10 सबसे बड़ी गलतियाँ (Top 10 Anti-Patterns)")
    a()
    a("1. **बिना आवश्यकताएं समझे सीधे आर्किटेक्चर बनाना:** हमेशा पहले 3-5 मिनट DAU, रीड:राइट अनुपात और SLA स्पष्ट करें।")
    a("2. **रैम (RAM) को असीमित मान लेना:** Redis में असीमित डेटा नहीं समा सकता; हमेशा LRU Eviction और TTL लगाएं।")
    a("3. **नेटवर्क पार्टीशन और स्प्लिट-ब्रेन को अनदेखा करना:** हमेशा कोरम ($N/2 + 1$) और Raft कंसेंसस का उल्लेख करें।")
    a("4. **माइक्रोसर्विस में Two-Phase Commit (2PC) लगाना:** 2PC ब्लॉकिंग है; इसके स्थान पर **Saga Pattern** का उपयोग करें।")
    a("5. **कैश स्टैम्पीड (Cache Stampede) को भूल जाना:** हॉट की एक्सपायर होने पर डीबी क्रैश से बचने हेतु Mutex Lock लगाएं।")
    a("6. **डेटाबेस रेप्लिकेशन लैग की उपेक्षा:** यूजर के हालिया राइट्स को कुछ सेकंड तक सीधे Master DB से पढ़ें।")
    a("7. **बिना आवश्यकता के ओवर-इंजीनियरिंग:** 10 QPS के सिस्टम के लिए 50 नोड्स का Kafka क्लस्टर न सुझाएं।")
    a("8. **सिंगल प्वाइंट ऑफ फेलियर (SPOF) छोड़ देना:** लोड बैलेंसर और मास्टर डीबी को हमेशा एक्टिव-पैसिव रिडंडेंसी दें।")
    a("9. **डेटाबेस इंडेक्सिंग के नुकसान न जानना:** हर कॉलम पर इंडेक्स बनाने से राइट्स धीमे होते हैं और डिस्क भरती है।")
    a("10. **इंटरव्यूअर के साथ साइलेंट हो जाना:** हमेशा 'Think out loud' करें और अपने विचारों को साझा करें।")
    a()
    a("### 4. FAANG/MANG सिस्टम डिज़ाइन मूल्यांकन रूब्रिक (Grading Rubric)")
    a()
    a("| स्तर (Level) | अपेक्षित क्षमताएँ (Expectations) |")
    a("|---|---|")
    a("| **L4 (Mid-Level)** | सही कंपोनेंट्स चुनना, बेसिक APIs और डीबी स्कीमा बनाना, लोड बैलेंसर और कैश का सही उपयोग। |")
    a("| **L5 (Senior Engineer)** | ट्रेड-ऑफ्स स्पष्ट करना, बॉटलनेक्स की पहचान, डेटा शार्डिंग, कंकरेंसी लॉक्स, फेलियर मोड्स। |")
    a("| **L6 (Staff / Principal)** | अस्पष्टता को परिभाषित करना, मल्टी-डेटासेंटर DR, लागत अनुकूलन, संगठन-व्यापी प्रभाव। |")
    a()
    a("---")
    a()

    # 8. Interactive Simulators Guide
    a("## 🎮 लाइव इंटरएक्टिव सिम्युलेटर्स गाइड")
    a()
    a("इस प्रोजेक्ट में सिद्धांतों को जीवंत करने के लिए व्यावहारिक, पूर्णतः कार्यात्मक कोड और इंटरएक्टिव सिम्युलेटर्स शामिल हैं:")
    a()
    a("### 1. वेब डैशबोर्ड और लाइव सिम्युलेटर्स (`http://localhost:8000/`)")
    a("- **Token Bucket Rate Limiter (Ch 04):** लाइव रिक्वेस्ट भेजकर HTTP 429 थ्रॉटलिंग का वास्तविक प्रभाव देखें।")
    a("- **Consistent Hashing Ring (Ch 05):** कीज़ डालें और देखें कि वर्चुअल नोड्स के साथ कौन सा सर्वर रिस्पॉन्सिबल होता है।")
    a("- **Twitter Snowflake Generator (Ch 07):** 64-बिट टाइम-सॉर्टेड आईडी जनरेट करें और उसके बिट कंपोनेंट्स का विश्लेषण करें।")
    a("- **TinyURL Shortener (Ch 08):** Base62 एन्कोडिंग, LRU Cache और Bloom Filter के साथ यूआरएल छोटा करें।")
    a("- **Search Autocomplete (Ch 13):** Prefix Trie के साथ O(1) में सजेशन्स सर्च करें।")
    a("- **Real-time Leaderboard (Ch 25):** SkipList + Hash Table पर लाइव स्कोर अपडेट और टॉप-5 पोडियम फेच करें।")
    a("- **Digital Wallet (Ch 27):** डेडलॉक-फ्री डबल-एंट्री लेजर में ट्रांसफर टेस्ट करें।")
    a("- **Metrics Engine (Ch 20):** CPU यूसेज रिकॉर्ड करें और ऑटोमैटिक थ्रेशोल्ड अलर्ट्स ट्रिगर होते देखें।")
    a()
    a("### 2. VitePress सम्पूर्ण डॉक्यूमेंटेशन पोर्टल (`http://localhost:5173/` या `/portal/`)")
    a("- **सभी 28 चैप्टर्स** संपूर्ण **Tech-Hinglish** में सुसज्जित।")
    a("- **180+ विश्व भाषाओं का लाइव गूगल ट्रांसलेटर ड्रॉपडाउन** (अंग्रेजी, स्पेनिश, फ्रेंच, जर्मन, अरबी, रूसी, चीनी, जापानी, मराठी, बंगाली, तेलुगु, तमिल, गुजराती, आदि)।")
    a("- डार्क/लाइट मोड और ऑफलाइन लोकल सर्च।")
    a()
    a("### 3. इंटरएक्टिव CLI टूल्स (`python cli.py`)")
    a("```bash")
    a("# सभी सिस्टम्स का समग्र बेंचमार्क")
    a("python cli.py benchmark-all")
    a()
    a("# विशिष्ट सिस्टम डेमो")
    a("python cli.py demo-rate-limiter")
    a("python cli.py demo-consistent-hashing")
    a("python cli.py demo-snowflake")
    a("python cli.py demo-url-shortener")
    a("python cli.py demo-autocomplete")
    a("python cli.py demo-leaderboard")
    a("python cli.py demo-wallet")
    a("python cli.py demo-message-queue")
    a("python cli.py demo-object-storage")
    a("python cli.py demo-stock-exchange")
    a("```")
    a()
    a("---")
    a()

    # 8. Resources
    a("## 📖 संदर्भ एवं इंजीनियरिंग ब्लॉग्स (Curated Engineering Resources)")
    a()
    a("### Rate Limiting & Resilience")
    a("- [Martin Fowler: Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)")
    a("- [Uber Engineering: Leaky Bucket Rate Limiting Library in Go](https://github.com/uber-go/ratelimit)")
    a("- [Stripe Engineering: Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)")
    a()
    a("### Consistent Hashing & Distributed Storage")
    a("- [Tom White: Consistent Hashing Explained](https://tom-e-white.com/2007/11/consistent-hashing.html)")
    a("- [Stanford CS168: Consistent Hashing Lecture Notes](http://theory.stanford.edu/~tim/s16/l/l1.pdf)")
    a("- [Amazon Dynamo: Highly Available Key-value Store (SOSP 2007 Paper)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)")
    a("- [Google Maglev: A Fast and Reliable Software Network Load Balancer](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44824.pdf)")
    a("- [Discord Engineering: How Discord Scaled Elixir to 5,000,000 Concurrent Users](https://blog.discord.com/scaling-elixir-f9b8e1e7c29b)")
    a()
    a("### Databases & Storage Engines")
    a("- [Google Bigtable: A Distributed Storage System for Structured Data (OSDI 2006)](https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf)")
    a("- [Facebook Haystack: Finding a needle in Haystack - Facebook's photo storage](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Beaver.pdf)")
    a("- [Datastax: Apache Cassandra Architecture Internals](https://docs.datastax.com/en/archived/cassandra/3.0/cassandra/architecture/archIntro.html)")
    a("- [RocksDB: LSM-Tree internals and write amplification](https://rocksdb.org/blog/2014/03/27/how-to-backup-rocksdb.html)")
    a()
    a("### Unique IDs & Time")
    a("- [Twitter Engineering: Announcing Snowflake](https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html)")
    a("- [Flickr Code: Ticket Servers - Distributed Unique Primary Keys on the Cheap](https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap)")
    a()
    a("### Messaging, Streaming & Real-Time")
    a("- [LinkedIn Engineering / Apache Kafka Architecture Paper (NetDB 2011)](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/Kafka.pdf)")
    a("- [Discord Engineering: How Discord Stores Billions of Messages](https://discord.com/blog/how-discord-stores-billions-of-messages)")
    a("- [Slack Engineering: Flannel - An Application-Level Edge Cache to Make Slack Scale](https://slack.engineering/flannel-an-application-level-edge-cache-to-make-slack-scale/)")
    a("- [Netflix Tech Blog: High Quality Video Encoding at Scale](https://netflixtechblog.com/high-quality-video-encoding-at-scale-d159db052746)")
    a()
    a("### Financial Systems, Low Latency & High Performance")
    a("- [Martin Fowler: The LMAX Architecture (Disruptor Pattern)](https://martinfowler.com/articles/lmax.html)")
    a("- [Double-entry bookkeeping principles for software engineers](https://beancount.github.io/docs/the_double_entry_counting_method.html)")
    a("- [High-frequency trading matching engine design](https://www.cmegroup.com/education/courses/introduction-to-cme-globex.html)")
    a()
    a("---")
    a()
    a("## 📜 लाइसेंस एवं कॉपीराइट (License & Copyright)")
    a("यह रिपोजिटरी jigsi_karia द्वारा क्यूरेट की गई है और सॉफ्टवेयर इंजीनियरिंग समुदाय के अध्ययन हेतु निःशुल्क उपलब्ध है।")

    content = "\n".join(lines)
    return content

if __name__ == '__main__':
    c = build_full_readme()
    with open('Readme.md', 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Readme.md generated with {len(c.splitlines())} lines.")
