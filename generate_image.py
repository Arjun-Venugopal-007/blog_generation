import os
import re
import random
import hashlib
import logging
from typing import Optional, List, Dict
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read API keys
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
OPENVERSE_API_KEY = os.getenv("OPENVERSE_API_KEY")

if not UNSPLASH_ACCESS_KEY and not OPENVERSE_API_KEY:
    raise ValueError("❌ Both UNSPLASH_ACCESS_KEY and OPENVERSE_API_KEY are missing! Please check your .env file.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set headers
HEADERS = {
    'User-Agent': 'StudentBlogApp/1.0 (contact@youruniversity.edu)'
}

def fetch_unsplash_image(query: str, orientation: str = "landscape") -> Dict:
    """Fetch image from Unsplash"""
    try:
        clean_query = query.strip().replace(' ', '+')
        url = "https://api.unsplash.com/search/photos"
        params = {
            'query': clean_query,
            'per_page': 20,
            'orientation': orientation,
            'order_by': 'relevant',
            'content_filter': 'high',
            'client_id': UNSPLASH_ACCESS_KEY
        }
        
        logger.info(f"🔍 Searching Unsplash for: '{query}'")
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])
        
        if results:
            quality_images = [img for img in results if img.get("width", 0) >= 800]
            selected_images = quality_images if quality_images else results
            image = random.choice(selected_images)
            
            image_url = image.get("urls", {}).get("regular", image.get("urls", {}).get("small"))
            author = image.get("user", {}).get("name", "Unknown")
            attribution = f"Photo by {author} on Unsplash"
            
            return {"url": image_url, "attribution": attribution, "source": "Unsplash"}
        
        return {"url": None, "attribution": None, "source": "Unsplash"}
        
    except Exception as e:
        logger.error(f"❌ Unsplash fetch failed for '{query}': {e}")
        return {"url": None, "attribution": None, "source": "Unsplash"}

def fetch_openverse_image(query: str) -> Dict:
    """Fetch image from Openverse"""
    try:
        clean_query = query.strip().replace(' ', '+')
        url = "https://api.openverse.engineering/v1/images/"
        params = {
            'q': clean_query,
            'page_size': 20,
            'license_type': 'all-cc',
            'source': 'wordpress, flickr'
        }
        
        logger.info(f"🔍 Searching Openverse for: '{query}'")
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])
        
        if results:
            image = random.choice(results)
            image_url = image.get("url")
            author = image.get("creator", {}).get("name", "Unknown")
            attribution = f"Image by {author} on Openverse"
            
            return {"url": image_url, "attribution": attribution, "source": "Openverse"}
        
        return {"url": None, "attribution": None, "source": "Openverse"}
        
    except Exception as e:
        logger.error(f"❌ Openverse fetch failed for '{query}': {e}")
        return {"url": None, "attribution": None, "source": "Openverse"}

def fetch_wikipedia_image(query: str) -> Dict:
    """Fetch image from Wikipedia"""
    try:
        clean_query = query.strip().replace(' ', '_')
        url = f"https://en.wikipedia.org/api/rest_v1/page/media-list/{clean_query}"
        
        logger.info(f"🔍 Searching Wikipedia for: '{query}'")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])
        
        if items:
            valid_images = [item for item in items if item.get("type") == "image" and item.get("srcset")]
            if valid_images:
                image = random.choice(valid_images)
                image_url = image.get("srcset", [{}])[0].get("src")
                attribution = image.get("caption", "Image from Wikipedia")
                
                return {"url": f"https:{image_url}", "attribution": attribution, "source": "Wikipedia"}
        
        return {"url": None, "attribution": None, "source": "Wikipedia"}
        
    except Exception as e:
        logger.error(f"❌ Wikipedia fetch failed for '{query}': {e}")
        return {"url": None, "attribution": None, "source": "Wikipedia"}

def download_image(url: str, filename: str) -> Optional[str]:
    """Download image to static directory"""
    try:
        static_dir = Path("static/images")
        static_dir.mkdir(parents=True, exist_ok=True)
        image_path = static_dir / filename

        logger.info(f"📥 Downloading image from: {url}")
        with requests.get(url, headers=HEADERS, stream=True, timeout=15) as response:
            response.raise_for_status()
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return f"/static/images/{filename}"
    except Exception as e:
        logger.error(f"❌ Failed to download image: {e}")
        return None

def generate_images_for_title_and_description(title: str, description: str, num_images: int = 6) -> List[Dict]:
    """Generate images based on title and description keywords"""
    try:
        generated_images = []
        
        # Extract keywords from description
        words = re.findall(r'\b[A-Za-z]{4,}\b', description.lower())
        common_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'said', 'each',
            'which', 'their', 'time', 'about', 'would', 'there', 'could', 'other', 'more',
            'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your',
            'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made',
            'before', 'here', 'through', 'when', 'where', 'much', 'some', 'these', 'many',
            'then', 'them', 'well', 'were'
        }
        
        keywords = [word for word in set(words) if word not in common_words][:5]
        queries = [title] + [f"{title} {keyword}" for keyword in keywords]
        
        while len(queries) < num_images:
            queries.append(f"{title} concept")
        
        sources = ["Unsplash", "Openverse", "Wikipedia"]
        for i, query in enumerate(queries[:num_images]):
            logger.info(f"🎨 Generating image {i+1}/{num_images} for query: {query}")
            
            # Try each source until we get a valid image
            for source in sources:
                result = {}
                if source == "Unsplash" and UNSPLASH_ACCESS_KEY:
                    result = fetch_unsplash_image(query)
                elif source == "Openverse" and OPENVERSE_API_KEY:
                    result = fetch_openverse_image(query)
                elif source == "Wikipedia":
                    result = fetch_wikipedia_image(query)
                
                if result.get("url"):
                    filename = f"blog_{hashlib.md5(f'{title}_{query}_{i}'.encode()).hexdigest()}.jpg"
                    local_path = download_image(result["url"], filename)
                    
                    if local_path:
                        generated_images.append({
                            'path': local_path,
                            'query': query,
                            'attribution': result["attribution"],
                            'source': result["source"],
                            'index': i
                        })
                        logger.info(f"✅ Image generated from {source} for: {query}")
                        break
            
            if not any(img['query'] == query for img in generated_images):
                logger.warning(f"⚠ No image found for: {query}")
        
        return generated_images
        
    except Exception as e:
        logger.error(f"❌ Failed to generate images: {e}")
        return []