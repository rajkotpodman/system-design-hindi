import { defineConfig } from 'vitepress'

const hindiSidebar = [
  {
    text: '🚀 बुनियादी और आर्किटेक्चर (Foundations)',
    items: [
      { text: '01: Zero से Millions तक Scaling', link: '/hi/01-scaling' },
      { text: '02: Back-of-the-envelope Estimation', link: '/hi/02-back-of-the-envelope-estimation' },
      { text: '03: System Design Interview Framework', link: '/hi/03-system-design-framework' },
    ]
  },
  {
    text: '🧱 डिस्ट्रीब्यूटेड बिल्डिंग ब्लॉक्स (Core Primitives)',
    items: [
      { text: '04: Rate Limiter Design', link: '/hi/04-rate-limiter' },
      { text: '05: Consistent Hashing', link: '/hi/05-consistent-hashing' },
      { text: '06: Key-Value Store Design', link: '/hi/06-key-value-store' },
      { text: '07: Unique ID Generator (Snowflake)', link: '/hi/07-unique-id-generator' },
      { text: '08: URL Shortener (TinyURL)', link: '/hi/08-url-shortener' },
    ]
  },
  {
    text: '⚡ वेब-स्केल और रियल-टाइम सिस्टम्स (Web-Scale Systems)',
    items: [
      { text: '09: Distributed Web Crawler', link: '/hi/09-web-crawler' },
      { text: '10: Notification System', link: '/hi/10-notification-system' },
      { text: '11: News Feed System', link: '/hi/11-news-feed-system' },
      { text: '12: Real-time Chat System', link: '/hi/12-chat-system' },
      { text: '13: Search Autocomplete (Trie)', link: '/hi/13-search-autocomplete' },
      { text: '14: YouTube / Video Streaming', link: '/hi/14-youtube' },
      { text: '15: Google Drive Cloud Storage', link: '/hi/15-google-drive' },
    ]
  },
  {
    text: '🗺️ जियोस्पाशियल और इन्फ्रास्ट्रक्चर (Geo & Infra)',
    items: [
      { text: '16: Proximity Service (Geohash)', link: '/hi/16-proximity-service' },
      { text: '17: Nearby Friends (Redis Pub/Sub)', link: '/hi/17-nearby-friends' },
      { text: '18: Google Maps Design', link: '/hi/18-google-maps' },
      { text: '19: Distributed Message Queue (Kafka)', link: '/hi/19-distributed-message-queue' },
      { text: '20: Metrics & Alerting System', link: '/hi/20-metrics-monitoring' },
    ]
  },
  {
    text: '💰 स्ट्रीमिंग, फिनटेक और एक्सचेंज (Fintech & Complex)',
    items: [
      { text: '21: Ad Click Event Aggregation', link: '/hi/21-ad-click-aggregation' },
      { text: '22: Hotel Reservation System', link: '/hi/22-hotel-reservation' },
      { text: '23: Distributed Email Service', link: '/hi/23-distributed-email' },
      { text: '24: S3-like Object Storage', link: '/hi/24-object-storage' },
      { text: '25: Real-time Gaming Leaderboard', link: '/hi/25-gaming-leaderboard' },
      { text: '26: Payment System (Double-Entry)', link: '/hi/26-payment-system' },
      { text: '27: Digital Wallet (ACID Transfers)', link: '/hi/27-digital-wallet' },
      { text: '28: Real-time Stock Exchange', link: '/hi/28-stock-exchange' },
    ]
  }
]

