# Chapter 13: Search Autocomplete System Design करना (Typeahead / Google Search Suggestions)

## Introduction (भूमिका)
**Search Autocomplete** (जिसे Typeahead या Incremental Search भी कहा जाता है) Google या Amazon सर्च बार की तरह काम करता है: जैसे ही यूज़र कुछ अक्षर टाइप करता है, सिस्टम तुरंत उस प्रीफिक्स (Prefix) से शुरू होने वाले सबसे लोकप्रिय Top-5 सर्च सुझाव (Suggestions) स्क्रीन पर दिखा देता है।

### सिस्टम की मुख्य आवश्यकताएं (Requirements)
- **Fast Response Time:** सुझाव 100 मिलीसेकंड ($<100\text{ ms}$) से कम समय में यूज़र की स्क्रीन पर आने चाहिए, वरना टाइपिंग लैग महसूस होगा।
- **Relevant & Popular:** सुझाव ऐतिहासिक सर्च फ्रीक्वेंसी (Query Popularity) के आधार पर Top 5 होने चाहिए।
- **High Throughput:** 10 Million DAU, और प्रत्येक सर्च क्वेरी में 4-6 की-स्ट्रोक्स (Keystrokes) होते हैं $\implies \approx \mathbf{48,000\text{ QPS}}$ संभालना।

---

## Step 1: High-Level Architecture (दो स्वतंत्र सेवाएं)

पूरे सिस्टम को 2 अलग-अलग टियर्स में बांटा जाता है:
1. **Data Gathering Service (ऑफ़लाइन / बैच पाइपलाइन):** यूज़र्स द्वारा सर्च किए गए अरबों शब्दों के लॉग्स इकट्ठा करती है, फ्रीक्वेंसी काउंट करती है और हर हफ्ते नया Trie डेटा स्ट्रक्चर बनाती है।
2. **Query Service (ऑनलाइन / रियल-टाइम सेवा):** जब यूज़र टाइप करता है, तो यह इन-मेमोरी Trie Cache से तुरंत Top-5 परिणाम पढ़कर वापस भेजती है।

<div style="margin-left:3rem">
<img src="/images/13-search-autocomplete/data-gathering.png" alt="Data Gathering" width="600">
</div>

---

## Step 2: कोर डेटा स्ट्रक्चर — Trie (Prefix Tree)

डेटाबेस में `SELECT query FROM table WHERE query LIKE 'tw%' ORDER BY freq DESC LIMIT 5` चलाना अत्यंत धीमा है। इसके लिए **Trie (प्रीफिक्स ट्री)** डेटा स्ट्रक्चर का उपयोग किया जाता है:

<div style="margin-left:3rem">
<img src="/images/13-search-autocomplete/trie-structure.png" alt="Trie Structure" width="500">
</div>

### बेसिक Trie की सीमा:
- यदि हम हर कीस्ट्रोक पर रूट से ट्री को ट्रेवर्स करें और फिर उस सब-ट्री के सभी हज़ारों नोड्स को सॉर्ट करके Top 5 निकालें:
  $$\text{Time Complexity} = O(p) + O(c) + O(c \log k)$$
  (जहाँ $p = \text{Prefix Length}$, $c = \text{Total Child Nodes}$). यह 48,000 QPS पर बहुत धीमा हो जाएगा।

---

### The Game-Changing Optimization: Pre-computed Top-k Cache at Each Node!

<img src="/images/13-search-autocomplete/cached-trie.png" alt="Cached Trie" width="600">

> [!TIP]
> **ऑप्टिमाइज़ेशन का रहस्य:**
> रन-टाइम पर सब-ट्री को सॉर्ट करने के बजाय, **Trie बनाते समय ही प्रत्येक नोड पर पहले से ही उसके Top 5 सबसे लोकप्रिय सर्च शब्द स्टोर कर दिए जाते हैं!**
> - जब यूज़र `t` टाइप करता है $\to$ सीधे `t` नोड पर मौजूद प्री-कंप्यूटेड 5 सुझाव लौट जाते हैं।
> - जब यूज़र `tw` टाइप करता है $\to$ सीधे `w` नोड पर मौजूद प्री-कंप्यूटेड 5 सुझाव लौट जाते हैं।
> - **लुकअप टाइम कॉम्प्लेक्सिटी:** सीधे घटकर **$O(1)$** (या $O(\text{Prefix Length})$) हो जाती है!

---

## Step 3: Data Gathering Pipeline (अल्ट्रा-स्केल डेटा पाइपलाइन)

हर एक कीस्ट्रोक पर Trie को रियल-टाइम में अपडेट करना असंभव है क्योंकि अरबों कीस्ट्रोक्स आते हैं। इसलिए **MapReduce / Spark** बैच पाइपलाइन अपनाई जाती है:

<div style="margin-left:3rem">
<img src="/images/13-search-autocomplete/data-gathering-flow.png" alt="Updated Data Gathering Flow" width="600">
</div>

1. **Analytics Logs:** सभी सर्च क्वेरीज़ अपेंड-ओनली लॉग फाइल्स में राइट होती हैं।
2. **Aggregators:** हर सप्ताह लॉग्स को एग्रीगेट करके `query -> frequency` टेबल तैयार करते हैं।
3. **Workers:** नया Trie जनरेट करते हैं और उसका स्नैपशॉट **Trie DB (Key-Value Store / MongoDB)** में सेव कर देते हैं।
4. **Trie Cache:** नया Trie इन-मेमोरी डिस्ट्रीब्यूटेड कैश (Redis / Memcached) में लोड कर दिया जाता है।

---

## Step 4: Sharding & Scale-Out (जब डेटा बहुत बड़ा हो जाए)

<div style="margin-left:3rem">
<img src="/images/13-search-autocomplete/sharding.png" alt="Sharding" width="400">
</div>

यदि अंग्रेजी भाषा के सभी शब्द एक सर्वर की रैम में नहीं समाते:
- **Prefix Range Sharding:**
  - सर्वर 1: `a - m`
  - सर्वर 2: `n - z`
- यदि `a` से शुरू होने वाले शब्द बहुत ज्यादा हैं:
  - सब-शार्द्स: `aa - ag`, `ah - an`, `ao - az`.
- **Client-Side Optimization:** ब्राउज़र कैशिंग (`Cache-Control: private, max-age=3600`) का उपयोग करके बार-बार टाइप होने वाले समान प्रीफिक्स की रिक्वेस्ट नेटवर्क पर जाने से रोक दी जाती है।
