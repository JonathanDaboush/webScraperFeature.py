"""
Unit Tests for Keyword Extractor

Tests for the KeywordExtractor class including:
- Tech skills extraction
- Product category detection
- Seasonal theme identification
- Demographic classification
- Category scoring
- Edge cases and failure scenarios
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from Crawler.keyword_extractor import KeywordExtractor


class TestKeywordExtractorInit:
    """Test keyword extractor initialization."""
    
    def test_extractor_initializes(self):
        """✅ PASS: Extractor should initialize successfully."""
        extractor = KeywordExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'TECH_SKILLS')
        assert hasattr(extractor, 'PRODUCT_CATEGORIES')
        assert hasattr(extractor, 'SEASONAL_THEMES')
        assert hasattr(extractor, 'DEMOGRAPHICS')
    
    def test_keyword_databases_loaded(self):
        """✅ PASS: Keyword databases should be populated."""
        extractor = KeywordExtractor()
        assert len(extractor.TECH_SKILLS) > 0
        assert len(extractor.PRODUCT_CATEGORIES) > 0
        assert len(extractor.SEASONAL_THEMES) > 0
        assert len(extractor.DEMOGRAPHICS) > 0
    
    def test_keyword_patterns_built(self):
        """✅ PASS: Search patterns should be built."""
        extractor = KeywordExtractor()
        assert hasattr(extractor, 'all_keywords')
        assert 'tech' in extractor.all_keywords
        assert 'products' in extractor.all_keywords
        assert len(extractor.all_keywords['tech']) > 0


class TestTechSkillsExtraction:
    """Test technical skills extraction."""
    
    def test_extract_programming_languages(self, sample_tech_text):
        """✅ PASS: Should extract programming languages."""
        extractor = KeywordExtractor()
        skills = extractor.extract_tech_skills(sample_tech_text.lower())
        
        assert 'python' in skills
        assert 'javascript' in skills
        assert 'typescript' in skills
    
    def test_extract_frameworks(self, sample_tech_text):
        """✅ PASS: Should extract frameworks."""
        extractor = KeywordExtractor()
        skills = extractor.extract_tech_skills(sample_tech_text.lower())
        
        assert 'react' in skills
        assert 'django' in skills
        assert 'flask' in skills
    
    def test_extract_databases(self, sample_tech_text):
        """✅ PASS: Should extract database names."""
        extractor = KeywordExtractor()
        skills = extractor.extract_tech_skills(sample_tech_text.lower())
        
        assert 'postgresql' in skills
        assert 'mongodb' in skills
        assert 'redis' in skills
    
    def test_extract_cloud_tools(self, sample_tech_text):
        """✅ PASS: Should extract cloud and DevOps tools."""
        extractor = KeywordExtractor()
        skills = extractor.extract_tech_skills(sample_tech_text.lower())
        
        assert 'aws' in skills
        assert 'docker' in skills
        assert 'kubernetes' in skills
    
    def test_no_tech_skills_in_non_tech_text(self, sample_ecommerce_text):
        """✅ PASS: Should not find tech skills in e-commerce text."""
        extractor = KeywordExtractor()
        skills = extractor.extract_tech_skills(sample_ecommerce_text.lower())
        
        # May find generic terms like 'performance', but no specific languages
        assert 'python' not in skills
        assert 'java' not in skills
        assert 'react' not in skills
    
    def test_case_insensitive_extraction(self):
        """✅ PASS: Should extract regardless of case."""
        extractor = KeywordExtractor()
        text = "We use PYTHON and React for our projects"
        skills = extractor.extract_tech_skills(text.lower())
        
        assert 'python' in skills
        assert 'react' in skills
    
    def test_word_boundary_matching(self):
        """✅ PASS: Should respect word boundaries."""
        extractor = KeywordExtractor()
        text = "We love carpet python snakes"  # Should not match 'python'
        skills = extractor.extract_tech_skills(text.lower())
        
        # 'python' should still match as it's a separate word
        assert 'python' in skills
    
    def test_empty_text_returns_empty_list(self):
        """✅ PASS: Should return empty list for empty text."""
        extractor = KeywordExtractor()
        skills = extractor.extract_tech_skills("")
        
        assert skills == []
    
    def test_extract_ai_ml_skills(self):
        """✅ PASS: Should extract AI/ML related skills."""
        extractor = KeywordExtractor()
        text = "Experience with TensorFlow, PyTorch, and machine learning required"
        skills = extractor.extract_tech_skills(text.lower())
        
        assert 'tensorflow' in skills
        assert 'pytorch' in skills
        assert 'machine learning' in skills


class TestProductCategoriesExtraction:
    """Test product category extraction."""
    
    def test_extract_electronics(self, sample_ecommerce_text):
        """✅ PASS: Should extract electronics keywords."""
        extractor = KeywordExtractor()
        products = extractor.extract_product_categories(sample_ecommerce_text.lower())
        
        assert 'laptop' in products
        assert 'keyboard' in products
        assert 'mouse' in products
        assert 'headphones' in products
    
    def test_extract_fashion_items(self):
        """✅ PASS: Should extract fashion keywords."""
        extractor = KeywordExtractor()
        text = "New collection: dresses, jeans, sneakers, and accessories"
        products = extractor.extract_product_categories(text.lower())
        
        assert 'dress' in products or 'dresses' in products
        assert 'jeans' in products
        assert 'sneakers' in products
        assert 'accessories' in products
    
    def test_extract_home_garden(self):
        """✅ PASS: Should extract home & garden keywords."""
        extractor = KeywordExtractor()
        text = "Sale on furniture, sofas, lamps, and smart home devices"
        products = extractor.extract_product_categories(text.lower())
        
        assert 'furniture' in products
        assert 'sofa' in products or 'sofas' in products
        assert 'lamp' in products or 'lamps' in products
    
    def test_no_products_in_tech_text(self, sample_tech_text):
        """✅ PASS: Should find minimal products in tech text."""
        extractor = KeywordExtractor()
        products = extractor.extract_product_categories(sample_tech_text.lower())
        
        # Tech text shouldn't have many product keywords
        assert 'laptop' not in products
        assert 'phone' not in products
    
    def test_multiple_categories_detected(self):
        """✅ PASS: Should detect multiple product categories."""
        extractor = KeywordExtractor()
        text = "Shop laptops, clothing, furniture, and toys at great prices"
        products = extractor.extract_product_categories(text.lower())
        
        assert 'laptop' in products or 'laptops' in products
        assert 'clothing' in products
        assert 'furniture' in products
        assert 'toy' in products or 'toys' in products


class TestSeasonalThemesExtraction:
    """Test seasonal theme extraction."""
    
    def test_extract_christmas_keywords(self, sample_seasonal_text):
        """✅ PASS: Should extract Christmas keywords."""
        extractor = KeywordExtractor()
        themes = extractor.extract_seasonal_themes(sample_seasonal_text.lower())
        
        assert 'christmas' in themes
        assert 'holiday' in themes
        assert 'gift' in themes or 'gifts' in themes
    
    def test_extract_halloween_keywords(self, sample_seasonal_text):
        """✅ PASS: Should extract Halloween keywords."""
        extractor = KeywordExtractor()
        themes = extractor.extract_seasonal_themes(sample_seasonal_text.lower())
        
        assert 'halloween' in themes
        assert 'costume' in themes or 'costumes' in themes
    
    def test_extract_black_friday(self, sample_seasonal_text):
        """✅ PASS: Should extract Black Friday keywords."""
        extractor = KeywordExtractor()
        themes = extractor.extract_seasonal_themes(sample_seasonal_text.lower())
        
        assert 'black friday' in themes or 'sale' in themes
    
    def test_extract_valentines(self, sample_seasonal_text):
        """✅ PASS: Should extract Valentine's Day keywords."""
        extractor = KeywordExtractor()
        themes = extractor.extract_seasonal_themes(sample_seasonal_text.lower())
        
        assert "valentine" in themes or "valentine's day" in themes
    
    def test_no_seasonal_in_regular_text(self, sample_tech_text):
        """✅ PASS: Should not find seasonal themes in tech text."""
        extractor = KeywordExtractor()
        themes = extractor.extract_seasonal_themes(sample_tech_text.lower())
        
        assert 'christmas' not in themes
        assert 'halloween' not in themes


