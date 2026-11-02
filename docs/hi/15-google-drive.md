# Chapter 15: Google Drive / Cloud File Storage Design करना (Dropbox Architecture)

## Introduction (भूमिका)
**Google Drive** (या Dropbox, OneDrive) एक क्लाउड-आधारित फाइल स्टोरेज और सिंक्रोनाइज़ेशन सेवा है जो यूज़र्स को अपने डॉक्यूमेंट्स, फोटो और वीडियो सुरक्षित रखने, विभिन्न डिवाइसेस (फोन, लैपटॉप) पर सिंक करने और दोस्तों के साथ शेयर करने की सुविधा देती है।

### मुख्य आवश्यकताएं (Requirements)
- **File Upload & Download:** बड़ी फाइल्स (10 GB तक) को तेज़ी से अपलोड/डाउनलोड करना।
- **Cross-Device Sync (डेल्टा सिंक):** लैपटॉप पर फाइल एडिट करते ही फोन पर कुछ सेकंड में अपडेट हो जाना।
- **Revision History:** फाइल्स के पिछले वर्शन्स सुरक्षित रखना (Version Control)।
- **Scale:** **10 Million DAU**, कुल स्टोरेज क्षमता $\approx \mathbf{500\text{ Petabytes (PB)}}$।
- **100% Data Reliability:** डेटा का 1 बाइट भी नष्ट नहीं होना चाहिए (Zero Data Loss Guarantee)।

---

## Step 1: The Core Innovation — Chunking & Delta Sync

यदि यूज़र 100 MB की एक PDF या Word फाइल में सिर्फ 1 लाइन बदलता है, तो क्या हमें पूरी 100 MB की फाइल दोबारा अपलोड करनी चाहिए? बिल्कुल नहीं! इससे यूज़र का इंटरनेट डेटा और हमारे क्लाउड का बैंडविड्थ दोनों बर्बाद होंगे।

<div style="margin-left:2rem">
<img src="/images/15-google-drive/delta-sync.png" alt="Delta Sync" width="400">
</div>

### Block-Level Chunking (चंकिंग तकनीक):
1. फाइल को **4 MB के छोटे-छोटे ब्लॉक्स (Blocks / Chunks)** में तोड़ दिया जाता है।
2. प्रत्येक ब्लॉक का एक यूनीक क्रिप्टोग्राफिक हैश (जैसे SHA-256) निकाला जाता है।
3. **Delta Sync (परिवर्तन सिंक):** जब फाइल एडिट होती है, तो केवल वही 4 MB का ब्लॉक दोबारा अपलोड होता है जिसमें बदलाव हुआ है, बाकी सभी ब्लॉक्स पुराने ही इस्तेमाल होते हैं!
4. **Block Deduplication:** यदि दुनिया भर के 10,000 यूज़र्स के पास एक ही समान Ubuntu ISO या मूवी फाइल है, तो क्लाउड स्टोरेज में वह ब्लॉक केवल एक ही बार स्टोर होता है और बाकी सभी को केवल पॉइंटर दे दिया जाता है। इससे स्टोरेज लागत 70% तक घट जाती है।

---

## Step 2: High-Level Architecture (सिस्टम कंपोनेंट्स)

<div style="margin-left:5rem">
<img src="/images/15-google-drive/high-level-design.png" alt="High Level Design" width="500">
</div>

1. **User Client:** फाइल को लोकली 4MB चंक्स में तोड़ता है, कंप्रेस करता है और एन्क्रिप्ट करता है।
2. **Block Servers:** ब्लॉक्स को प्रोसेस करते हैं और ऑब्जेक्ट स्टोरेज में ट्रांसफर करते हैं।
3. **Cloud Storage (S3 / Blob Store):** सभी रॉ डेटा ब्लॉक्स को स्टोर करता है।
4. **Cold Storage (S3 Glacier):** पुरानी इनएक्टिव फाइल्स को बेहद सस्ती कोल्ड स्टोरेज में मूव कर दिया जाता है।
5. **Metadata Database (MySQL / Spanner):** फाइल्स, यूज़र्स, पाथ्स और ब्लॉक्स के बीच की मैपिंग (Metadata) रखता है।
6. **Notification Service (WebSocket / Long Polling):** जब भी कोई फाइल एडिट होती है, तो यह सर्विस यूज़र के अन्य सभी डिवाइसेस को सिंक करने का सिग्नल भेजती है।

---

## Step 3: Metadata Schema Design

<div style="margin-left:5rem">
<img src="/images/15-google-drive/metadata-database.png" alt="Metadata Database" width="500">
</div>

डेटाबेस में 4 मुख्य टेबल्स होते हैं:
1. **User Table:** यूज़र आईडी, नाम और उपयोग किया गया स्टोरेज कोटा।
2. **File Table:** `file_id`, फाइल का नाम, पाथ, ओनर और मौजूदा वर्शन।
3. **Block Table:** `block_id`, `file_version_id`, `block_order` (फाइल को सही क्रम में दोबारा जोड़ने के लिए) और `block_hash`।
4. **File Version Table:** हर पिछले वर्शन का रिकॉर्ड ताकि यूज़र कभी भी पुरानी फाइल रिस्टोर कर सके।

---

## Step 4: Sync Conflicts (समवर्ती टकराव कैसे सुलझाएं?)

<div style="margin-left:5rem">
<img src="/images/15-google-drive/sync-conflicts.png" alt="Sync Conflicts" width="600">
</div>

जब दो यूज़र्स (या एक ही यूज़र फोन और लैपटॉप पर) एक ही फाइल को एक ही समय में ऑफलाइन एडिट करते हैं:
1. जो वर्शन पहले हमारे सर्वर पर पहुँचता है, उसे मुख्य वर्शन स्वीकार कर लिया जाता है।
2. जब दूसरे डिवाइस का वर्शन आता है, तो सिस्टम **Sync Conflict** डिटेक्ट करता है।
3. सिस्टम फाइल को ओवरराइट करने के बजाय दो फाइल्स बना देता है:
   - `Document.docx` (सर्वर का ताज़ा वर्शन)
   - `Document_conflicted_copy_User2.docx` (लोकल वर्शन)
4. यूज़र दोनों फाइल्स की तुलना करके स्वयं तय कर सकता है कि किसे रखना है (Dropbox / Google Drive यही रणनीति अपनाते हैं)।
