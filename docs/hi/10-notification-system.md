# Chapter 10: Notification System Design करना (Push, SMS, Email)

## Introduction (भूमिका)
एक **Notification System** आधुनिक मोबाइल और वेब एप्लिकेशन्स (जैसे Uber, Swiggy, Netflix) का अनिवार्य कंपोनेंट है। यह यूज़र्स को महत्वपूर्ण अपडेट्स, बिलिंग अलर्ट्स, प्रमोशन्स और ओटीपी (OTP) समय पर भेजने का काम करता है।

नोटिफिकेशन्स मुख्य रूप से 3 चैनलों द्वारा डिलीवर किए जाते हैं:
1. **Mobile Push Notifications:** iOS (APNS) और Android (FCM).
2. **SMS Messages:** Twilio, Nexmo, Sinch.
3. **Transactional Emails:** SendGrid, Amazon SES, Mailchimp.

---

## Step 1: Requirements और Scope समझना

### Scale & Traffic
- **Push Notifications:** 10 Million प्रति दिन
- **Emails:** 5 Million प्रति दिन
- **SMS Messages:** 1 Million प्रति दिन
- **Soft Real-Time:** नोटिफिकेशन्स न्यूनतम लेटेंसी में यूज़र के डिवाइस तक पहुँचने चाहिए।
- **Opt-Out Control:** यूज़र सेटिंग्स में किसी विशेष चैनल (जैसे प्रमोशनल SMS) को बंद कर सके।

---

## Step 2: High-Level Architecture (सिस्टम कंपोनेंट्स)

<div style="margin-left:3rem">
<img src="/images/10-notification-system/contact-info-gathering.png" alt="Contact Info Gathering" width="500">
</div>

### 1. Contact Info Gathering (डिवाइस टोकन और संपर्क जानकारी)
जब यूज़र ऐप इनस्टॉल करता है या लॉगिन करता है:
- iOS डिवाइस Apple से एक **Device Token** प्राप्त करता है।
- Android डिवाइस Google से एक **Registration Token (FCM Token)** प्राप्त करता है।
- हमारी ऐप यह टोकन हमारे डेटाबेस में `user_id` के साथ सुरक्षित कर लेती है।

---

### 2. प्रारंभिक डिज़ाइन की समस्याएं (Initial SPOF Design)
<div style="margin-left:3rem">
<img src="/images/10-notification-system/high-level-design.png" alt="High Level Design" width="500">
</div>

यदि हम एक ही नोटिफिकेशन सर्वर पर सीधे Third-Party APIs (APNS/FCM/Twilio) कॉल करें:
- **SPOF (Single Point of Failure):** यदि नोटिफिकेशन सर्वर क्रैश हुआ, तो पूरी सर्विस ठप।
- **Performance Bottleneck:** Third-party APIs नेटवर्क पर धीमी हो सकती हैं, जिससे सर्वर के थ्रेड्स ब्लॉक हो जाएंगे।

---

### 3. उन्नत और स्केलेबल आर्किटेक्चर (Message Queues & Workers)
<div style="margin-left:3rem">
<img src="/images/10-notification-system/improved-design.png" alt="Improved Design" width="500">
</div>

- **Stateless Notification Servers:** रिक्वेस्ट्स को वैलिडेट करते हैं और तुरंत एक **Message Queue (जैसे RabbitMQ / Kafka)** में पुश कर देते हैं।
- **Dedicated Message Queues per Channel:** 
  - Push Queue
  - SMS Queue
  - Email Queue
- **Independent Workers:** वर्कर पूल्स संबंधित कतार से मैसेज निकालते हैं और थर्ड-पार्टी प्रोवाइडर्स को भेजते हैं। यदि SMS प्रोवाइडर धीमा भी हो, तो Push Notifications बिना किसी रुकावट के चलते रहते हैं।

---

## Step 3: Design Deep Dive (विश्वसनीयता और सुरक्षा)

### 1. Data Loss से बचाव (At-Least-Once Delivery)
<div style="margin-left:3rem">
<img src="/images/10-notification-system/data-loss.png" alt="Data Loss" width="400">
</div>

नोटिफिकेशन डेटा को भेजने से पहले डिस्क पर **Notification Log Database** में राइट किया जाता है। यदि कोई वर्कर क्रैश भी हो जाए, तो मैसेज कतार में वापस आ जाता है और दूसरा वर्कर उसे दोबारा प्रोसेस करता है।

### 2. Deduplication (डुप्लिकेट नोटिफिकेशन से बचाव)
नेटवर्क री-ट्राई के कारण एक ही यूज़र को 2 बार "Order Delivered" का मैसेज न मिले, इसके लिए:
- हर नोटिफिकेशन इवेंट में एक यूनीक **Event ID** होता है।
- वर्कर भेजने से पहले Redis में चेक करता है:
  - यदि Event ID पहले से मौजूद है $\to$ मैसेज डिस्कार्ड कर दिया जाता है।
  - यदि नया है $\to$ मैसेज भेजा जाता है और Event ID को TTL के साथ Redis में लिख दिया जाता है।

### 3. Notification Templates & Rate Limiting
<div style="margin-left:3rem">
<img src="/images/10-notification-system/events-tracking.png" alt="Events Tracking" width="400">
</div>

- **Templates:** बार-बार नया मैसेज कंपोज़ करने के बजाय प्री-फॉर्मेटेड टेम्प्लेट (जैसे `"Hi {name}, your order #{order_id} is out for delivery"`) इस्तेमाल होते हैं।
- **Rate Limiting:** किसी भी यूज़र को स्पैम से बचाने के लिए प्रति घंटे अधिकतम 3-5 नोटिफिकेशन्स की सीमा तय की जाती है।

---

## सम्पूर्ण आर्किटेक्चर सारांश (Final Architecture Flow)

<div style="margin-left:3rem">
<img src="/images/10-notification-system/updated-design.png" alt="Updated Design" width="500">
</div>

1. Microservices (Billing, Shipping, Marketing) नोटिफिकेशन API को कॉल करती हैं।
2. Notification Servers इन-मेमोरी Redis से यूज़र प्रेफरेंसेज और डिवाइस टोकन्स लाते हैं।
3. इवेंट्स को अलग-अलग चैनल की कतारों (Queues) में भेजा जाता है।
4. Workers इवेंट्स को प्रोसेस करके APNS, FCM, और Twilio को हैंडऑफ करते हैं।
5. Analytics Workers डिलीवरी स्टेटस, ओपन रेट्स और क्लिक मैट्रिक्स ट्रैक करते हैं।