const englishSidebar = [
  {
    text: '🚀 Foundations & Architecture',
    items: [
      { text: 'Ch 01: Scale from 0 to Millions', link: '/en/01-scaling' },
      { text: 'Ch 02: Back of the Envelope Estimation', link: '/en/02-back-of-the-envelope-estimation' },
      { text: 'Ch 03: System Design Framework', link: '/en/03-system-design-framework' },
    ]
  },
  {
    text: '🧱 Distributed Core Primitives',
    items: [
      { text: 'Ch 04: Design a Rate Limiter', link: '/en/04-rate-limiter' },
      { text: 'Ch 05: Consistent Hashing', link: '/en/05-consistent-hashing' },
      { text: 'Ch 06: Key-Value Store', link: '/en/06-key-value-store' },
      { text: 'Ch 07: Unique ID Generator', link: '/en/07-unique-id-generator' },
      { text: 'Ch 08: URL Shortener', link: '/en/08-url-shortener' },
    ]
  },
  {
    text: '⚡ Web-Scale & Real-time Systems',
    items: [
      { text: 'Ch 09: Web Crawler', link: '/en/09-web-crawler' },
      { text: 'Ch 10: Notification System', link: '/en/10-notification-system' },
      { text: 'Ch 11: News Feed System', link: '/en/11-news-feed-system' },
      { text: 'Ch 12: Chat System', link: '/en/12-chat-system' },
      { text: 'Ch 13: Search Autocomplete', link: '/en/13-search-autocomplete' },
      { text: 'Ch 14: YouTube', link: '/en/14-youtube' },
      { text: 'Ch 15: Google Drive', link: '/en/15-google-drive' },
    ]
  },
  {
    text: '🗺️ Geospatial & Infrastructure',
    items: [
      { text: 'Ch 16: Proximity Service', link: '/en/16-proximity-service' },
      { text: 'Ch 17: Nearby Friends', link: '/en/17-nearby-friends' },
      { text: 'Ch 18: Google Maps', link: '/en/18-google-maps' },
      { text: 'Ch 19: Distributed Message Queue', link: '/en/19-distributed-message-queue' },
      { text: 'Ch 20: Metrics Monitoring & Alerting', link: '/en/20-metrics-monitoring' },
    ]
  },
  {
    text: '💰 Streaming, Fintech & Complex Systems',
    items: [
      { text: 'Ch 21: Ad Click Event Aggregation', link: '/en/21-ad-click-aggregation' },
      { text: 'Ch 22: Hotel Reservation System', link: '/en/22-hotel-reservation' },
      { text: 'Ch 23: Distributed Email Service', link: '/en/23-distributed-email' },
      { text: 'Ch 24: S3-like Object Storage', link: '/en/24-object-storage' },
      { text: 'Ch 25: Real-time Gaming Leaderboard', link: '/en/25-gaming-leaderboard' },
      { text: 'Ch 26: Payment System', link: '/en/26-payment-system' },
      { text: 'Ch 27: Digital Wallet', link: '/en/27-digital-wallet' },
      { text: 'Ch 28: Stock Exchange', link: '/en/28-stock-exchange' },
    ]
  }
]

// Determine base URL dynamically based on environment
const isGitHubActions = !!process.env.GITHUB_ACTIONS
const isBuild = process.argv.includes('build')
const base = process.env.VITE_BASE || (isGitHubActions ? '/system-design-hindi/' : (isBuild ? '/portal/' : '/'))

export default defineConfig({
  title: 'System Design Interview in Hindi',
  description: 'Complete 28-chapter System Design notes in Tech-Hinglish with live interactive simulators',
  lang: 'hi',
  base: base,
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: true,
  head: [
    [
      'script',
      { type: 'text/javascript' },
      `function googleTranslateElementInit() {
        if (window.google && window.google.translate) {
          new google.translate.TranslateElement({
            pageLanguage: 'hi',
            autoDisplay: false
          }, 'google_translate_element');
        }
      }`
    ],
    [
      'script',
      {
        type: 'text/javascript',
        src: 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'
      }
    ]
  ],

  locales: {
    root: {
      label: 'हिन्दी (Hinglish)',
      lang: 'hi',
      themeConfig: {
        nav: [
          { text: '🏠 होम', link: '/' },
          { text: '📚 28 चैप्टर्स', link: '/hi/01-scaling' },
          { text: '⚡ लाइव सिम्युलेटर', link: 'http://localhost:8000/' },
          { text: '📄 API Docs (Swagger)', link: 'http://localhost:8000/docs' },
        ],
        sidebar: hindiSidebar,
        search: {
          provider: 'local',
          options: {
            locales: {
              root: {
                translations: {
                  button: {
                    buttonText: 'सर्च करें...',
                    buttonAriaLabel: 'सर्च करें'
                  },
                  modal: {
                    noResultsText: 'कोई परिणाम नहीं मिला',
                    resetButtonTitle: 'रीसेट करें',
                    footer: {
                      selectText: 'चुनने के लिए',
                      navigateText: 'नेविगेट करने के लिए',
                      closeText: 'बंद करने के लिए'
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    en: {
      label: 'English',
      lang: 'en',
      link: '/en/',
      themeConfig: {
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Notes', link: '/en/01-scaling' },
          { text: 'Live Playground', link: 'http://localhost:8000/' },
          { text: 'API Docs', link: 'http://localhost:8000/docs' },
        ],
        sidebar: englishSidebar,
        search: {
          provider: 'local'
        }
      }
    }
  },

  themeConfig: {
    siteTitle: '⚡ System Design (हिन्दी)',
    socialLinks: [
      { icon: 'github', link: 'https://github.com/rajkotpodman/system-design-hindi' }
    ],
    footer: {
      message: 'System Design Interview Guide — Tech-Hinglish & Interactive Simulators',
      copyright: 'Free & Open Source for Developers & Students'
    }
  }
})
