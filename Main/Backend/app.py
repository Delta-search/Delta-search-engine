import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
import notelinks_mechanism as notelinks

app = Flask(__name__)
CORS(app)

# Store crawled data in memory (temporary, non-persistent)
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
        latest_results[query.lower()] = categorized  # Store lowercase for consistency

    # Start crawling in the background
    threading.Thread(target=crawl_and_store).start()

    return jsonify({'message': f'Crawling in progress for "{query}". Please check back soon.'}), 202


@app.route('/results', methods=['GET'])
def results():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    categorized = latest_results.get(query.lower())
    if not categorized:
        return jsonify({'message': f'Results for "{query}" not available yet.'}), 404

    return jsonify(categorized)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
