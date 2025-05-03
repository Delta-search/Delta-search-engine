from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import notelinks_mechanism as notelinks  # Updated import

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Route to handle search queries
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')  # Get the search query from the request
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Set up seed URLs for crawling based on the query
    seed_urls = [
        f"https://news.google.com/search?q={query.replace(' ', '+')}",
        f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    ]
    
    # Run YogoolBot to fetch results
    results = notelinks.yogoolbot_cli.run_yogoolbot(query, seed_urls)


    # If no results found
    if not results:
        return jsonify({'error': 'No results found'}), 404

    # Categorize using notelinks_mechanism
    categorized = notelinks.categorize_results(results)

    return jsonify({'results': categorized})

# Start the Flask server
if __name__ == "__main__":
    app.run(debug=True)
