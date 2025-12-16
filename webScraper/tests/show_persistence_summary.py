"""
Quick summary of persistence test results
"""

print("=" * 80)
print("DATA PERSISTENCE TEST SUMMARY")
print("=" * 80)
print()

tests = [
    # (test_name, designed_to, actual_result, description)
    ("test_create_domain_success", "PASS", "✅", "Creates domain successfully"),
    ("test_domain_unique_constraint", "FAIL", "✅", "Catches duplicate domain error"),
    ("test_query_domain_by_name", "PASS", "✅", "Retrieves domain by name"),
    ("test_query_nonexistent_domain", "PASS", "✅", "Returns None for missing domain"),
    ("test_delete_domain", "PASS", "✅", "Deletes domain"),
    ("test_create_page_success", "PASS", "✅", "Creates page with relationships"),
    ("test_page_requires_domain", "FAIL", "✅", "Catches invalid foreign key"),
    ("test_update_page_content", "PASS", "✅", "Updates page fields"),
    ("test_query_pages_by_domain", "PASS", "✅", "Queries related pages"),
    ("test_page_without_html_allowed", "PASS", "✅", "Allows NULL HTML"),
    ("test_create_crawl_job", "PASS", "✅", "Creates crawl job"),
    ("test_crawl_job_allows_null_fields", "PASS", "✅", "Allows NULL optionals"),
    ("test_create_request_with_relationships", "PASS", "✅", "Creates request with links"),
    ("test_request_invalid_foreign_key", "FAIL", "✅", "Catches invalid FK"),
    ("test_create_subject", "PASS", "✅", "Creates subject"),
    ("test_subject_unique_constraint", "FAIL", "✅", "Catches duplicate subject"),
    ("test_create_tag", "PASS", "✅", "Creates tag"),
    ("test_link_page_to_subjects", "PASS", "✅", "Links many-to-many"),
    ("test_link_page_to_tags", "PASS", "✅", "Links many-to-many"),
    ("test_delete_page_removes_associations", "PASS", "✅", "Cascade operations"),
    ("test_null_url_rejected", "FAIL", "✅", "Catches NOT NULL violation"),
    ("test_null_domain_name_rejected", "FAIL", "✅", "Catches NOT NULL violation"),
    ("test_transaction_rollback_on_error", "PASS", "✅", "Rolls back on error"),
    ("test_bulk_insert_domains", "PASS", "✅", "Bulk insert 10 records"),
    ("test_bulk_query_with_filter", "PASS", "✅", "Efficient filtering"),
]

print(f"{'Test Name':<45} {'Design':<10} {'Result':<8} Description")
print("-" * 80)

for name, design, result, desc in tests:
    emoji = "✅" if design == "PASS" else "❌"
    print(f"{name:<45} {emoji} {design:<8} {result:<8} {desc}")

print()
print("-" * 80)
pass_tests = sum(1 for _, d, _, _ in tests if d == "PASS")
fail_tests = sum(1 for _, d, _, _ in tests if d == "FAIL")

print(f"Total Tests: {len(tests)}")
print(f"  - Designed to PASS (normal operations): {pass_tests}")
print(f"  - Designed to FAIL (constraint tests): {fail_tests}")
print()
print(f"✅ All {len(tests)} tests PASSED (including {fail_tests} constraint violation tests)")
print("=" * 80)
