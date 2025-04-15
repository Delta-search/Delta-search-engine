import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
import notelinks_mechanism as notelinks

app = Flask(__name__)
CORS(app)

# Store crawled data in memory temporarily (not production-safe)
latest_results = {}

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    def crawl_and_store():
        seed_urls = [
            f"https://news.google.com/search?q={query.replace(' ', '+')}",
            f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        ]
        results = notelinks.deltabot_cli.run_deltabot(query, seed_urls)
        categorized = notelinks.categorize_results(results)
        latest_results[query] = categorized

    # Start background thread
    threading.Thread(target=crawl_and_store).start()

    return jsonify({'message': f'Crawling in progress for "{query}". Please check back soon.'}), 202
