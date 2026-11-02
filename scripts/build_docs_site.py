"""
Build and configure the VitePress documentation website with i18n (Tech-Hinglish & English).
"""

import os
import shutil
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
PUBLIC_IMAGES = DOCS_DIR / "public" / "images"

CHAPTERS = [
    ("01. Scaling", "01-scaling", "Ch 01: Scaling from 0 to Millions", "01: Zero से Millions तक Scaling"),
    ("02. Back Of the Envelope Estimation", "02-back-of-the-envelope-estimation", "Ch 02: Back-of-the-envelope Estimation", "02: Back-of-the-envelope Estimation"),
    ("03. System Design Framework", "03-system-design-framework", "Ch 03: System Design Interview Framework", "03: System Design Interview Framework"),
    ("04. Rate Limiter", "04-rate-limiter", "Ch 04: Design a Rate Limiter", "04: Rate Limiter Design"),
    ("05. Consistent Hashing", "05-consistent-hashing", "Ch 05: Consistent Hashing", "05: Consistent Hashing"),
    ("06. Key-Value Store", "06-key-value-store", "Ch 06: Key-Value Store", "06: Key-Value Store Design"),
    ("07. Unique-Id Generator", "07-unique-id-generator", "Ch 07: Unique ID Generator", "07: Distributed Unique ID Generator"),
    ("08. URL Shortener", "08-url-shortener", "Ch 08: URL Shortener", "08: URL Shortener (TinyURL)"),
    ("09. Web Crawler", "09-web-crawler", "Ch 09: Web Crawler", "09: Web Crawler Design"),
    ("10. Notification System", "10-notification-system", "Ch 10: Notification System", "10: Notification System"),
    ("11. News Feed System", "11-news-feed-system", "Ch 11: News Feed System", "11: News Feed System"),
    ("12. Chat System", "12-chat-system", "Ch 12: Real-time Chat System", "12: Real-time Chat System"),
    ("13. Search Autocomplete", "13-search-autocomplete", "Ch 13: Search Autocomplete", "13: Search Autocomplete System"),
    ("14. Youtube", "14-youtube", "Ch 14: YouTube Video Streaming", "14: YouTube Video Streaming"),
    ("15. Google Drive", "15-google-drive", "Ch 15: Google Drive Cloud Storage", "15: Google Drive Cloud Storage"),
    ("16. Proximity Service", "16-proximity-service", "Ch 16: Proximity Service", "16: Proximity Service (Geohash)"),
    ("17. Nearby Friends", "17-nearby-friends", "Ch 17: Nearby Friends", "17: Nearby Friends (Redis Pub/Sub)"),
    ("18. Google Maps", "18-google-maps", "Ch 18: Google Maps", "18: Google Maps Design"),
    ("19. Distributed Message Queue", "19-distributed-message-queue", "Ch 19: Distributed Message Queue", "19: Message Queue (Kafka)"),
    ("20. Metrics Monitoring and Alerting System", "20-metrics-monitoring", "Ch 20: Metrics Monitoring & Alerting", "20: Metrics & Alerting System"),
    ("21. Ad Click Event Aggregation", "21-ad-click-aggregation", "Ch 21: Ad Click Event Aggregation", "21: Ad Click Aggregation (Streaming)"),
    ("22. Hotel Reservation System", "22-hotel-reservation", "Ch 22: Hotel Reservation System", "22: Hotel Reservation (ACID & Saga)"),
    ("23. Distributed Email Service", "23-distributed-email", "Ch 23: Distributed Email Service", "23: Distributed Email Service"),
    ("24. S3-like Object Storage", "24-object-storage", "Ch 24: S3-like Object Storage", "24: S3-like Object Storage"),
    ("25. Real-time Gaming Leaderboard", "25-gaming-leaderboard", "Ch 25: Real-time Gaming Leaderboard", "25: Real-time Gaming Leaderboard"),
    ("26. Payment System", "26-payment-system", "Ch 26: Payment System", "26: Payment System (Ledger & Idempotency)"),
    ("27.  Digital Wallet", "27-digital-wallet", "Ch 27: Digital Wallet", "27: Digital Wallet (Atomic Transfers)"),
    ("28. Stock Exchange", "28-stock-exchange", "Ch 28: Real-time Stock Exchange", "28: Real-time Stock Exchange"),
]

def setup_directories():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "hi").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "en").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / ".vitepress").mkdir(parents=True, exist_ok=True)
    PUBLIC_IMAGES.mkdir(parents=True, exist_ok=True)

def sanitize_markdown(content: str, slug: str) -> str:
    # Replace relative image paths
    content = re.sub(r'(src=["\'])\.?/?images/', rf'\1/images/{slug}/', content)
    content = re.sub(r'(\!\[.*?\]\()\s*\.?/?images/', rf'\1/images/{slug}/', content)
    # Fix broken tag typos in original notes
    content = re.sub(r'<div style="margin-left:2rem">\s*(<img[^>]+>)\s*<div>', r'<div>\n\1\n</div>', content)
    # Unindent block HTML tags so markdown parser doesn't treat them as raw code blocks
    content = re.sub(r'^[ \t]+<(/?div[^>]*)>', r'<\1>', content, flags=re.MULTILINE)
    content = re.sub(r'^[ \t]+<(/?p[^>]*)>', r'<\1>', content, flags=re.MULTILINE)
    content = re.sub(r'^[ \t]+(<img[^>]+>)', r'\1', content, flags=re.MULTILINE)
    return content

def copy_images_and_sync_chapters():
    for folder_name, slug, title_en, title_hi in CHAPTERS:
        src_folder = ROOT / folder_name
        if not src_folder.exists():
            continue
        
        # Copy images
        src_images = src_folder / "images"
        dest_images = PUBLIC_IMAGES / slug
        dest_images.mkdir(parents=True, exist_ok=True)
        if src_images.exists():
            for img in src_images.glob("*"):
                if img.is_file():
                    shutil.copy2(img, dest_images / img.name)

        # Sync English file
        readme_src = src_folder / "Readme.md"
        if not readme_src.exists():
            readme_src = src_folder / "README.md"
        
        if readme_src.exists():
            content = readme_src.read_text(encoding="utf-8", errors="replace")
            content = sanitize_markdown(content, slug)
            (DOCS_DIR / "en" / f"{slug}.md").write_text(content, encoding="utf-8")
        
        # Sync Hindi file if exists
        hi_src = src_folder / "Readme.hi.md"
        if not hi_src.exists():
            hi_src = src_folder / "README.hi.md"
        hi_dest = DOCS_DIR / "hi" / f"{slug}.md"
        if hi_src.exists():
            content = hi_src.read_text(encoding="utf-8", errors="replace")
            content = sanitize_markdown(content, slug)
            hi_dest.write_text(content, encoding="utf-8")
        elif readme_src.exists():
            # Fallback with English content until translated
            en_content = (DOCS_DIR / "en" / f"{slug}.md").read_text(encoding="utf-8")
            banner = f"> [!NOTE]\n> **{title_hi}** — इसका संपूर्ण Tech-Hinglish अनुवाद तैयार किया जा रहा है। नीचे संदर्भ के लिए मूल सामग्री दी गई है।\n\n"
            hi_dest.write_text(banner + en_content, encoding="utf-8")

if __name__ == "__main__":
    setup_directories()
    copy_images_and_sync_chapters()
    print("Docs directories and images synchronized successfully.")
