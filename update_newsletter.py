import requests
from bs4 import BeautifulSoup
import re
import datetime

# --- Configuration ---
SITEMAP_URLS = [
    "https://blog.bytebytego.com/sitemap/2026",
    "https://blog.bytebytego.com/sitemap/2025",
    "https://blog.bytebytego.com/sitemap/2024",
    "https://blog.bytebytego.com/sitemap/2023",
    "https://blog.bytebytego.com/sitemap/2022",
    "https://blog.bytebytego.com/sitemap/2021"
]

# --- Fetching Logic ---
episodes = []
ep_pattern = re.compile(r'(?:EP|Episode)\s*(\d+)', re.IGNORECASE)

print("🚀 Starting fetch process...")

for url in SITEMAP_URLS:
    try:
        response = requests.get(url)
        if response.status_code != 200: continue
            
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        
        for link in links:
            title = link.get_text().strip()
            href = link.get('href')
            
            if not title or not href: continue
                
            match = ep_pattern.search(title)
            if match:
                ep_num = int(match.group(1))
                # Clean up title: Remove "EP123: " prefix for cleaner display if desired, 
                # or keep it as is. Let's keep it raw but clean up extra spaces.
                episodes.append({'number': ep_num, 'title': title, 'url': href})
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")

# --- Deduplication ---
# Keep the entry with the longest title (usually the most descriptive)
unique_episodes = {}
for ep in episodes:
    num = ep['number']
    if num not in unique_episodes or len(ep['title']) > len(unique_episodes[num]['title']):
        unique_episodes[num] = ep

# --- Sorting ---
# Descending: Newest first (EP 200 -> EP 1)
desc_episodes = sorted(unique_episodes.values(), key=lambda x: x['number'], reverse=True)
# Ascending: Oldest first (EP 1 -> EP 200)
asc_episodes = sorted(unique_episodes.values(), key=lambda x: x['number'])

total_eps = len(desc_episodes)
last_updated = datetime.datetime.now().strftime('%Y-%m-%d')

# --- Markdown Generation ---
md = f"""
# 📚 ByteByteGo Newsletter Archive

[![Auto-Update](https://github.com/d3v3nx/ByteByteGo-Newsletters/actions/workflows/daily_update.yml/badge.svg)](https://github.com/d3v3nx/ByteByteGo-Newsletters/actions/workflows/daily_update.yml)
![Episode Count](https://img.shields.io/badge/Episodes-{total_eps}-blue)
![Last Updated](https://img.shields.io/badge/Last%20Updated-{last_updated}-green)

> **Note:** This is an unofficial automated archive to help developers find episodes easily. All content belongs to [ByteByteGo](https://blog.bytebytego.com/).

---

## 🔥 Latest Episodes (Descending)
*Newest episodes appear at the top.*

| Episode | Title | Read |
| :---: | :--- | :---: |
"""

# Generate Descending Table
for ep in desc_episodes:
    md += f"| **EP{ep['number']}** | [{ep['title']}]({ep['url']}) | [🔗]({ep['url']}) |\n"

md += """
---

<details>
<summary><h2>📜 Chronological Archive (Ascending: EP1 → Present)</h2> (Click to Expand)</summary>

<br>

| Episode | Title | Link |
| :---: | :--- | :---: |
"""

# Generate Ascending Table (Hidden by default)
for ep in asc_episodes:
    md += f"| EP{ep['number']} | [{ep['title']}]({ep['url']}) | [👉]({ep['url']}) |\n"

md += """
</details>

---
### ⚠️ Disclaimer
This repository is not affiliated with ByteByteGo or Alex Xu. It is a personal project to index public newsletter links. 
<br>
<sub>Generated automatically by GitHub Actions.</sub>
"""

# --- Save to File ---
with open("README.md", "w", encoding="utf-8") as f:
    f.write(md)

print(f"✅ README.md updated with {total_eps} episodes.")