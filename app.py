from flask import Flask, request, jsonify
from scraper import fetch_html, extract_keywords, extract_content
from pdf_generator import generate_pdf_report
import os
import requests  # For making API calls
from flask_cors import CORS
from transformers import pipeline  # Import Hugging Face pipeline
import time  # Import the time module
import tempfile # Import tempfile for Vercel

app = Flask(__name__)
CORS(app)

# Google PageSpeed Insights API Key (Replace with your actual key)
API_KEY = os.environ.get("AIzaSyA36RMGPw6CGZcqgmu8n1z8TT6L6IBFXCQ") # Get from env var with default
API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Hugging Face Sentiment Analysis Pipeline
# sentiment_analyzer = pipeline("sentiment-analysis")

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        html_content = fetch_html(url)
        if not html_content:
            return jsonify({'error': 'Failed to fetch HTML'}), 500

        keywords = extract_keywords(html_content)
        content = extract_content(html_content, keywords)

        # Handle PDF path for Vercel (using /tmp) and default for others
        if 'VERCEL' in os.environ:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf_file = tmp_file.name
                generate_pdf_report(keywords, content, pdf_file)
        else:
            pdf_file = generate_pdf_report(keywords, content, "report.pdf")

        # Make API call to Google PageSpeed Insights
        api_request_url = f"{API_URL}?url={url}&key={API_KEY}"
        try:
            api_response = requests.get(api_request_url, timeout=10).json() # Added timeout
        except requests.exceptions.Timeout:
            print("Google PageSpeed Insights API timed out.")
            api_response = {}
        except requests.exceptions.RequestException as e:
            print(f"Error during Google PageSpeed Insights API call: {e}")
            api_response = {}

        # Extract relevant data (e.g., performance score)
        performance_score = api_response.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', None)

        # Perform sentiment analysis using Hugging Face
        sentiment_result = None
        # if content:
        #     try:
        #         sentiment_output = sentiment_analyzer(content[:512])[0] # Limit input length for some models
        #         sentiment_result = sentiment_output['label']
        #     except Exception as e:
        #         print(f"Sentiment Analysis Error: {e}")

        # Create response data including PDF path and API data
        response_data = {
            'report_path': pdf_file,
            'keywords': keywords,
            'content': content,
            'performance_score': performance_score,
            # 'sentiment': sentiment_result # Comment out sentiment
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Analysis Error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # Added host and port for proper serving in Spaces
