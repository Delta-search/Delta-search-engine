import deltabot_cli

# -----------------------------
# Categorize into Notelinks
# -----------------------------
def categorize_website(title, url, content):
    text = f"{title} {url} {content}".lower()

    categories = {
        "Introduction": ["introduction", "what is", "overview", "basics"],
        "Applications": ["uses", "applications", "benefits", "real-world"],
        "How it Works": ["how it works", "mechanism", "working", "function", "architecture"],
        "History": ["history", "origin", "inventor", "discovered", "timeline"],
        "Lists & Rankings": ["top", "best", "rankings", "comparison", "review", "list of"],
        "Future": ["future", "predictions", "upcoming"]
    }

    # Check for categories based on keywords in the text
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "Other"

# -----------------------------
# Main Categorization Function
# -----------------------------
def categorize_results(results):
    categorized = {}

    for url, result in results.items():
        # Safeguard for missing keys
        title = result.get('title', 'No title available')
        content = result.get('content', '')

        # Categorize based on content and keywords
        category = categorize_website(title, url, content)
        if category is None:
            continue

        if category not in categorized:
            categorized[category] = []

        categorized[category].append(result)

    # Sort each category by RankWell score (if available)
    for cat in categorized:
        categorized[cat] = sorted(
            categorized[cat],
            key=lambda x: x.get("score", 0),
            reverse=True
        )

    return categorized

# -----------------------------
# Entry Point
# -----------------------------
def main():
    query = input("Enter search query: ")
    seed_urls = [
        f"https://news.google.com/search?q={query.replace(' ', '+')}",
        f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    ]
    
    # Use the correct function to fetch the results
    results = deltabot_cli.run_deltabot(query, seed_urls)  # Correct function call
    
    categorized = categorize_results(results)

    if not categorized:
        print("\n⚠️ No relevant Notelinks found.")
        return

    print("\n📚 Notelinks:\n")
    for category, items in categorized.items():
        print(f"🗂️  {category}")
        print("-" * 80)
        for item in items:
            title = item.get('title', 'No title available')
            url = item.get('url', 'No URL available')

            print(f"Title: {title}")
            print(f"   URL: {url}")
            print(f"   RankWell: {item.get('rank', 'N/A')} | Score: {item.get('score', 'N/A')} | Label: {item.get('label', 'N/A')}")
            print(f"   Engagement: {item.get('engagement', 'N/A')} | Content Quality: {item.get('content_quality', 'N/A')}")
            print()
        print()

if __name__ == "__main__":
    main()
