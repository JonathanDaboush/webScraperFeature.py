"""
Test Keyword Extraction Functionality

This script demonstrates the enhanced keyword extraction capabilities
for tech skills, product categories, seasonal themes, and demographics.
"""

import sys
import os
import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import just the class we need directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "keyword_extractor",
    os.path.join(current_dir, "Crawler", "keyword_extractor.py")
)
keyword_extractor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(keyword_extractor_module)
KeywordExtractor = keyword_extractor_module.KeywordExtractor


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_tech_page():
    """Test extraction from a tech-related page"""
    print_section("TEST 1: Tech Skills Extraction")
    
    sample_text = """
    Senior Full Stack Developer - Remote Position
    
    We're looking for an experienced developer with expertise in:
    - Python, JavaScript, TypeScript
    - React, Next.js, Node.js, Django, Flask
    - PostgreSQL, MongoDB, Redis
    - AWS, Docker, Kubernetes
    - Git, CI/CD, Jenkins
    
    Experience with machine learning, TensorFlow, and PyTorch is a plus.
    Must have strong skills in REST API design, GraphQL, and microservices architecture.
    """
    
    extractor = KeywordExtractor()
    results = extractor.extract_all(sample_text, "Full Stack Developer Job")
    
    print("\n📊 TECH SKILLS FOUND:")
    for skill in results['tech_skills'][:20]:
        print(f"  ✓ {skill}")
    
    print(f"\n📈 TOTAL: {len(results['tech_skills'])} tech skills detected")
    print(f"🎯 IS TECH-RELATED: {extractor.is_tech_related(sample_text)}")
    

def test_ecommerce_page():
    """Test extraction from an e-commerce page"""
    print_section("TEST 2: E-Commerce Product Categories")
    
    sample_text = """
    Gaming Laptop - RTX 4080 Graphics Card
    
    High-performance laptop for gaming and content creation.
    Includes:
    - Intel Core i9 processor
    - 32GB RAM
    - 1TB SSD storage
    - Mechanical keyboard
    - RGB mouse included
    - Premium headphones
    
    Also available: wireless router, external monitor, USB hub, and gaming chair.
    Perfect for students, professionals, and gamers.
    """
    
    extractor = KeywordExtractor()
    results = extractor.extract_all(sample_text, "Gaming Laptop - Electronics")
    
    print("\n🛍️ PRODUCT CATEGORIES FOUND:")
    for category in results['product_categories'][:20]:
        print(f"  ✓ {category}")
    
    print("\n🎯 TOP CATEGORIES WITH SCORES:")
    top_cats = extractor.get_top_categories(sample_text, "Gaming Laptop", top_n=5)
    for category, score in top_cats:
        print(f"  📦 {category}: {score:.3f}")
    
    print(f"\n📈 TOTAL: {len(results['product_categories'])} product keywords")
    print(f"🛒 IS E-COMMERCE: {extractor.is_ecommerce_related(sample_text)}")


def test_seasonal_page():
    """Test extraction of seasonal themes"""
    print_section("TEST 3: Seasonal & Occasion Themes")
    
    sample_text = """
    Christmas Sale - Holiday Decorations!
    
    Get ready for the holidays with our amazing selection:
    - Christmas trees and ornaments
    - Santa costumes for kids
    - Halloween costumes clearance
    - Valentine's Day gift ideas
    - Easter bunny decorations
    - Back to school supplies
    
    Perfect gifts for mom on Mother's Day and dad on Father's Day.
    Don't miss our Black Friday deals!
    """
    
    extractor = KeywordExtractor()
    results = extractor.extract_all(sample_text, "Holiday Sale 2024")
    
    print("\n🎄 SEASONAL THEMES FOUND:")
    for theme in results['seasonal_themes']:
        print(f"  ✓ {theme}")
    
    print("\n👥 DEMOGRAPHICS FOUND:")
    for demo in results['demographics']:
        print(f"  ✓ {demo}")
    
    print(f"\n📈 TOTAL: {len(results['seasonal_themes'])} seasonal keywords")


def test_fashion_page():
    """Test fashion/clothing category extraction"""
    print_section("TEST 4: Fashion & Apparel")
    
    sample_text = """
    Women's Summer Fashion Collection
    
    New arrivals for ladies:
    - Dresses, skirts, and blouses
    - Jeans, shorts, and pants
    - Sneakers, sandals, and heels
    - Designer handbags and purses
    - Jewelry: necklaces, bracelets, earrings
    - Sunglasses and accessories
    
    Men's section: shirts, jackets, shoes
    Kids clothing: boys and girls apparel
    
    Unisex items available. Perfect for casual and formal occasions.
    """
    
    extractor = KeywordExtractor()
    results = extractor.extract_all(sample_text, "Fashion Store")
    
    print("\n👗 PRODUCT CATEGORIES:")
    fashion_items = [k for k in results['product_categories'] if k in 
                     extractor.PRODUCT_CATEGORIES['fashion']]
    for item in fashion_items[:15]:
        print(f"  ✓ {item}")
    
    print("\n🎯 TOP CATEGORIES:")
    top_cats = extractor.get_top_categories(sample_text, "Fashion Store", top_n=5)
    for category, score in top_cats:
        print(f"  📦 {category}: {score:.3f}")


