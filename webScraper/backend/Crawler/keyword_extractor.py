"""
Pulls out tech skills, products, seasonal stuff, and demographics from pages.
Helps categorize what we find.
"""

import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Finds keywords in page content."""
    
    # Tech stuff to look for
    TECH_SKILLS = {
        # Programming Languages
        'languages': [
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift',
            'kotlin', 'go', 'rust', 'typescript', 'scala', 'perl', 'r', 'matlab',
            'dart', 'elixir', 'haskell', 'lua', 'objective-c', 'shell', 'bash',
            'powershell', 'sql', 'html', 'css', 'sass', 'less'
        ],
        
        # Frameworks & Libraries
        'frameworks': [
            'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt', 'django',
            'flask', 'fastapi', 'express', 'nest.js', 'spring', 'laravel',
            'rails', 'asp.net', 'symfony', 'flutter', 'react native', 'ionic',
            'electron', 'tailwind', 'bootstrap', 'material-ui', 'chakra ui',
            'jquery', 'backbone', 'ember', 'meteor', 'gatsby', 'redux', 'vuex',
            'mobx', 'rxjs', 'socket.io', 'graphql', 'rest api', 'grpc'
        ],
        
        # Databases
        'databases': [
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'firebase', 'supabase', 'mariadb',
            'oracle', 'sql server', 'sqlite', 'neo4j', 'couchdb', 'influxdb',
            'timescaledb', 'cockroachdb', 'memcached', 'etcd'
        ],
        
        # Cloud & DevOps
        'cloud': [
            'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean',
            'vercel', 'netlify', 'cloudflare', 'kubernetes', 'docker', 'jenkins',
            'gitlab ci', 'github actions', 'circleci', 'travis ci', 'terraform',
            'ansible', 'puppet', 'chef', 'vagrant', 'helm', 'istio', 'prometheus',
            'grafana', 'datadog', 'new relic', 'elk stack', 'splunk'
        ],
        
        # Data Science & AI
        'data_ai': [
            'machine learning', 'deep learning', 'neural networks', 'tensorflow',
            'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'scipy',
            'jupyter', 'matplotlib', 'seaborn', 'plotly', 'tableau', 'power bi',
            'spark', 'hadoop', 'airflow', 'kafka', 'nlp', 'computer vision',
            'opencv', 'yolo', 'bert', 'gpt', 'transformers', 'llm', 'rag',
            'langchain', 'llamaindex', 'vector database', 'pinecone', 'weaviate'
        ],
        
        # Mobile Development
        'mobile': [
            'ios', 'android', 'swift', 'swiftui', 'kotlin', 'java', 'flutter',
            'react native', 'xamarin', 'cordova', 'phonegap', 'ionic',
            'mobile development', 'app development'
        ],
        
        # Web Technologies
        'web': [
            'frontend', 'backend', 'full stack', 'responsive design', 'pwa',
            'spa', 'ssr', 'ssg', 'jamstack', 'headless cms', 'api', 'rest',
            'graphql', 'websocket', 'webrtc', 'service worker', 'web assembly',
            'wasm', 'oauth', 'jwt', 'authentication', 'authorization', 'cors',
            'cdn', 'caching', 'load balancing', 'microservices', 'serverless'
        ],
        
        # Testing & Quality
        'testing': [
            'jest', 'mocha', 'chai', 'jasmine', 'pytest', 'unittest', 'selenium',
            'cypress', 'playwright', 'puppeteer', 'testcafe', 'junit', 'testng',
            'cucumber', 'tdd', 'bdd', 'unit testing', 'integration testing',
            'e2e testing', 'test automation', 'ci/cd', 'code review', 'debugging'
        ],
        
        # Security
        'security': [
            'cybersecurity', 'penetration testing', 'ethical hacking', 'owasp',
            'ssl', 'tls', 'encryption', 'cryptography', 'oauth', 'saml',
            'two-factor authentication', '2fa', 'vulnerability', 'firewall',
            'vpn', 'security audit', 'compliance', 'gdpr', 'hipaa'
        ],
        
        # Blockchain & Web3
        'blockchain': [
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'solidity',
            'smart contracts', 'web3', 'defi', 'nft', 'dao', 'dapp', 'metamask',
            'polygon', 'solana', 'cardano', 'binance smart chain'
        ],
        
        # Other Skills
        'other': [
            'git', 'github', 'gitlab', 'bitbucket', 'version control', 'agile',
            'scrum', 'kanban', 'jira', 'confluence', 'slack', 'linux', 'unix',
            'windows server', 'networking', 'tcp/ip', 'dns', 'http', 'https',
            'ui/ux', 'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator'
        ]
    }
    
    # Product Categories
    PRODUCT_CATEGORIES = {
        # Electronics
        'electronics': [
            'laptop', 'desktop', 'computer', 'smartphone', 'phone', 'tablet',
            'ipad', 'macbook', 'chromebook', 'monitor', 'display', 'keyboard',
            'mouse', 'headphones', 'earbuds', 'speaker', 'camera', 'webcam',
            'microphone', 'router', 'modem', 'smart tv', 'streaming device',
            'gaming console', 'playstation', 'xbox', 'nintendo', 'switch',
            'graphics card', 'gpu', 'cpu', 'processor', 'ram', 'memory',
            'ssd', 'hard drive', 'storage', 'usb', 'charger', 'cable',
            'smartwatch', 'fitness tracker', 'drone', 'vr headset', 'ar glasses'
        ],
        
        # Home & Garden
        'home_garden': [
            'furniture', 'sofa', 'couch', 'chair', 'table', 'desk', 'bed',
            'mattress', 'pillow', 'blanket', 'bedding', 'curtains', 'rug',
            'lamp', 'lighting', 'decor', 'wall art', 'mirror', 'shelf',
            'storage', 'organizer', 'vacuum', 'air purifier', 'humidifier',
            'fan', 'heater', 'thermostat', 'smart home', 'alexa', 'google home',
            'plant', 'garden tools', 'lawn mower', 'grill', 'patio furniture',
            'outdoor', 'kitchen appliances', 'blender', 'coffee maker', 'toaster'
        ],
        
        # Clothing & Fashion
        'fashion': [
            'shirt', 't-shirt', 'blouse', 'dress', 'pants', 'jeans', 'shorts',
            'skirt', 'jacket', 'coat', 'sweater', 'hoodie', 'sweatshirt',
            'underwear', 'socks', 'shoes', 'sneakers', 'boots', 'sandals',
            'heels', 'accessories', 'bag', 'backpack', 'purse', 'wallet',
            'belt', 'hat', 'cap', 'scarf', 'gloves', 'sunglasses', 'jewelry',
            'watch', 'necklace', 'bracelet', 'ring', 'earrings', 'fashion',
            'style', 'clothing', 'apparel', 'outfit', 'wardrobe', 'designer'
        ],
        
        # Sports & Outdoors
        'sports': [
            'fitness', 'gym', 'workout', 'exercise', 'yoga', 'running',
            'cycling', 'bike', 'bicycle', 'treadmill', 'weights', 'dumbbells',
            'kettlebell', 'resistance bands', 'yoga mat', 'sports equipment',
            'basketball', 'football', 'soccer', 'baseball', 'tennis', 'golf',
            'swimming', 'camping', 'hiking', 'backpacking', 'tent', 'sleeping bag',
            'climbing', 'skiing', 'snowboarding', 'surfing', 'skateboard',
            'scooter', 'fishing', 'hunting', 'athletic', 'sportswear'
        ],
        
        # Toys & Games
        'toys_games': [
            'toy', 'game', 'puzzle', 'board game', 'card game', 'lego',
            'action figure', 'doll', 'stuffed animal', 'plush', 'building blocks',
            'educational toy', 'stem', 'robot', 'rc car', 'remote control',
            'video game', 'gaming', 'console', 'controller', 'minecraft',
            'fortnite', 'roblox', 'pokemon', 'marvel', 'star wars', 'disney',
            'playset', 'collectible', 'trading cards', 'hobby', 'craft'
        ],
        
        # Books & Media
        'books_media': [
            'book', 'ebook', 'audiobook', 'novel', 'fiction', 'non-fiction',
            'biography', 'textbook', 'cookbook', 'magazine', 'comic', 'manga',
            'kindle', 'audible', 'music', 'cd', 'vinyl', 'record', 'movie',
            'dvd', 'blu-ray', 'streaming', 'netflix', 'hulu', 'disney+',
            'prime video', 'spotify', 'apple music', 'podcast', 'literature'
        ],
        
        # Beauty & Health
        'beauty_health': [
            'skincare', 'makeup', 'cosmetics', 'lipstick', 'foundation',
            'mascara', 'eyeshadow', 'perfume', 'cologne', 'fragrance',
            'shampoo', 'conditioner', 'hair care', 'hair dryer', 'straightener',
            'curling iron', 'lotion', 'moisturizer', 'serum', 'cleanser',
            'sunscreen', 'vitamins', 'supplements', 'protein powder',
            'essential oils', 'aromatherapy', 'massage', 'spa', 'wellness',
            'health', 'medical', 'first aid', 'thermometer', 'blood pressure'
        ],
        
        # Food & Grocery
        'food_grocery': [
            'organic', 'gluten-free', 'vegan', 'vegetarian', 'keto', 'paleo',
            'snacks', 'candy', 'chocolate', 'chips', 'cookies', 'crackers',
            'nuts', 'dried fruit', 'protein bar', 'energy drink', 'coffee',
            'tea', 'beverage', 'water', 'juice', 'soda', 'alcohol', 'wine',
            'beer', 'grocery', 'pantry', 'condiments', 'spices', 'baking'
        ],
        
        # Baby & Kids
        'baby_kids': [
            'baby', 'infant', 'toddler', 'newborn', 'diaper', 'wipes',
            'baby formula', 'bottle', 'pacifier', 'stroller', 'car seat',
            'crib', 'bassinet', 'baby monitor', 'baby clothes', 'onesie',
            'bib', 'baby food', 'teething', 'nursery', 'parenting', 'maternity',
            'pregnancy', 'children', 'kids clothes', 'school supplies'
        ],
        
        # Pet Supplies
        'pets': [
            'pet', 'dog', 'cat', 'puppy', 'kitten', 'pet food', 'dog food',
            'cat food', 'pet treats', 'pet toys', 'leash', 'collar', 'pet bed',
            'litter box', 'cat litter', 'aquarium', 'fish tank', 'bird cage',
            'pet grooming', 'pet care', 'veterinary', 'pet supplies'
        ],
        
        # Automotive
        'automotive': [
            'car', 'vehicle', 'auto', 'automobile', 'truck', 'suv', 'sedan',
            'motorcycle', 'bike', 'scooter', 'electric vehicle', 'ev', 'tesla',
            'car parts', 'tires', 'wheels', 'oil', 'battery', 'car accessories',
            'dash cam', 'car seat', 'floor mats', 'tools', 'automotive'
        ],
        
        # Office & School
        'office_school': [
            'office supplies', 'notebook', 'pen', 'pencil', 'marker', 'paper',
            'folder', 'binder', 'stapler', 'tape', 'scissors', 'calculator',
            'planner', 'calendar', 'desk organizer', 'whiteboard', 'backpack',
            'lunch box', 'school supplies', 'textbook', 'stationery'
        ]
    }
    
    # Seasonal & Occasion Categories
    SEASONAL_THEMES = {
        'halloween': [
            'halloween', 'costume', 'trick or treat', 'pumpkin', 'spooky',
            'scary', 'horror', 'witch', 'ghost', 'skeleton', 'zombie',
            'vampire', 'candy', 'october', 'fall decoration', 'haunted'
        ],
        
        'christmas': [
            'christmas', 'xmas', 'holiday', 'santa', 'santa claus', 'reindeer',
            'elf', 'gift', 'present', 'ornament', 'tree', 'christmas tree',
            'wreath', 'lights', 'decoration', 'stocking', 'advent', 'carol',
            'nativity', 'snowman', 'winter', 'festive', 'jolly', 'merry'
        ],
        
        'thanksgiving': [
            'thanksgiving', 'turkey', 'harvest', 'autumn', 'fall', 'gratitude',
            'family dinner', 'stuffing', 'cranberry', 'pumpkin pie', 'november'
        ],
        
        'easter': [
            'easter', 'egg hunt', 'easter egg', 'bunny', 'easter basket',
            'spring', 'pastel', 'chocolate egg', 'resurrection', 'april'
        ],
        
        'valentines': [
            'valentine', "valentine's day", 'love', 'romance', 'romantic',
            'heart', 'roses', 'flowers', 'chocolate', 'date night', 'couple',
            'february 14', 'sweetheart', 'cupid'
        ],
        
        'back_to_school': [
            'back to school', 'school supplies', 'backpack', 'lunchbox',
            'classroom', 'student', 'teacher', 'september', 'academic',
            'textbook', 'school clothes', 'school shoes'
        ],
        
        'summer': [
            'summer', 'beach', 'pool', 'swimsuit', 'bikini', 'sunscreen',
            'flip flops', 'vacation', 'travel', 'barbecue', 'grill', 'outdoor',
            'camping', 'picnic', 'shorts', 'tank top', 'sunglasses'
        ],
        
        'new_year': [
            'new year', "new year's", 'resolution', 'party', 'champagne',
            'countdown', 'celebration', 'january', 'fresh start', 'goal'
        ],
        
        'mothers_day': [
            "mother's day", 'mom', 'mother', 'mama', 'mommy', 'gift for mom',
            'may', 'maternal', 'mom gift'
        ],
        
        'fathers_day': [
            "father's day", 'dad', 'father', 'papa', 'daddy', 'gift for dad',
            'june', 'paternal', 'dad gift'
        ],
        
        'black_friday': [
            'black friday', 'cyber monday', 'sale', 'deal', 'discount',
            'clearance', 'promotion', 'shopping', 'bargain', 'savings'
        ]
    }
    
    # Demographic Categories
    DEMOGRAPHICS = {
        'age_groups': [
            'baby', 'infant', 'toddler', 'kids', 'children', 'teen', 'teenager',
            'young adult', 'adult', 'senior', 'elderly', 'age', 'youth'
        ],
        
        'gender': [
            'men', 'women', 'boys', 'girls', 'male', 'female', 'unisex',
            'gender neutral', 'mens', 'womens', 'ladies', 'gentlemen'
        ],
        
        'lifestyle': [
            'professional', 'business', 'casual', 'formal', 'athletic',
            'active', 'lifestyle', 'luxury', 'budget', 'premium', 'eco-friendly',
            'sustainable', 'organic', 'handmade', 'artisan', 'vintage',
            'modern', 'minimalist', 'bohemian', 'rustic', 'industrial'
        ]
    }
    
    def __init__(self):
        """Initialize the keyword extractor."""
        # Build combined search patterns
        self._build_search_patterns()
    
    def _build_search_patterns(self):
        """Build regex patterns for efficient matching."""
        # Combine all tech skills into search pattern
        all_tech = []
        for category, skills in self.TECH_SKILLS.items():
            all_tech.extend(skills)
        
        # Combine all categories into search pattern
        all_categories = []
        for category, items in self.PRODUCT_CATEGORIES.items():
            all_categories.extend(items)
        
        # Combine seasonal themes
        all_seasonal = []
        for theme, keywords in self.SEASONAL_THEMES.items():
            all_seasonal.extend(keywords)
        
        # Combine demographics
        all_demographics = []
        for demo_type, keywords in self.DEMOGRAPHICS.items():
            all_demographics.extend(keywords)
        
        # Store for quick lookup
        self.all_keywords = {
            'tech': set(all_tech),
            'products': set(all_categories),
            'seasonal': set(all_seasonal),
            'demographics': set(all_demographics)
        }
    
    def extract_all(self, text: str, title: str = '') -> Dict[str, List[str]]:
        """
        Extract all keyword types from text.
        
        Args:
            text: Main content text
            title: Page title (given higher weight)
        
        Returns:
            {
                'tech_skills': [...],
                'product_categories': [...],
                'seasonal_themes': [...],
                'demographics': [...],
                'all_keywords': [...]
            }
        """
        # Combine title and text (title has more weight)
        full_text = (title + ' ' + title + ' ' + text).lower()
        
        results = {
            'tech_skills': self.extract_tech_skills(full_text),
            'product_categories': self.extract_product_categories(full_text),
            'seasonal_themes': self.extract_seasonal_themes(full_text),
            'demographics': self.extract_demographics(full_text),
        }
        
        # Combine all unique keywords
        all_found = set()
        for category, keywords in results.items():
            all_found.update(keywords)
        
        results['all_keywords'] = sorted(list(all_found))
        
        return results
    
    def extract_tech_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        found = set()
        text_lower = text.lower()
        
        for category, skills in self.TECH_SKILLS.items():
            for skill in skills:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found.add(skill)
        
        return sorted(list(found))
    
    def extract_product_categories(self, text: str) -> List[str]:
        """Extract product category keywords from text."""
        found = set()
        text_lower = text.lower()
        
        for category, items in self.PRODUCT_CATEGORIES.items():
            for item in items:
                pattern = r'\b' + re.escape(item.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found.add(item)
        
        return sorted(list(found))
    
    def extract_seasonal_themes(self, text: str) -> List[str]:
        """Extract seasonal/occasion themes from text."""
        found = set()
        text_lower = text.lower()
        
        for theme, keywords in self.SEASONAL_THEMES.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found.add(keyword)
        
        return sorted(list(found))
    
    def extract_demographics(self, text: str) -> List[str]:
        """Extract demographic keywords from text."""
        found = set()
        text_lower = text.lower()
        
        for demo_type, keywords in self.DEMOGRAPHICS.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found.add(keyword)
        
        return sorted(list(found))
    
    def get_category_scores(self, text: str, title: str = '') -> Dict[str, float]:
        """
        Get relevance scores for each category.
        
        Returns:
            {
                'electronics': 0.85,
                'fashion': 0.23,
                ...
            }
        """
        full_text = (title + ' ' + title + ' ' + text).lower()
        scores = {}
        
        # Score product categories
        for category, items in self.PRODUCT_CATEGORIES.items():
            matches = 0
            for item in items:
                pattern = r'\b' + re.escape(item.lower()) + r'\b'
                matches += len(re.findall(pattern, full_text))
            
            # Normalize by text length and category size
            word_count = len(full_text.split())
            if word_count > 0:
                score = matches / (word_count * 0.01)
                scores[category] = min(1.0, score)
            else:
                scores[category] = 0.0
        
        return scores
    
    def get_top_categories(self, text: str, title: str = '', top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Get top N product categories by relevance score.
        
        Returns:
            [('electronics', 0.85), ('home_garden', 0.42), ...]
        """
        scores = self.get_category_scores(text, title)
        
        # Sort by score descending
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N with non-zero scores
        return [(cat, score) for cat, score in sorted_scores[:top_n] if score > 0]
    
    def is_tech_related(self, text: str, threshold: int = 3) -> bool:
        """Check if page is tech-related based on keyword count."""
        skills = self.extract_tech_skills(text.lower())
        return len(skills) >= threshold
    
    def is_ecommerce_related(self, text: str, threshold: int = 5) -> bool:
        """Check if page is e-commerce related based on product keywords."""
        products = self.extract_product_categories(text.lower())
        return len(products) >= threshold
