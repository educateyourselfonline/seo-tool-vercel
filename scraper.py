print("Importing scraper.py...")
import requests
from bs4 import BeautifulSoup
from collections import Counter

def fetch_html(url):
    print(f"scraper.py: Fetching HTML from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"scraper.py: Error fetching {url}: {e}")
        return None

def extract_keywords(html_content):
    print("scraper.py: Extracting keywords...")
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    words = text.lower().split()
    keyword_counts = Counter(words)
    common_keywords = [word for word, count in keyword_counts.most_common(20) if len(word) > 3]
    print(f"scraper.py: Extracted keywords: {common_keywords}")
    return common_keywords

def extract_content(html_content, keywords):
    print("scraper.py: Extracting content...")
    if not html_content or not keywords:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    relevant_content = " ".join(p.get_text() for p in paragraphs if any(keyword in p.get_text().lower() for keyword in keywords))
    print(f"scraper.py: Extracted content (first 100 chars): {relevant_content[:100]}")
    return relevant_content