def test_mixed_content():
    """Test extraction from mixed content"""
    print_section("TEST 5: Mixed Content Analysis")
    
    sample_text = """
    Tech Gifts for Kids This Christmas
    
    Best electronics and toys for children:
    - Educational robot with Python programming
    - Nintendo Switch gaming console
    - iPad tablet for learning
    - LEGO robotics kit with coding
    - Smart watch for kids
    - Minecraft and Roblox gift cards
    
    Perfect for boys and girls aged 8-14.
    Halloween costumes also on sale!
    
    Parents love these STEM toys that teach JavaScript and scratch programming.
    """
    
    extractor = KeywordExtractor()
    results = extractor.extract_all(sample_text, "Tech Gifts for Kids")
    
    print("\n🔧 TECH SKILLS:")
    print(f"  {', '.join(results['tech_skills'][:10])}")
    
    print("\n🎁 PRODUCT CATEGORIES:")
    print(f"  {', '.join(results['product_categories'][:15])}")
    
    print("\n🎄 SEASONAL THEMES:")
    print(f"  {', '.join(results['seasonal_themes'])}")
    
    print("\n👥 DEMOGRAPHICS:")
    print(f"  {', '.join(results['demographics'])}")
    
    print("\n🎯 TOP CATEGORIES WITH SCORES:")
    top_cats = extractor.get_top_categories(sample_text, "Tech Gifts", top_n=5)
    for category, score in top_cats:
        print(f"  📦 {category}: {score:.3f}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total keywords: {len(results['all_keywords'])}")
    print(f"  Tech-related: {extractor.is_tech_related(sample_text)}")
    print(f"  E-commerce: {extractor.is_ecommerce_related(sample_text)}")


def test_statistics():
    """Show statistics about available keywords"""
    print_section("KEYWORD DATABASE STATISTICS")
    
    extractor = KeywordExtractor()
    
    print("\n📚 TECH SKILLS DATABASE:")
    for category, skills in extractor.TECH_SKILLS.items():
        print(f"  {category}: {len(skills)} skills")
    
    total_tech = sum(len(v) for v in extractor.TECH_SKILLS.values())
    print(f"  TOTAL: {total_tech} tech skills")
    
    print("\n🛍️ PRODUCT CATEGORIES DATABASE:")
    for category, items in extractor.PRODUCT_CATEGORIES.items():
        print(f"  {category}: {len(items)} keywords")
    
    total_products = sum(len(v) for v in extractor.PRODUCT_CATEGORIES.values())
    print(f"  TOTAL: {total_products} product keywords")
    
    print("\n🎄 SEASONAL THEMES DATABASE:")
    for theme, keywords in extractor.SEASONAL_THEMES.items():
        print(f"  {theme}: {len(keywords)} keywords")
    
    total_seasonal = sum(len(v) for v in extractor.SEASONAL_THEMES.values())
    print(f"  TOTAL: {total_seasonal} seasonal keywords")
    
    print("\n👥 DEMOGRAPHICS DATABASE:")
    for demo_type, keywords in extractor.DEMOGRAPHICS.items():
        print(f"  {demo_type}: {len(keywords)} keywords")
    
    total_demo = sum(len(v) for v in extractor.DEMOGRAPHICS.values())
    print(f"  TOTAL: {total_demo} demographic keywords")
    
    print("\n🎯 GRAND TOTAL:")
    grand_total = total_tech + total_products + total_seasonal + total_demo
    print(f"  {grand_total} keywords across all categories!")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  KEYWORD EXTRACTOR - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    test_statistics()
    test_tech_page()
    test_ecommerce_page()
    test_seasonal_page()
    test_fashion_page()
    test_mixed_content()
    
    print("\n" + "="*70)
    print("  ✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\n💡 USAGE:")
    print("  This keyword extraction system can be used for:")
    print("    • Analyzing user browsing history")
    print("    • Categorizing crawled web pages")
    print("    • Product recommendation systems")
    print("    • Job skill matching")
    print("    • Seasonal content detection")
    print("    • E-commerce product classification")
    print("\n")


if __name__ == '__main__':
    main()
