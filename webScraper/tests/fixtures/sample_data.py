"""
Sample test data and fixtures for testing

This module contains additional test data that can be imported
by test files for more complex scenarios.
"""

# Sample HTML pages for different scenarios

TECH_BLOG_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Modern Web Development with React and Node.js</title>
    <meta name="description" content="Learn full-stack development">
</head>
<body>
    <article>
        <h1>Building Modern Web Apps</h1>
        <p>In this tutorial, we'll explore React, Node.js, and MongoDB.</p>
        <p>We'll also cover TypeScript, Docker, and AWS deployment.</p>
        <ul>
            <li>React for frontend</li>
            <li>Express.js for backend</li>
            <li>PostgreSQL for database</li>
        </ul>
    </article>
</body>
</html>
"""

ECOMMERCE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Shop Electronics - Laptops, Smartphones, Tablets</title>
    <meta name="keywords" content="electronics, laptop, smartphone, gadgets">
</head>
<body>
    <main>
        <h1>Electronics Store</h1>
        <div class="products">
            <div class="product">
                <h2>Gaming Laptop</h2>
                <p>High-performance laptop for gaming</p>
                <span class="price">$1299</span>
            </div>
            <div class="product">
                <h2>Smartphone Pro</h2>
                <p>Latest smartphone with 5G</p>
                <span class="price">$899</span>
            </div>
            <div class="product">
                <h2>Wireless Headphones</h2>
                <p>Premium noise-canceling headphones</p>
                <span class="price">$299</span>
            </div>
        </div>
    </main>
</body>
</html>
"""

SEASONAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Christmas Sale - Holiday Shopping Deals</title>
</head>
<body>
    <header>
        <h1>Holiday Season Sale</h1>
        <p>Special Christmas offers and Black Friday deals!</p>
    </header>
    <main>
        <section class="holiday">
            <h2>Christmas Gifts</h2>
            <p>Perfect presents for the holiday season</p>
        </section>
        <section class="sale">
            <h2>Black Friday Specials</h2>
            <p>Up to 70% off on Valentine's Day items</p>
        </section>
    </main>
</body>
</html>
"""

JOB_POSTING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Senior Python Developer - Remote Position</title>
</head>
<body>
    <article class="job-posting">
        <h1>Senior Python Developer</h1>
        <div class="requirements">
            <h2>Required Skills:</h2>
            <ul>
                <li>5+ years Python experience</li>
                <li>Django or Flask framework</li>
                <li>PostgreSQL and Redis</li>
                <li>AWS or Google Cloud</li>
                <li>Docker and Kubernetes</li>
                <li>React.js (bonus)</li>
            </ul>
        </div>
        <div class="description">
            <p>We're looking for an experienced backend developer to join our team.</p>
            <p>You'll work with cutting-edge technologies including Machine Learning and AI.</p>
        </div>
    </article>
</body>
</html>
"""

MIXED_CONTENT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Summer Tech Sale - Laptops and Gadgets</title>
</head>
<body>
    <main>
        <h1>Summer Electronics Sale</h1>
        <p>Shop the latest technology for students and professionals</p>
        
        <section class="products">
            <h2>Developer Laptops</h2>
            <p>Perfect for Python, Java, and JavaScript development</p>
            <p>Ideal for students and young professionals</p>
        </section>
        
        <section class="seasonal">
            <h2>Back to School Deals</h2>
            <p>Special offers for the summer season</p>
        </section>
    </main>
</body>
</html>
"""

# Sample text content

TECH_TEXT = """
We are looking for a Full Stack Developer with expertise in:
- Frontend: React, Vue.js, Angular
- Backend: Node.js, Python, Ruby
- Databases: MongoDB, MySQL, PostgreSQL
- DevOps: Docker, Kubernetes, AWS, Jenkins
- Languages: JavaScript, TypeScript, Go, Rust
"""

ECOMMERCE_TEXT = """
Shop our latest collection of electronics, clothing, and home goods.
Featured products include laptops, smartphones, cameras, furniture, and jewelry.
Browse categories: electronics, fashion, books, toys, sports equipment, and more.
Free shipping on all gadgets and accessories over $50.
"""

SEASONAL_TEXT = """
Celebrate the holidays with our special Christmas sale!
Black Friday and Cyber Monday deals are here.
Valentine's Day gifts, Mother's Day specials, and Father's Day presents.
Get ready for Halloween costumes and Thanksgiving decorations.
Summer sale ends soon! Back to school shopping starts now.
"""

DEMOGRAPHICS_TEXT = """
Products for everyone: men's fashion, women's accessories, kids' toys.
Targeting young adults, professionals, students, and seniors.
Perfect for teenagers looking for the latest trends.
Great gifts for children and toddlers.
"""

# Sample API responses

KEYWORD_EXTRACT_RESPONSE = {
    'tech_skills': ['python', 'javascript', 'react'],
    'product_categories': ['laptop', 'smartphone'],
    'seasonal_themes': ['christmas', 'black friday'],
    'demographics': ['students'],
    'all_keywords': ['python', 'javascript', 'react', 'laptop', 'smartphone', 'christmas', 'black friday', 'students']
}

PAGE_ANALYSIS_RESPONSE = {
    'url': 'https://example.com/test',
    'title': 'Test Page',
    'tech_skills': ['python', 'django'],
    'product_categories': [],
    'seasonal_themes': [],
    'is_tech_related': True,
    'is_ecommerce_related': False,
    'is_seasonal': False,
    'relevance_score': 0.85
}

CATEGORIES_RESPONSE = {
    'tech_skills': ['python', 'javascript', 'react', 'node.js'],
    'product_categories': ['laptop', 'smartphone', 'tablet'],
    'seasonal_themes': ['christmas', 'black friday'],
    'demographics': ['students', 'professionals'],
    'total_tech_skills': 200,
    'total_product_categories': 150,
    'total_seasonal_themes': 50,
    'total_demographics': 25
}

# Sample database records

SAMPLE_DOMAIN = {
    'id': 1,
    'name': 'example.com'
}

SAMPLE_PAGE = {
    'id': 1,
    'url': 'https://example.com/page1',
    'domain_id': 1,
    'title': 'Test Page',
    'content': 'Sample content for testing',
    'summary': 'Test page summary',
    'status_code': 200
}

SAMPLE_TAGS = [
    {'id': 1, 'name': 'tech:python'},
    {'id': 2, 'name': 'tech:javascript'},
    {'id': 3, 'name': 'product:laptop'},
    {'id': 4, 'name': 'seasonal:christmas'}
]

SAMPLE_SUBJECTS = [
    {'id': 1, 'name': 'Web Development'},
    {'id': 2, 'name': 'Machine Learning'},
    {'id': 3, 'name': 'E-commerce'}
]
