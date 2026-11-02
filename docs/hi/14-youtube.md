# Chapter 14: YouTube / Video Streaming Platform Design करना

## Introduction (भूमिका)
**YouTube** दुनिया का सबसे बड़ा वीडियो स्ट्रीमिंग प्लेटफॉर्म है जहाँ हर मिनट सैकड़ों घंटे के वीडियो अपलोड होते हैं और रोज़ाना अरबों बार देखे जाते हैं।

इस चैप्टर में हम एक ऐसा स्केलेबल वीडियो स्ट्रीमिंग आर्किटेक्चर डिज़ाइन करेंगे जो:
- **Fast Resumable Uploads:** बड़े वीडियोज़ (1 GB+) को बिना रुकावट के तेज़ी से अपलोड करना।
- **Smooth Streaming (Adaptive Bitrate):** यूज़र के इंटरनेट कनेक्शन (2G/3G/4G/5G/WiFi) के अनुसार वीडियो क्वालिटी (144p से 4K) को अपने आप एडजस्ट करना।
- **Cost-Optimized CDN Caching:** अरबों डॉलर के बैंडविड्थ खर्च को न्यूनतम करना।

---

## Step 1: High-Level Architecture (दो मुख्य प्रवाह)

<div style="margin-left:3rem">
<img src="/images/14-youtube/high-level-design.png" alt="High Level Design" width="400">
</div>

1. **Video Uploading Flow:** वीडियो को ओरिजिनल स्टोरेज (S3 Blob Store) में अपलोड करना और ट्रांसकोडिंग पाइपलाइन शुरू करना।
2. **Video Streaming Flow:** वीडियो को ग्लोबल CDN एज सर्वर्स से यूज़र के डिवाइस पर स्ट्रीम करना।

<div style="margin-left:3rem">
<img src="/images/14-youtube/video-uploading-flow.png" alt="Video Upload Flow" width="500">
</div>

---

## Step 2: Video Transcoding पाइपलाइन (DAG Model)

मोबाइल फोन से रिकॉर्ड किया गया ओरिजिनल रॉ वीडियो बहुत बड़ा होता है और हर डिवाइस (iPhone, Android, Smart TV) में अलग-अलग कोडेक (Codec) की जरूरत होती है।

### ट्रांसकोडिंग क्यों अनिवार्य है?
1. **कम्प्रेशन:** रॉ वीडियो को H.264 / VP9 / AV1 कोडेक्स से कंप्रेस करके साइज 90% कम करना।
2. **मल्टीपल रेजोल्यूशन:** 1080p, 720p, 480p, 360p, 240p के अलग-अलग चंक्स तैयार करना।
3. **स्ट्रीमिंग प्रोटोकॉल तैयार करना:** **Apple HLS** (HTTP Live Streaming) या **MPEG-DASH**।

### DAG (Directed Acyclic Graph) आर्किटेक्चर:
<div style="margin-left: 3em;">
<img src="/images/14-youtube/dag-video-transcoding.png" alt="DAG Video Transcoding" width="600">
</div>

वीडियो प्रोसेसिंग को समानांतर (Parallel) छोटे-छोटे टास्कस में तोड़ दिया जाता है:
- **GOP (Group of Pictures) Splitting:** वीडियो को कुछ-कुछ सेकंड्स के चंक्स में काटना।
- **Audio Extraction:** ऑडियो ट्रैक अलग निकालना।
- **Video Encoding:** अलग-अलग बिटरेट पर एक साथ एन्कोड करना।
- **Thumbnail Generator:** ऑटोमैटिक थंबनेल्स बनाना।
- **Watermarking:** कॉपीराइट वॉटरमार्क लगाना।

---

## Step 3: Video Streaming Protocols (Adaptive Bitrate)

<div style="margin-left: 3em;">
<img src="/images/14-youtube/video-streaming-flow.png" alt="Video Streaming Flow" height="400">
</div>

वीडियो कभी भी एक साथ पूरी फाइल के रूप में डाउनलोड नहीं होता! 
- वीडियो को 5-10 सेकंड के छोटे-छोटे फाइल्स (`.ts` या `.m4s` चंक्स) में बांटा जाता है।
- साथ में एक **Manifest File (`.m3u8` या `.mpd`)** होती है जिसमें सभी रेजोल्यूशंस और चंक्स के URLs लिखे होते हैं।
- **क्लाइंट प्लेयर (ExoPlayer / Video.js):** 
  - प्लेयर नेटवर्क स्पीड मापता है। 
  - यदि WiFi तेज़ है $\to$ 1080p चंक्स मांगता है।
  - यदि यूज़र लिफ्ट में गया और सिग्नल कमज़ोर हुआ $\to$ प्लेयर बिना वीडियो अटके तुरंत 360p चंक मांग लेता है (**Smooth Playback**)।

---

## Step 4: Cost Optimization (CDN बैंडविड्थ कैसे बचाएं?)

प्रतिदिन 5 Billion वीडियो व्यूज के लिए CDN का खर्च लाखों डॉलर प्रतिदिन हो सकता है। YouTube लागत कैसे बचाता है?

1. **Pareto Principle (80-20 Rule):** 
   - 80% व्यूज केवल 20% लोकप्रिय (Trending / Viral) वीडियोज़ पर आते हैं।
   - केवल टॉप 20% लोकप्रिय वीडियोज़ को प्रीमियम **CDN Edge Servers** पर कैश किया जाता है।
   - कम देखे जाने वाले पुराने वीडियोज़ को सीधे ओरिजिन ऑब्जेक्ट स्टोरेज से स्ट्रीम किया जाता है।
2. **On-Demand Transcoding:** जिन पुराने वीडियोज़ पर सालों में 1 व्यू आता है, उनके सभी 10 रेजोल्यूशंस पहले से बनाकर नहीं रखे जाते। ज़रूरत पड़ने पर उन्हें ऑन-डिमांड एन्कोड किया जाता है।
3. **ISP Partnerships (Open Connect / Google Global Cache):** टेलीकॉम कंपनियों (Jio, Airtel) के डेटा सेंटर्स के अंदर अपने कैशिंग सर्वर्स लगाना ताकि ट्रैफिक लोकल रहे।

---

## Step 5: Security (सुरक्षा और प्री-साइन्ड URLs)
<img src="/images/14-youtube/pres-signed-urls.png" alt="Pre Signed" width="500">

- वीडियो अपलोड करते समय यूज़र सीधे API सर्वर को वीडियो नहीं भेजता।
- API सर्वर यूज़र को एक टाइम-लिमिटेड **Pre-Signed S3 Upload URL** देता है।
- क्लाइंट सीधे AWS S3 या Google Cloud Storage में अपलोड करता है, जिससे हमारे वेब सर्वर्स का नेटवर्क बैंडविड्थ पूरी तरह खाली रहता है।
- कॉपीराइट सुरक्षा के लिए **DRM (Digital Rights Management - Google Widevine, Apple FairPlay)** का उपयोग किया जाता है।
