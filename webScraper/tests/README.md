# Web Scraper Test Suite

Comprehensive test suite for the web scraper application including unit tests, integration tests, and performance tests.

## Setup

### Install Test Dependencies

```powershell
cd backend
pip install pytest pytest-cov pytest-mock
```

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/
│   ├── test_keyword_extractor.py  # KeywordExtractor unit tests
│   └── test_research_crawler.py   # ResearchCrawler unit tests
├── integration/
│   └── test_integration.py        # Integration tests
├── fixtures/                       # Test data (create as needed)
└── README.md                       # This file
```

## Running Tests

### Run All Tests

```powershell
pytest tests/ -v
```

### Run Unit Tests Only

```powershell
pytest tests/unit/ -v
```

### Run Integration Tests Only

```powershell
pytest tests/integration/ -v -m integration
```

### Run Specific Test File

```powershell
pytest tests/unit/test_keyword_extractor.py -v
```

### Run Specific Test Class

```powershell
pytest tests/unit/test_keyword_extractor.py::TestTechSkillsExtraction -v
```

### Run Specific Test Method

```powershell
pytest tests/unit/test_keyword_extractor.py::TestTechSkillsExtraction::test_extract_programming_languages -v
```

### Run with Coverage

```powershell
pytest tests/ --cov=backend/Crawler --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```powershell
pytest tests/ -vv --tb=long
```

### Run Failed Tests Only

```powershell
pytest tests/ --lf
```

## Test Categories

### Unit Tests (110+ tests)

- **test_keyword_extractor.py** (60+ tests)
  - Initialization tests
  - Tech skills extraction (languages, frameworks, databases, cloud)
  - Product categories extraction
  - Seasonal themes extraction
  - Demographics extraction
  - Combined extraction
  - Category scoring
  - Page type detection
  - Edge cases
  - Expected failure scenarios

- **test_research_crawler.py** (50+ tests)
  - Initialization tests
  - Content extraction
  - Subject extraction
  - Tag extraction
  - Link extraction
  - Relevance calculation
  - Metadata extraction
  - Summary generation
  - Integration workflows
  - Error handling

### Integration Tests (20+ tests)

- **test_integration.py**
  - API endpoint tests (requires running server)
  - Database persistence tests
  - End-to-end workflows
  - Performance tests
  - Error recovery tests
  - Data consistency tests

## Test Markers

Tests use markers for categorization:

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.skip` - Skipped tests (e.g., require running server)
- ✅ PASS - Tests expected to pass
- ❌ EXPECTED FAIL - Tests designed to fail (negative testing)

## Test Fixtures

Defined in `conftest.py`:

- `test_engine` - Test database engine
- `test_session` - Database session with automatic cleanup
- `mock_http_client` - Mocked HTTP client
- `sample_html` - Sample HTML content
- `sample_tech_text` - Sample tech-related text
- `sample_ecommerce_text` - Sample e-commerce text
- `sample_seasonal_text` - Sample seasonal text

## Expected Test Results

### Passing Tests (✅)

Most tests should pass. These validate correct functionality:

```
tests/unit/test_keyword_extractor.py .................... (60 passed)
tests/unit/test_research_crawler.py .................... (50 passed)
tests/integration/test_integration.py ............ (12 passed, 8 skipped)
```

### Expected Failures (❌)

Some tests are designed to fail to demonstrate error handling:

- `test_extract_from_empty_string` - Should fail gracefully
- `test_extract_from_gibberish` - Should return empty results
- `test_invalid_html` - Should handle malformed HTML
- `test_missing_required_fields` - Should raise validation errors

### Skipped Tests

Some tests require external dependencies and are skipped by default:

- API endpoint tests (require running Flask server)
- Browser history tests (require actual browser data)

To run skipped tests:

```powershell
# Start the Flask server first
cd backend
python api.py

# Then run all tests including skipped ones
pytest tests/ -v --runxfail
```

## Writing New Tests

### Test Template

```python
@pytest.mark.integration  # Optional marker
class TestMyFeature:
    """Test my new feature."""
    
    def test_basic_functionality(self, test_session):
        """✅ PASS: Should do basic thing."""
        # Arrange
        # ... setup code
        
        # Act
        result = some_function()
        
        # Assert
        assert result == expected
    
    def test_error_case(self):
        """❌ EXPECTED FAIL: Should handle errors."""
        with pytest.raises(ValueError):
            some_function(invalid_input)
```

### Best Practices

1. **Use descriptive test names** - Start with `test_` and describe what is being tested
2. **Mark expected results** - Use ✅ PASS or ❌ EXPECTED FAIL in docstrings
3. **Use fixtures** - Reuse setup code via fixtures in `conftest.py`
4. **Mock external dependencies** - Don't make real HTTP requests or database calls in unit tests
5. **Test edge cases** - Empty strings, None values, large inputs
6. **Test error handling** - Use `pytest.raises()` for expected exceptions

## Debugging Failed Tests

### View Full Output

```powershell
pytest tests/unit/test_keyword_extractor.py::test_failing_test -vv --tb=long
```

### Drop into Debugger on Failure

```powershell
pytest tests/ --pdb
```

### Print Debug Info

Add `print()` statements or use `pytest -s` to see stdout:

```powershell
pytest tests/unit/test_keyword_extractor.py -s
```

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install pytest pytest-cov
    pytest tests/ --cov=backend/Crawler --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v2
```

## Coverage Goals

- **Overall**: Aim for 80%+ coverage
- **Critical paths**: 95%+ coverage (keyword extraction, crawling)
- **Error handling**: 70%+ coverage

Check current coverage:

```powershell
pytest tests/ --cov=backend/Crawler --cov-report=term-missing
```

## Performance Benchmarks

Expected performance (from integration tests):

- Keyword extraction: < 0.5 seconds for 10,000 words
- Single page crawl: < 1 second
- 10 page crawl: < 5 seconds
- Database save: < 0.1 seconds per page

Run performance tests:

```powershell
pytest tests/integration/test_integration.py::TestPerformance -v
```

## Known Issues

1. **API endpoint tests skipped** - Require running Flask server
2. **Browser history tests** - Need actual browser history files
3. **Some integration tests** - May fail if database is not configured

## Support

For issues or questions:
1. Check test output for specific error messages
2. Review test code for expected behavior
3. Check `conftest.py` for available fixtures
4. Ensure all dependencies are installed (`pip install -r requirements.txt`)
