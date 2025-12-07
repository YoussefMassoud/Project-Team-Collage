from flask import Flask, request, jsonify
import json
from flask_cors import CORS
# import gtts if needed later

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/fetch-post', methods=['POST'])
def fetch_post():
    data = request.json
    url = data.get('url')
    
    # Mocking fetching logic by returning data from post2.json
    try:
        with open('post2.json', 'r', encoding='utf-8') as f:
            post_data = json.load(f)
            # Update the URL in the mock data to match the requested one if valid
            if url:
               post_data['url'] = url
            return jsonify(post_data), 200
    except FileNotFoundError:
        return jsonify({"message": "Mock data file not found", "url": url}), 404
    except Exception as e:
        return jsonify({"message": f"Error loading mock data: {str(e)}", "url": url}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_post():
    data = request.json
    # Mock analysis result matching frontend interface
    analysis_result = {
        "topics": ["Customer Service", "Delay", "Complaint"],
        "issues": [
            "Long waiting time mentioned (2 hours)",
            "Unresponsive customer support",
            "Loyal customer thinking of leaving"
        ],
        "suggestions": [
            "Respond immediately with an apology",
            "Offer a compensation or discount code",
            "Escalate to a support manager"
        ],
        "comment_analysis": {
            "Positive": 5,
            "Negative": 80,
            "Neutral": 15
        },
        "sentiment": "Negative"
    }
    return jsonify(analysis_result), 200

if __name__ == '__main__':
    app.run(debug=True)
