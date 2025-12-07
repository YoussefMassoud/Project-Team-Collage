import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Pexels API configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
PEXELS_API_URL = 'https://api.pexels.com/v1/search'

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)


def read_keywords_from_file(filepath):
    """Read and extract keywords from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Split by whitespace, newlines, commas, etc.
            keywords = [word.strip() for word in content.replace(',', ' ').split() if word.strip()]
            return keywords
    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def search_pexels_photos(query, per_page=5):
    """Search for photos on Pexels API."""
    if not PEXELS_API_KEY:
        raise Exception("Pexels API key not found. Please set PEXELS_API_KEY in .env file")
    
    headers = {
        'Authorization': PEXELS_API_KEY
    }
    
    params = {
        'query': query,
        'per_page': per_page,
        'page': 1
    }
    
    try:
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching Pexels: {e}")
        return None


def download_image(url, filename):
    """Download an image from a URL and save it locally."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """Process the file and download images."""
    try:
        # Check if file was uploaded or use existing file.txt
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            # Use default file.txt
            filepath = 'file.txt'
            if not os.path.exists(filepath):
                flash('No file uploaded and file.txt not found', 'error')
                return redirect(url_for('index'))
        
        # Read keywords from file
        keywords = read_keywords_from_file(filepath)
        
        if not keywords:
            flash('No keywords found in file', 'warning')
            return redirect(url_for('index'))
        
        # Process each keyword and download images
        downloaded_images = []
        errors = []
        
        for keyword in keywords[:5]:  # Limit to first 5 keywords to avoid rate limiting
            try:
                # Search for photos
                results = search_pexels_photos(keyword, per_page=2)
                
                if results and 'photos' in results:
                    for idx, photo in enumerate(results['photos']):
                        # Download medium-sized image
                        image_url = photo['src']['medium']
                        filename = f"{keyword}_{idx + 1}_{photo['id']}.jpg"
                        
                        downloaded_path = download_image(image_url, filename)
                        
                        if downloaded_path:
                            downloaded_images.append({
                                'filename': filename,
                                'keyword': keyword,
                                'photographer': photo['photographer'],
                                'url': photo['url']
                            })
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.2)
                else:
                    errors.append(f"No results found for: {keyword}")
                    
            except Exception as e:
                errors.append(f"Error processing '{keyword}': {str(e)}")
        
        if downloaded_images:
            flash(f'Successfully downloaded {len(downloaded_images)} images!', 'success')
        
        if errors:
            for error in errors:
                flash(error, 'warning')
        
        return render_template('results.html', images=downloaded_images, errors=errors)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/results')
def results():
    """Display results page."""
    # List all downloaded images
    images = []
    if os.path.exists(app.config['DOWNLOAD_FOLDER']):
        for filename in os.listdir(app.config['DOWNLOAD_FOLDER']):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                images.append({'filename': filename})
    
    return render_template('results.html', images=images, errors=[])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
