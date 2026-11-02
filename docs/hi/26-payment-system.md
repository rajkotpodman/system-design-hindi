# Chapter 26: Payment System Design करना (Stripe / Amazon Pay-in & Payout)

## Introduction (भूमिका)
इस चैप्टर में हम एक आधुनिक ई-कॉमर्स प्लेटफॉर्म (जैसे Amazon या Flipkart) के लिए **Payment System** का आर्किटेक्चर डिज़ाइन करेंगे।

पेमेंट सिस्टम किसी भी ऑनलाइन बिज़नेस का सबसे नाज़ुक और महत्वपूर्ण हिस्सा होता है, जो वित्तीय लेन-देन (Financial Transactions) और पैसे के मूवमेंट को सुरक्षित रूप से पूरा करता है। 

> [!CAUTION]
> **पेमेंट सिस्टम्स का सुनहरा नियम (Golden Rule):**
> अन्य सिस्टम्स (जैसे Twitter या YouTube) में थोड़ी बहुत डेटा विसंगति (Inconsistency) या डुप्लिकेट लाइक्स चल सकते हैं, लेकिन **पेमेंट सिस्टम में पैसे का 1 पैसा भी न तो हवा में गायब हो सकता है और न ही डुप्लिकेट कट सकता है**। यहाँ High Throughput से कहीं ज्यादा **100% Reliability, Zero Data Loss, और Strong Consistency** मायने रखती है।

---

## Step 1: Requirements और Scope समझना

### 1. Functional Requirements
- **Pay-in Flow:** ग्राहक से पैसा लेकर मर्चेंट/प्लेटफॉर्म के खाते में जमा करना (क्रेडिट कार्ड, यूपीआई, पेपाल)।
- **Pay-out Flow:** महीने के अंत में दुनिया भर के सेलर्स/मर्चेंट्स को उनके बैंक अकाउंट में पैसा भेजना।
- **Reconciliation (समाधान/मिलान):** आंतरिक डेटाबेस और बाहरी बैंकों/PSP के बीच हर रात लेन-देन का 1-1 पाई का मिलान करना।

### 2. Non-Functional Requirements
- **Reliability & Fault-Tolerance:** नेटवर्क फेलियर, टाइमआउट या पेमेंट गेटवे एरर के दौरान भी सटीक स्थिति संभालना।
- **Idempotency (अपरिवर्तनीयता):** यदि यूज़र "Pay Now" बटन पर 5 बार तेज़ी से क्लिक कर दे, तो भी उसके खाते से केवल एक ही बार पैसे कटने चाहिए।
- **Security & Compliance:** PCI-DSS अनुपालन (क्रेडिट कार्ड का CVV या नंबर अपने सर्वर पर स्टोर नहीं करना; टोकनाइज़ेशन के लिए Stripe/PSP पर निर्भर रहना)।

---

## Step 2: High-Level Architecture (Pay-in Flow)

<div style="margin-left:3rem">
<img src="/images/26-payment-system/high-level-flow.png" alt="high-level-flow" width="500" />
</div>

<div style="margin-left:3rem">
<img src="/images/26-payment-system/payin-flow-high-level.png" alt="pay-in-flow-high-level" width="500" />
</div>

### मुख्य माइक्रो-सर्विसेज:
1. **Payment Service:** पेमेंट रिक्वेस्ट प्राप्त करती है, फ्रॉड चेक और रिस्क असेसमेंट करती है।
2. **Payment Executor:** external PSP (Payment Service Provider जैसे Stripe, Adyen) के जरिए कार्ड स्कीम (Visa/Mastercard) को कॉल करके वास्तविक पैसे ट्रांसफर करवाता है।
3. **Double-Entry Ledger Service:** हर वित्तीय लेन-देन का बहीखाता (Audit Trail) रखती है।
4. **Wallet Service:** मर्चेंट्स और यूज़र्स के मौजूदा बैलेंस का हिसाब रखती है।

---

