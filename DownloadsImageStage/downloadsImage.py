import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
BASE_URL = "https://api.pexels.com/v1/search"
HEADERS = {
    "Authorization": PEXELS_API_KEY
}

def read_search_terms(filepath):
    """Reads the content of the file to use as search terms."""
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    return content

def search_images(query, per_page=1):
    """Searches for images on Pexels API."""
    if not query:
        return []
    
    # Pexels search works best with keywords, so we might want to truncate or extract keywords
    # For now, let's try using the first few words or the whole sentence if it's short.
    # If the text is very long, Pexels might return nothing.
    # Let's take the first 10 words as a heuristic for a search query if it's long.
    words = query.split()
    search_query = " ".join(words[:10]) 
    
    params = {
        "query": search_query,
        "per_page": per_page
    }
    
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json().get('photos', [])
    else:
        print(f"Error searching images: {response.status_code} - {response.text}")
        return []

def download_image(url, folder, filename):
    """Downloads an image from a URL."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download {url}")

def main():
    input_file = 'file.txt'
    output_folder = 'downloaded_images'
    
    print(f"Reading from {input_file}...")
    content = read_search_terms(input_file)
    
    if content:
        print(f"Searching for images matching: {content[:50]}...")
        photos = search_images(content, per_page=3) # Get top 3 images
        
        if photos:
            print(f"Found {len(photos)} images. Downloading...")
            for i, photo in enumerate(photos):
                image_url = photo['src']['original'] # Use original size or 'large'
                filename = f"image_{i+1}.jpg"
                download_image(image_url, output_folder, filename)
        else:
            print("No images found.")
    else:
        print("No content found in file.")

if __name__ == "__main__":
    main()