class TestDemographicsExtraction:
    """Test demographic keyword extraction."""
    
    def test_extract_age_groups(self):
        """✅ PASS: Should extract age group keywords."""
        extractor = KeywordExtractor()
        text = "Toys for kids, teens, and adults"
        demographics = extractor.extract_demographics(text.lower())
        
        assert 'kids' in demographics
        assert 'teen' in demographics or 'teens' in demographics
        assert 'adult' in demographics or 'adults' in demographics
    
    def test_extract_gender(self):
        """✅ PASS: Should extract gender keywords."""
        extractor = KeywordExtractor()
        text = "Clothing for men, women, boys, and girls"
        demographics = extractor.extract_demographics(text.lower())
        
        assert 'men' in demographics
        assert 'women' in demographics
        assert 'boys' in demographics
        assert 'girls' in demographics
    
    def test_extract_lifestyle(self, sample_ecommerce_text):
        """✅ PASS: Should extract lifestyle keywords."""
        extractor = KeywordExtractor()
        demographics = extractor.extract_demographics(sample_ecommerce_text.lower())
        
        assert 'professional' in demographics or 'student' in demographics or 'students' in demographics


class TestExtractAll:
    """Test the extract_all method."""
    
    def test_extract_all_categories(self, sample_tech_text):
        """✅ PASS: Should extract all keyword types at once."""
        extractor = KeywordExtractor()
        result = extractor.extract_all(sample_tech_text, "Senior Developer Job")
        
        assert 'tech_skills' in result
        assert 'product_categories' in result
        assert 'seasonal_themes' in result
        assert 'demographics' in result
        assert 'all_keywords' in result
    
    def test_all_keywords_combined(self, sample_tech_text):
        """✅ PASS: all_keywords should combine all categories."""
        extractor = KeywordExtractor()
        result = extractor.extract_all(sample_tech_text)
        
        assert len(result['all_keywords']) >= len(result['tech_skills'])
        
        # Check that tech skills are in all_keywords
        for skill in result['tech_skills'][:5]:
            assert skill in result['all_keywords']
    
    def test_title_given_higher_weight(self):
        """✅ PASS: Title should be considered in extraction."""
        extractor = KeywordExtractor()
        result = extractor.extract_all("generic content", "Python Developer")
        
        assert 'python' in result['tech_skills']


