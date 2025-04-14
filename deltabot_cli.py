import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import urllib.robotparser as robotparser
import time

# === Configuration ===
USER_AGENT = "DeltaBot/1.0"
MAX_PAGES = 20
DEPTH_LIMIT = 3

# RankWell quality score mapping
quality_map = {
    "Very Low Quality": 0.05,
    "Low Quality": 0.1,
    "Lower Medium Quality": 0.15,
    "Upper Medium Quality": 0.2,
    "High Quality": 0.3
}

# === Robots.txt Handling ===
robots_cache = {}

def can_fetch(url, user_agent=USER_AGENT):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    if base_url not in robots_cache:
        robots_url = urljoin(base_url, "/robots.txt")
        rp = robotparser.RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception as e:
            print(f"[DeltaBot] ⚠️ Could not fetch robots.txt for {base_url}: {e}")
            rp = None
        robots_cache[base_url] = rp

    rp = robots_cache.get(base_url)
    return rp.can_fetch(user_agent, url) if rp else True

# === Utility Functions ===

def fetch_page(url):
    headers = {"User-Agent": USER_AGENT}
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=5)
        load_time = time.time() - start_time
        if 'text/html' in response.headers.get('Content-Type', ''):
            return response.text, load_time
    except Exception as e:
        print(f"[DeltaBot] ⚠️ Failed to fetch {url}: {e}")
    return None, 0

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

def extract_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        if is_valid_url(full_url):
            links.add(full_url)
    return links

def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.string.strip() if soup.title and soup.title.string else "No title available"

def extract_text(html):
    return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)

def simulate_engagement(html):
    soup = BeautifulSoup(html, "html.parser")
    text_len = len(soup.get_text())
    link_count = len(soup.find_all("a"))
    return min(1.0, (text_len / 1000 + link_count / 50) / 2)

def estimate_content_quality(html, query):
    text = extract_text(html).lower()
    keywords = query.lower().split()
    score = sum(text.count(k) for k in keywords)
    return min(1.0, score / 10)

def calculate_quality_score(load_time, engagement, content_quality):
    load_score = max(0, 1 - (load_time / 5))  # Assume load_time=0 since not measured
    return 0.4 * load_score + 0.3 * engagement + 0.3 * content_quality

def label_quality(score):
    if score < 0.3:
        return "Very Low Quality"
    elif score < 0.45:
        return "Low Quality"
    elif score < 0.55:
        return "Lower Medium Quality"
    elif score < 0.7:
        return "Upper Medium Quality"
    else:
        return "High Quality"

# === DeltaBot Core Crawl + Rank Function ===

def run_deltabot(query, seed_urls, max_pages=MAX_PAGES, depth_limit=DEPTH_LIMIT):
    visited = set()
    queue = deque([(url, 0) for url in seed_urls])
    results = {}

    print(f"\n🔍 [DeltaBot] Starting crawl for query: '{query}'\n")

    while queue and len(results) < max_pages:
        url, depth = queue.popleft()
        if url in visited or depth > depth_limit:
            continue

        if not can_fetch(url):
            print(f"[DeltaBot] 🚫 Disallowed by robots.txt: {url}")
            continue

        print(f"🌐 Crawling: {url} | Depth: {depth}")
        html, load_time = fetch_page(url)
        if not html:
            continue

        visited.add(url)

        title = extract_title(html)
        content = extract_text(html)
        engagement = simulate_engagement(html)
        content_quality = estimate_content_quality(html, query)
        score = calculate_quality_score(load_time, engagement, content_quality)
        label = label_quality(score)

        results[url] = {
            "title": title,
            "url": url,
            "content": content,
            "score": round(score, 2),
            "label": label,
            "rank": quality_map[label],
            "engagement": round(engagement, 2),
            "content_quality": round(content_quality, 2),
        }

        for link in extract_links(url, html):
            if link not in visited:
                queue.append((link, depth + 1))

    print("\n✅ [DeltaBot] Crawl complete. Ranking results...\n")
    print_results(results)
    return results

# === CLI Output Formatter ===

def print_results(results):
    sorted_items = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)
    for i, (url, data) in enumerate(sorted_items, 1):
        print(f"{i}. {url}")
        print(f"   Rank: {data['rank']} | Label: {data['label']} | Score: {data['score']}")
        print(f"   Engagement: {data['engagement']} | Content Relevance: {data['content_quality']}")
        print("-" * 80)

# === CLI Entry Point ===

def main():
    query = input("Enter search query: ")
    
    # Set up seed URLs for crawling based on the query
    seed_urls = [
        f"https://news.google.com/search?q={query.replace(' ', '+')}",
        f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    ]
    
    # Fetch and categorize results using the correct function
    results = run_deltabot(query, seed_urls)

    if not results:
        print("\n⚠️ No relevant results found.")
        return

    print("\n📚 Results:\n")
    for url, data in results.items():
        print(f"Title: {data['title']}")
        print(f"   URL: {data['url']}")
        print(f"   RankWell: {data.get('rank', 'N/A')} | Score: {data.get('score', 'N/A')} | Label: {data.get('label', 'N/A')}")
        print(f"   Engagement: {data.get('engagement', 'N/A')} | Content Quality: {data.get('content_quality', 'N/A')}")
        print("-" * 80)

if __name__ == "__main__":
    main()
