#!/usr/bin/env python3
import time
import rusty_tags as rust
from jinja2 import Template

print('🔥 EXTREME STRESS TEST: Large E-commerce Product Catalog')
print('=' * 60)

# Generate test data - 200 products with 5 reviews each
products = []
for i in range(200):
    reviews = []
    for j in range(5):
        reviews.append({
            'author': f'User{j+1}',
            'rating': (j % 5) + 1,
            'comment': f'Review {j+1} for product {i+1}. This is a detailed review.'
        })
    
    products.append({
        'id': i + 1,
        'name': f'Product {i + 1}',
        'price': 29.99 + (i * 2.5),
        'category': ['Electronics', 'Clothing', 'Books', 'Home'][i % 4],
        'description': f'Detailed description for product {i + 1}.',
        'in_stock': i % 7 != 0,
        'rating': ((i % 5) + 1),
        'reviews': reviews,
        'specs': {
            'weight': f'{0.5 + (i * 0.1):.1f}kg',
            'dimensions': f'{10 + i}x{8 + i}x{5 + i}cm',
            'warranty': f'{(i % 3) + 1} year(s)'
        }
    })

catalog_data = {
    'title': 'Mega Product Catalog',
    'store_name': 'SuperStore',
    'products': products,
    'total_products': len(products)
}

# Jinja2 template
jinja_template = Template("""<!doctype html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ store_name }} - {{ title }}</h1>
    <p>Showing {{ total_products }} products</p>
    <div class="product-grid">
        {% for product in products %}
        <div class="product {{ product.category.lower() }}">
            <h3>{{ product.name }} (#{{ product.id }})</h3>
            <p class="price">${{ "%.2f"|format(product.price) }}</p>
            <p class="category">Category: {{ product.category }}</p>
            <p class="description">{{ product.description }}</p>
            <div class="stock-info">
                <span class="{{ 'in-stock' if product.in_stock else 'out-of-stock' }}">
                    {{ 'In Stock' if product.in_stock else 'Out of Stock' }}
                </span>
                <span class="rating">Rating: {{ product.rating }}/5</span>
            </div>
            <div class="specifications">
                <h4>Specifications:</h4>
                <ul>
                    <li>Weight: {{ product.specs.weight }}</li>
                    <li>Dimensions: {{ product.specs.dimensions }}</li>
                    <li>Warranty: {{ product.specs.warranty }}</li>
                </ul>
            </div>
            <div class="reviews">
                <h4>Customer Reviews:</h4>
                {% for review in product.reviews %}
                <div class="review">
                    <strong>{{ review.author }}</strong> ({{ review.rating }}/5):
                    <p>{{ review.comment }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>""")

def create_catalog_rust():
    product_divs = []
    for product in products:
        # Create review divs
        review_divs = []
        for review in product['reviews']:
            review_divs.append(rust.Div(
                rust.Strong(review['author']), f' ({review["rating"]}/5):',
                rust.P(review['comment']),
                cls='review'
            ))
        
        # Create product div
        product_divs.append(rust.Div(
            rust.H3(f'{product["name"]} (#{product["id"]})'),
            rust.P(f'${product["price"]:.2f}', cls='price'),
            rust.P(f'Category: {product["category"]}', cls='category'),
            rust.P(product['description'], cls='description'),
            rust.Div(
                rust.Span('In Stock' if product['in_stock'] else 'Out of Stock',
                          cls='in-stock' if product['in_stock'] else 'out-of-stock'),
                rust.Span(f'Rating: {product["rating"]}/5', cls='rating'),
                cls='stock-info'
            ),
            rust.Div(
                rust.H4('Specifications:'),
                rust.Ul(
                    rust.Li(f'Weight: {product["specs"]["weight"]}'),
                    rust.Li(f'Dimensions: {product["specs"]["dimensions"]}'),
                    rust.Li(f'Warranty: {product["specs"]["warranty"]}')
                ),
                cls='specifications'
            ),
            rust.Div(
                rust.H4('Customer Reviews:'),
                *review_divs,
                cls='reviews'
            ),
            cls=f'product {product["category"].lower()}'
        ))
    
    return rust.Html(
        rust.Title(catalog_data['title']),
        rust.H1(f'{catalog_data["store_name"]} - {catalog_data["title"]}'),
        rust.P(f'Showing {catalog_data["total_products"]} products'),
        rust.Div(*product_divs, cls='product-grid')
    )

print(f'Generating catalog with {len(products)} products, each with 5 reviews...')
print(f'Total elements: ~{len(products) * 25} HTML elements')

# Benchmark
iterations = 50
print(f'\\nTesting {iterations} iterations...')

print("Benchmarking Jinja2...")
start = time.perf_counter()
for _ in range(iterations):
    result = jinja_template.render(**catalog_data)
jinja_time = (time.perf_counter() - start) / iterations
jinja_size = len(result)

print("Benchmarking Rust...")
start = time.perf_counter()
for _ in range(iterations):
    result = str(create_catalog_rust())
rust_time = (time.perf_counter() - start) / iterations
rust_size = len(result)

print(f'\\n📊 EXTREME STRESS TEST RESULTS:')
print(f'=' * 40)
print(f'Jinja2: {jinja_time*1000:7.1f}ms ({1/jinja_time:5.0f} catalogs/sec) - {jinja_size:,} chars')
print(f'Rust:   {rust_time*1000:7.1f}ms ({1/rust_time:5.0f} catalogs/sec) - {rust_size:,} chars')

print(f'\\n🚀 Rust vs Jinja2: {jinja_time/rust_time:.1f}x faster')
print(f'💡 Generated {rust_size:,} character HTML documents with {len(products) * 25:,}+ elements!') 