## Step 3: Double-Entry Ledger System (दोहरा लेखा प्रणाली)

किसी भी वित्तीय सिस्टम में साधारण `UPDATE balance = balance + 100` लिखना एक बहुत बड़ी गलती है! इसके बजाय सदियों पुरानी **Double-Entry Bookkeeping** का नियम लागू किया जाता है:

> **मूल सिद्धांत:** 
> पैसा कभी न तो पैदा होता है और न ही नष्ट होता है—वह केवल एक खाते से दूसरे खाते में ट्रांसफर होता है। प्रत्येक ट्रांजेक्शन में दो प्रविष्टियाँ होती हैं:
> - एक खाते में **Debit (नामे)**
> - दूसरे खाते में **Credit (जमा)**
> $$\sum \text{Debit} = \sum \text{Credit} \quad \implies \quad \sum \text{All Entries} = 0$$

| Transaction ID | Account | Debit ($) | Credit ($) | Note |
| :--- | :--- | :--- | :--- | :--- |
| tx_101 | Buyer_Credit_Card | 100.00 | - | यूज़र के कार्ड से कटे |
| tx_101 | Merchant_Settlement | - | 100.00 | मर्चेंट को प्राप्त हुए |

- **फायदा:** ऑडिटर्स और टैक्स अधिकारी किसी भी समय पूरे सिस्टम का सम चेक करके तुरंत सत्यापित कर सकते हैं कि किसी नोड या बग ने अवैध पैसा उत्पन्न तो नहीं किया।

---

## Step 4: डुप्लिकेट पेमेंट से बचाव — Idempotency Keys

नेटवर्क टाइमआउट होने पर जब क्लाइंट को यह नहीं पता चलता कि पेमेंट सफल हुई या नहीं, तो क्लाइंट दोबारा रिक्वेस्ट भेजता है।

<p align="center">
<img src="/images/26-payment-system/retry-mechanism.png" alt="Retry Flow" width="450">
</p>

<p align="center">
<img src="/images/26-payment-system/idempotency-example.png" alt="Idempotency Example" width="450">
</p>

### समाधान: Idempotency Key (इडेम्पोटेंसी कुंजी)
1. चेकआउट पेज लोड होते ही क्लाइंट को एक यूनीक UUID (`idempotency_key`) दी जाती है।
2. जब भी पेमेंट रिक्वेस्ट भेजी जाती है, तो HTTP हेडर में यह की भेजी जाती है:
   ```http
   Idempotency-Key: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
   ```
3. सर्वर पर `idempotency_keys` टेबल में एक यूनिक कंस्ट्रेंट (Unique Index) होता है।
4. यदि वही की दोबारा आती है:
   - डेटाबेस डुप्लिकेट एरर फेंक देता है।
   - पेमेंट गेटवे पर दोबारा चार्ज नहीं काटा जाता, बल्कि पिछली सफल पेमेंट का परिणाम ही वापस लौटा दिया जाता है।

---

## Step 5: Reconciliation (दैनिक मिलान प्रक्रिया)

रात के समय (Off-peak hours) बाहरी पेमेंट प्रोवाइडर (जैसे Stripe/Visa) हमें एक **Settlement File (CSV/MT940)** भेजता है जिसमें उनके द्वारा प्रोसेस किए गए सभी ट्रांजेक्शन होते हैं।
- हमारा **Reconciliation Worker** हमारे आंतरिक Ledger रिकॉर्ड्स और बैंक की स्टेटमेंट का लाइन-दर-लाइन मिलान करता है।
- यदि कोई विसंगति (Mismatch) मिलती है (जैसे बैंक ने पैसे काट लिए लेकिन हमारे सर्वर का डेटाबेस क्रैश होने से ऑर्डर नहीं बना):
  - सिस्टम उसे **Discrepancy Queue** में डाल देता है जहाँ ऑटोमेटेड री-ट्राई या कस्टमर सपोर्ट एजेंट रिफंड जारी करता है।
