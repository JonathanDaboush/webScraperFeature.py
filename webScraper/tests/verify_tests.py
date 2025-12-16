"""
Test Verification Script

This script validates that all test files are properly configured
and can be imported without errors.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

def check_imports():
    """Verify all test files can be imported."""
    print("Checking test file imports...")
    
    errors = []
    
    # Check conftest.py
    try:
        print("  ✓ conftest.py")
        import conftest
    except Exception as e:
        errors.append(f"  ✗ conftest.py: {e}")
    
    # Check unit tests
    try:
        from unit import test_keyword_extractor
        print("  ✓ unit/test_keyword_extractor.py")
    except Exception as e:
        errors.append(f"  ✗ unit/test_keyword_extractor.py: {e}")
    
    try:
        from unit import test_research_crawler
        print("  ✓ unit/test_research_crawler.py")
    except Exception as e:
        errors.append(f"  ✗ unit/test_research_crawler.py: {e}")
    
    # Check integration tests
    try:
        from integration import test_integration
        print("  ✓ integration/test_integration.py")
    except Exception as e:
        errors.append(f"  ✗ integration/test_integration.py: {e}")
    
    # Check fixtures
    try:
        from fixtures import sample_data
        print("  ✓ fixtures/sample_data.py")
    except Exception as e:
        errors.append(f"  ✗ fixtures/sample_data.py: {e}")
    
    return errors


def check_backend_modules():
    """Verify backend modules can be imported."""
    print("\nChecking backend module imports...")
    
    errors = []
    
    modules = [
        ('Crawler.keyword_extractor', 'KeywordExtractor'),
        ('Crawler.research_crawler', 'ResearchCrawler'),
        ('Persistance.repository', 'Repository'),
        ('Persistance.crawler', 'Page'),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            errors.append(f"  ✗ {module_name}.{class_name}: {e}")
    
    return errors


def count_tests():
    """Count total number of tests."""
    print("\nCounting tests...")
    
    test_dir = Path(__file__).parent
    
    test_counts = {}
    
    for test_file in test_dir.rglob('test_*.py'):
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            count = content.count('def test_')
            test_counts[test_file.name] = count
            print(f"  {test_file.name}: {count} tests")
    
    total = sum(test_counts.values())
    print(f"\n  Total: {total} tests")
    
    return total


def verify_test_structure():
    """Verify test directory structure."""
    print("\nVerifying test structure...")
    
    test_dir = Path(__file__).parent
    
    required_files = [
        'conftest.py',
        'README.md',
        'requirements.txt',
        'run_tests.py',
        'verify_tests.py',
        'unit/test_keyword_extractor.py',
        'unit/test_research_crawler.py',
        'integration/test_integration.py',
        'fixtures/sample_data.py'
    ]
    
    missing = []
    
    for file_path in required_files:
        full_path = test_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            missing.append(file_path)
            print(f"  ✗ {file_path} - MISSING")
    
    return missing


def main():
    """Run all verification checks."""
    print("="*70)
    print("TEST VERIFICATION")
    print("="*70)
    
    all_errors = []
    
    # Check structure
    missing_files = verify_test_structure()
    if missing_files:
        all_errors.extend([f"Missing file: {f}" for f in missing_files])
    
    # Check imports
    import_errors = check_imports()
    if import_errors:
        all_errors.extend(import_errors)
    
    # Check backend
    backend_errors = check_backend_modules()
    if backend_errors:
        all_errors.extend(backend_errors)
    
    # Count tests
    total_tests = count_tests()
    
    # Final summary
    print("\n" + "="*70)
    if all_errors:
        print("❌ VERIFICATION FAILED")
        print("\nErrors:")
        for error in all_errors:
            print(f"  {error}")
    else:
        print("✅ VERIFICATION PASSED")
        print(f"\n  {total_tests} tests ready to run")
        print("\nTo run tests:")
        print("  python run_tests.py")
        print("  python run_tests.py --unit")
        print("  python run_tests.py --integration")
        print("  python run_tests.py --coverage")
    print("="*70)
    
    return 0 if not all_errors else 1


if __name__ == '__main__':
    sys.exit(main())
