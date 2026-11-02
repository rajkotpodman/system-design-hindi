# Chapter 27: Digital Wallet System Design (PayTM / PayPal / Google Pay)

## Introduction (भूमिका)
**Digital Wallet** (जैसे PayTM, PhonePe, PayPal, या Cash App) यूज़र्स को अपने वॉलेट में पैसे स्टोर करने, दोस्तों को ट्रांसफर करने, या मर्चेंट्स को पेमेंट करने की सुविधा देता है। 

डिजिटल वॉलेट के बीच होने वाले ट्रांसफर्स सामान्य बैंकिंग नेटवर्क (जैसे ACH या Wire Transfer) की तुलना में कई गुना तेज़ और सस्ते होते हैं क्योंकि सारा ट्रांजेक्शन वॉलेट प्रोवाइडर के अपने आंतरिक लेज़र में प्रोसेस होता है।

### मुख्य चुनौतियाँ और आवश्यकताएँ (Scale & Scope)
- **Extreme Scale:** सिस्टम को प्रति सेकंड **1,000,000 (1 Million) TPS** सपोर्ट करना है!
- **Strict Correctness:** किसी भी हालत में पैसा गायब नहीं होना चाहिए।
- **Auditability & Reproducibility:** 2 साल बाद भी किसी भी खाते का ऐतिहासिक बैलेंस दिन-प्रतिदिन के इवेंट्स को दोबारा प्ले (Replay) करके 100% साबित किया जा सके।
- **Availability:** 99.99% Uptime.

---

## Step 1: Back-of-the-Envelope Estimation (बॉटलनेक की पहचान)

एक स्टैंडर्ड रिलेशनल डेटाबेस (जैसे MySQL on AWS RDS) अधिकतम **1,000 TPS** संभाल सकता है।
- हर वॉलेट ट्रांसफर में दो लेग्स (2 legs) होते हैं:
  - Account A से पैसे कटते हैं (Debit)
  - Account B में पैसे जुड़ते हैं (Credit)
- $1,000,000\text{ Transfers/sec} \implies 2,000,000\text{ DB Operations/sec}$!
- यदि हम पारंपरिक डेटाबेस पर निर्भर रहें, तो हमें **2,000 डेटाबेस नोड्स** की आवश्यकता होगी।
- अतः हमारा मुख्य आर्किटेक्चरल लक्ष्य प्रति-नोड TPS को अधिकतम करना और डिस्ट्रीब्यूटेड ट्रांजेक्शन्स की लेटेंसी को न्यूनतम करना है।

---

## Step 2: Distributed Transactions (डिस्ट्रीब्यूटेड ट्रांजेक्शन के विकल्प)

जब Account A और Account B दो अलग-अलग डेटाबेस शार्द्स (Shards) पर स्थित हों, तो दोनों में एक साथ या तो बदलाव होना चाहिए या कुछ नहीं होना चाहिए (Atomicity)।

### 1. Two-Phase Commit (2PC)
<div style="margin-left:3rem">
<img src="/images/27-digital-wallet/2pc-protocol.png" alt="2pc-protocol" width="500">
</div>

- **Phase 1 (Prepare):** कोऑर्डिनेटर दोनों डेटाबेस से पूछता है कि क्या वे ट्रांजेक्शन के लिए तैयार हैं? दोनों लॉक लगाते हैं और "Yes" कहते हैं।
- **Phase 2 (Commit):** यदि दोनों ने "Yes" कहा, तो कमिट होता है।
- **गंभीर कमी:** 2PC बहुत धीमा है। डिस्क पर भारी लॉक होल्ड करने से Lock Contention बढ़ता है और लेटेंसी 10 गुना बढ़ जाती है। कोऑर्डिनेटर SPOF बन जाता है।

---

### 2. Try-Confirm / Cancel (TC/C)
<div style="margin-left:3rem">
<img src="/images/27-digital-wallet/try-phase.png" alt="try-phase" width="500">
</div>

यह दो स्वतंत्र ट्रांजेक्शन्स के रूप में काम करता है:
1. **Try Phase:** Account A के बैलेंस से पैसे काटकर एक अस्थायी "Reserved" बकेट में डाल दिए जाते हैं।
2. **Confirm Phase:** यदि रिज़र्वेशन सफल रहा, तो Account B के खाते में पैसे जोड़ दिए जाते हैं।
3. **Cancel Phase (यदि फेल हुआ):** Account A का पैसा वापस उसके एक्टिव बैलेंस में जोड़ दिया जाता है (Compensating Transaction)।
- *फायदा:* डेटाबेस लेवल पर लंबे लॉक्स नहीं लगाने पड़ते, जिससे थ्रूपुट बहुत ज्यादा बढ़ जाता है।

---

### 3. Saga Pattern (ऑर्केस्ट्रेशन आधारित)
<div style="margin-left:3rem">
<img src="/images/27-digital-wallet/saga.png" alt="saga" width="500">
</div>

- माइक्रो-सर्विसेज में डिस्ट्रीब्यूटेड ट्रांजेक्शन के लिए Saga एक इंडस्ट्री स्टैंडर्ड है।
- सभी कार्य एक रेखीय क्रम (Linear Sequence) में होते हैं।
- यदि रास्ते में कोई भी सर्विस फेल होती है, तो Saga Orchestrator उलटी दिशा में कंपनसेटिंग ट्रांजेक्शन्स चलाकर पूरे सिस्टम को पुरानी सुरक्षित अवस्था में ले आता है।

---

## Step 3: Event Sourcing & CQRS (अल्टीमेट विश्वसनीयता का रहस्य)

वित्तीय सिस्टम्स में स्टेट (Current Balance) को सीधे डेटाबेस में ओवरराइट करना खतरनाक है। इसके बजाय **Event Sourcing** तकनीक अपनाई जाती है:

<p align="center">
<img src="/images/27-digital-wallet/event-sourcing.png" alt="Event Sourcing" width="450">
</p>

### 4 बुनियादी स्तंभ:
1. **Command (आदेश):** क्लाइंट का इरादा (Intent) — जैसे: *"ट्रांसफर $10 from Alice to Bob"*। कमांड्स FIFO कतार में आते हैं और वेलिडेशन के बाद प्रोसेस होते हैं।
2. **Event (अपरिवर्तनीय घटना):** सिस्टम में जो घट चुका है (Immutable Historical Fact) — जैसे: *"Account Alice Debited $10"*, *"Account Bob Credited $10"*। यह अपेंड-ओनली (Append-only) लॉग में सुरक्षित हो जाता है। इसे कभी डिलीट या एडिट नहीं किया जा सकता!
3. **State (मौजूदा स्थिति):** इवेंट्स के क्रम का परिणाम (Current Balances)।
4. **State Machine (पुनर्निर्माण):** यदि पूरा डेटाबेस क्रैश हो जाए, तो पहले दिन से लेकर आज तक के सभी इवेंट्स को दोबारा प्ले करके 1-1 सेकंड का सटीक बैलेंस दोबारा बनाया जा सकता है!

---

## High-Throughput Engine (LMAX Disruptor & RocksDB)

1 Million TPS हासिल करने के लिए:
- डिस्क I/O और नेटवर्क कॉल से बचने के लिए **In-Memory Sequential Execution** (LMAX Disruptor आर्किटेक्चर) का उपयोग किया जाता है।
- इवेंट्स को **Kafka** या **Raft consensus log** के जरिए रेप्लिकेट किया जाता है।
- लोकल स्टेट को **RocksDB (LSM Tree)** में स्टोर किया जाता है जो सीक्वेंशियल राइट्स में अल्ट्रा-फास्ट है।