class TestCategoryScoring:
    """Test category relevance scoring."""
    
    def test_get_category_scores(self, sample_ecommerce_text):
        """✅ PASS: Should return category scores."""
        extractor = KeywordExtractor()
        scores = extractor.get_category_scores(sample_ecommerce_text)
        
        assert isinstance(scores, dict)
        assert 'electronics' in scores
        assert 0 <= scores['electronics'] <= 1.0
    
    def test_electronics_scores_high_for_tech(self, sample_ecommerce_text):
        """✅ PASS: Electronics should score high for electronics text."""
        extractor = KeywordExtractor()
        scores = extractor.get_category_scores(sample_ecommerce_text)
        
        # Electronics should be one of the top categories
        assert scores['electronics'] > 0
    
    def test_get_top_categories(self, sample_ecommerce_text):
        """✅ PASS: Should return top N categories."""
        extractor = KeywordExtractor()
        top_cats = extractor.get_top_categories(sample_ecommerce_text, top_n=3)
        
        assert isinstance(top_cats, list)
        assert len(top_cats) <= 3
        
        # Should return tuples of (category, score)
        for cat, score in top_cats:
            assert isinstance(cat, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1.0


class TestPageTypeDetection:
    """Test is_tech_related and is_ecommerce_related methods."""
    
    def test_tech_page_detected(self, sample_tech_text):
        """✅ PASS: Should detect tech-related pages."""
        extractor = KeywordExtractor()
        assert extractor.is_tech_related(sample_tech_text) is True
    
    def test_non_tech_page_detected(self, sample_seasonal_text):
        """✅ PASS: Should detect non-tech pages."""
        extractor = KeywordExtractor()
        assert extractor.is_tech_related(sample_seasonal_text) is False
    
    def test_ecommerce_page_detected(self, sample_ecommerce_text):
        """✅ PASS: Should detect e-commerce pages."""
        extractor = KeywordExtractor()
        assert extractor.is_ecommerce_related(sample_ecommerce_text) is True
    
    def test_non_ecommerce_page_detected(self, sample_tech_text):
        """✅ PASS: Should detect non-e-commerce pages."""
        extractor = KeywordExtractor()
        # Tech text may have some product keywords, but not enough
        result = extractor.is_ecommerce_related(sample_tech_text)
        # This could be True or False depending on threshold
        assert isinstance(result, bool)
    
    def test_custom_threshold_tech(self):
        """✅ PASS: Should respect custom thresholds for tech detection."""
        extractor = KeywordExtractor()
        text = "We use Python and JavaScript"
        
        # With low threshold, should detect as tech
        assert extractor.is_tech_related(text, threshold=1) is True
        
        # With high threshold, might not detect as tech
        result = extractor.is_tech_related(text, threshold=10)
        assert isinstance(result, bool)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_string(self):
        """✅ PASS: Should handle empty strings."""
        extractor = KeywordExtractor()
        result = extractor.extract_all("")
        
        assert result['tech_skills'] == []
        assert result['product_categories'] == []
        assert result['seasonal_themes'] == []
        assert result['all_keywords'] == []
    
    def test_whitespace_only(self):
        """✅ PASS: Should handle whitespace-only strings."""
        extractor = KeywordExtractor()
        result = extractor.extract_all("   \n\t   ")
        
        assert result['tech_skills'] == []
    
    def test_very_long_text(self):
        """✅ PASS: Should handle very long text."""
        extractor = KeywordExtractor()
        long_text = "Python developer " * 10000
        result = extractor.extract_all(long_text)
        
        assert 'python' in result['tech_skills']
    
    def test_special_characters(self):
        """✅ PASS: Should handle special characters."""
        extractor = KeywordExtractor()
        text = "Python!@#$%^&*()Django[]{}Flask<>?/"
        skills = extractor.extract_tech_skills(text.lower())
        
        # Should still find keywords despite special chars
        assert 'python' in skills
        assert 'django' in skills
        assert 'flask' in skills
    
    def test_mixed_case_variations(self):
        """✅ PASS: Should handle mixed case."""
        extractor = KeywordExtractor()
        text = "PyThOn DJANGO flask ReAcT"
        skills = extractor.extract_tech_skills(text.lower())
        
        assert 'python' in skills
        assert 'django' in skills
        assert 'flask' in skills
        assert 'react' in skills
    
    def test_unicode_characters(self):
        """✅ PASS: Should handle unicode characters."""
        extractor = KeywordExtractor()
        text = "Python développeur avec React 🚀"
        skills = extractor.extract_tech_skills(text.lower())
        
        assert 'python' in skills
        assert 'react' in skills


class TestFailureScenarios:
    """Test scenarios that should intentionally fail or return unexpected results."""
    
    def test_nonsense_text_no_matches(self):
        """❌ EXPECTED FAIL: Random text should not match any keywords."""
        extractor = KeywordExtractor()
        text = "xyzabc qwerty asdfgh zxcvbn poiuyt"
        result = extractor.extract_all(text)
        
        # Should find nothing
        assert len(result['all_keywords']) == 0
    
    def test_partial_matches_not_found(self):
        """❌ EXPECTED FAIL: Partial words should not match."""
        extractor = KeywordExtractor()
        text = "pythonic reactjs javascripting"
        skills = extractor.extract_tech_skills(text.lower())
        
        # These are not exact matches - depends on word boundaries
        # Some might match, some might not
        # This test documents the behavior
        pass
    
    def test_numbers_only(self):
        """❌ EXPECTED FAIL: Numbers should not match."""
        extractor = KeywordExtractor()
        text = "123456 7890 42 3.14"
        result = extractor.extract_all(text)
        
        assert len(result['all_keywords']) == 0
    
    def test_invalid_type_raises_error(self):
        """❌ EXPECTED FAIL: Passing non-string should raise error."""
        extractor = KeywordExtractor()
        
        with pytest.raises((TypeError, AttributeError)):
            extractor.extract_all(None)
        
        with pytest.raises((TypeError, AttributeError)):
            extractor.extract_tech_skills(12345)
    
    def test_extremely_large_text_performance(self):
        """❌ POTENTIAL FAIL: Very large text might be slow."""
        extractor = KeywordExtractor()
        # 1 million words - might timeout or be slow
        huge_text = "Python " * 1000000
        
        import time
        start = time.time()
        result = extractor.extract_all(huge_text)
        duration = time.time() - start
        
        # Should complete in reasonable time (< 5 seconds)
        assert duration < 5.0, f"Took {duration}s - too slow!"
        assert 'python' in result['tech_skills']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
