#!/usr/bin/env python3
"""
Realistic Template Engine Benchmark: RustyTags vs Air vs Jinja2 vs Mako

This benchmark measures template engines as they're typically used in real applications:
1. Templates stored in separate files
2. Loading templates from disk
3. Rendering with dynamic data
4. Measuring time to process X requests (realistic metrics)
"""

import sys
import os
import time
import statistics
from pathlib import Path
from typing import Callable, List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rusty_tags as rt
from air.tags import *
from air.tags import Html as AirHtml
import jinja2
from mako.template import Template as MakoTemplate
from mako.lookup import TemplateLookup

class RealisticTemplateBenchmark:
    """Realistic template engine benchmark with file-based templates."""
    
    def __init__(self, request_counts=[100, 500, 1000, 5000]):
        self.request_counts = request_counts
        self.template_dir = Path("benchmarks/templates")
        self.template_dir.mkdir(exist_ok=True)
        
        # Setup template engines
        self._setup_template_files()
        self._setup_template_engines()
    
    def _setup_template_files(self):
        """Create template files for each engine."""
        print("📁 Creating template files...")
        
        # Simple template
        simple_jinja = '<div class="{{ cls }}">{{ content }}</div>'
        (self.template_dir / "simple.jinja2").write_text(simple_jinja)
        
        simple_mako = '<div class="${cls}">${content}</div>'
        (self.template_dir / "simple.mako").write_text(simple_mako)
        
        # Complex page template
        complex_jinja = '''<!doctype html>
<html lang="{{ lang }}">
<head><title>{{ title }}</title></head>
<body>
<div class="page-container">
    <header class="site-header">
        <h1>{{ heading }}</h1>
        <nav class="main-nav">
            <ul>
            {% for link in nav_links %}
                <li><a href="{{ link.url }}">{{ link.text }}</a></li>
            {% endfor %}
            </ul>
        </nav>
    </header>
    <main class="main-content">
        <section class="content">
            <h2>{{ section_title }}</h2>
            <p>{{ description }}</p>
            <ul class="features">
            {% for feature in features %}
                <li>{{ feature }}</li>
            {% endfor %}
            </ul>
        </section>
    </main>
    <footer class="site-footer">
        <p>{{ footer_text }}</p>
    </footer>
</div>
</body>
</html>'''
        (self.template_dir / "complex.jinja2").write_text(complex_jinja)
        
        complex_mako = '''<!doctype html>
<html lang="${lang}">
<head><title>${title}</title></head>
<body>
<div class="page-container">
    <header class="site-header">
        <h1>${heading}</h1>
        <nav class="main-nav">
            <ul>
            % for link in nav_links:
                <li><a href="${link['url']}">${link['text']}</a></li>
            % endfor
            </ul>
        </nav>
    </header>
    <main class="main-content">
        <section class="content">
            <h2>${section_title}</h2>
            <p>${description}</p>
            <ul class="features">
            % for feature in features:
                <li>${feature}</li>
            % endfor
            </ul>
        </section>
    </main>
    <footer class="site-footer">
        <p>${footer_text}</p>
    </footer>
</div>
</body>
</html>'''
        (self.template_dir / "complex.mako").write_text(complex_mako)
        
        # Product list template
        list_jinja = '''<div class="product-list">
    <h2>{{ title }}</h2>
    <div class="products">
    {% for product in products %}
        <div class="product-card" data-id="{{ product.id }}">
            <h3>{{ product.name }}</h3>
            <p class="price">${{ product.price }}</p>
            <p class="description">{{ product.description }}</p>
            <div class="tags">
            {% for tag in product.tags %}
                <span class="tag">{{ tag }}</span>
            {% endfor %}
            </div>
        </div>
    {% endfor %}
    </div>
</div>'''
        (self.template_dir / "products.jinja2").write_text(list_jinja)
        
        list_mako = '''<div class="product-list">
    <h2>${title}</h2>
    <div class="products">
    % for product in products:
        <div class="product-card" data-id="${product['id']}">
            <h3>${product['name']}</h3>
            <p class="price">$${product['price']}</p>
            <p class="description">${product['description']}</p>
            <div class="tags">
            % for tag in product['tags']:
                <span class="tag">${tag}</span>
            % endfor
            </div>
        </div>
    % endfor
    </div>
</div>'''
        (self.template_dir / "products.mako").write_text(list_mako)
        
        print("✅ Template files created successfully!")
    
    def _setup_template_engines(self):
        """Setup template engine environments."""
        print("🔧 Setting up template engines...")
        
        # Jinja2 with file loader
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir))
        )
        
        # Mako with template lookup
        self.mako_lookup = TemplateLookup(
            directories=[str(self.template_dir)]
        )
        
        print("✅ Template engines configured!")
    
    def benchmark_requests(self, name: str, func: Callable, request_count: int, data: Any) -> Dict[str, float]:
        """Benchmark processing N requests and return timing metrics."""
        print(f"  Processing {request_count:,} requests...")
        
        # Warmup run
        for _ in range(min(10, request_count // 10)):
            func(data)
        
        # Timed run
        start_time = time.perf_counter()
        
        for i in range(request_count):
            result = func(data)
            # Simulate some processing of the result
            len(result)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'avg_time_per_request': total_time / request_count,
            'requests_per_second': request_count / total_time if total_time > 0 else 0
        }
    
    def run_realistic_benchmark_suite(self):
        """Run realistic template benchmarks with file loading."""
        print("\\n🌐 REALISTIC TEMPLATE ENGINE BENCHMARK")
        print("=" * 60)
        print("📁 Templates loaded from separate files (as in real apps)")
        print("⏱️  Measuring time to process N requests")
        
        # Test data for different scenarios
        test_scenarios = self._get_test_scenarios()
        
        # Define benchmark suites with realistic template loading
        benchmark_suites = [
            ("Simple Page Template", self._simple_template_benchmarks, test_scenarios['simple']),
            ("Complex Page Template", self._complex_template_benchmarks, test_scenarios['complex']),
            ("Product List Template", self._product_list_benchmarks, test_scenarios['products']),
        ]
        
        all_results = {}
        
        for suite_name, benchmark_funcs, data in benchmark_suites:
            print(f"\\n🎯 {suite_name} Benchmark")
            print("=" * 60)
            
            suite_results = {}
            benchmark_funcs_dict = benchmark_funcs()
            
            for engine_name, func in benchmark_funcs_dict.items():
                print(f"\\n📊 Testing {engine_name}")
                engine_results = {}
                
                for request_count in self.request_counts:
                    engine_results[request_count] = self.benchmark_requests(
                        engine_name, func, request_count, data
                    )
                
                suite_results[engine_name] = engine_results
            
            all_results[suite_name] = suite_results
            self._print_suite_results(suite_name, suite_results)
        
        self._print_overall_summary(all_results)
        return all_results
    
    def _get_test_scenarios(self):
        """Generate test data for different scenarios."""
        return {
            'simple': {
                'cls': 'welcome-message',
                'content': 'Welcome to our realistic benchmark!'
            },
            'complex': {
                'lang': 'en',
                'title': 'Realistic Template Benchmark',
                'heading': 'Real-World Performance Testing',
                'nav_links': [
                    {'url': '/', 'text': 'Home'},
                    {'url': '/products', 'text': 'Products'},
                    {'url': '/about', 'text': 'About'},
                    {'url': '/contact', 'text': 'Contact'}
                ],
                'section_title': 'Template Engine Comparison',
                'description': 'Measuring template engines as they are actually used in production applications.',
                'features': [
                    '📁 File-based templates',
                    '⏱️ Realistic request processing',
                    '🌐 Production-like scenarios',
                    '📊 Time-based metrics'
                ],
                'footer_text': '© 2024 Realistic Template Benchmark'
            },
            'products': {
                'title': 'Featured Products',
                'products': [
                    {
                        'id': i,
                        'name': f'Product {i}',
                        'price': f'{19.99 + i * 10:.2f}',
                        'description': f'High-quality product {i} with excellent features and great value.',
                        'tags': [f'tag{j}' for j in range(3)]
                    }
                    for i in range(25)
                ]
            }
        }
    
    def _simple_template_benchmarks(self):
        """Simple template rendering benchmarks with file loading."""
        return {
            'RustyTags': lambda data: rt.Div(data['content'], class_=data['cls']),
            'Air': lambda data: Div(data['content'], cls=data['cls']).render(),
            'Jinja2': lambda data: self.jinja_env.get_template('simple.jinja2').render(**data),
            'Mako': lambda data: self.mako_lookup.get_template('simple.mako').render(**data),
        }
    
    def _complex_template_benchmarks(self):
        """Complex template rendering benchmarks with file loading."""
        return {
            'RustyTags': self._rusty_complex_template,
            'Air': self._air_complex_template,
            'Jinja2': lambda data: self.jinja_env.get_template('complex.jinja2').render(**data),
            'Mako': lambda data: self.mako_lookup.get_template('complex.mako').render(**data),
        }
    
    def _product_list_benchmarks(self):
        """Product list template benchmarks with file loading."""
        return {
            'RustyTags': self._rusty_product_list,
            'Air': self._air_product_list,
            'Jinja2': lambda data: self.jinja_env.get_template('products.jinja2').render(**data),
            'Mako': lambda data: self.mako_lookup.get_template('products.mako').render(**data),
        }
    
    def _rusty_complex_template(self, data):
        """RustyTags complex template (no file loading - direct generation)."""
        return rt.Html(
            rt.Title(data['title']),
            rt.Div(
                rt.Header(
                    rt.H1(data['heading']),
                    rt.Nav(
                        rt.Ul(
                            *[rt.Li(rt.A(link['text'], href=link['url'])) for link in data['nav_links']]
                        ),
                        class_="main-nav"
                    ),
                    class_="site-header"
                ),
                rt.Main(
                    rt.Section(
                        rt.H2(data['section_title']),
                        rt.P(data['description']),
                        rt.Ul(
                            *[rt.Li(feature) for feature in data['features']],
                            class_="features"
                        ),
                        class_="content"
                    ),
                    class_="main-content"
                ),
                rt.Footer(
                    rt.P(data['footer_text']),
                    class_="site-footer"
                ),
                class_="page-container"
            ),
            lang=data['lang']
        )
    
    def _air_complex_template(self, data):
        """Air complex template (no file loading - direct generation)."""
        return AirHtml(
            Title(data['title']),
            Div(
                Header(
                    H1(data['heading']),
                    Nav(
                        Ul(
                            *[Li(A(link['text'], href=link['url'])) for link in data['nav_links']]
                        ),
                        cls="main-nav"
                    ),
                    cls="site-header"
                ),
                Main(
                    Section(
                        H2(data['section_title']),
                        P(data['description']),
                        Ul(
                            *[Li(feature) for feature in data['features']],
                            cls="features"
                        ),
                        cls="content"
                    ),
                    cls="main-content"
                ),
                Footer(
                    P(data['footer_text']),
                    cls="site-footer"
                ),
                cls="page-container"
            ),
            lang=data['lang']
        ).render()
    
    def _rusty_product_list(self, data):
        """RustyTags product list template."""
        return rt.Div(
            rt.H2(data['title']),
            rt.Div(
                *[rt.Div(
                    rt.H3(product['name']),
                    rt.P(f"${product['price']}", class_="price"),
                    rt.P(product['description'], class_="description"),
                    rt.Div(
                        *[rt.Span(tag, class_="tag") for tag in product['tags']],
                        class_="tags"
                    ),
                    class_="product-card",
                    **{"data-id": str(product['id'])}
                ) for product in data['products']],
                class_="products"
            ),
            class_="product-list"
        )
    
    def _air_product_list(self, data):
        """Air product list template."""
        return Div(
            H2(data['title']),
            Div(
                *[Div(
                    H3(product['name']),
                    P(f"${product['price']}", cls="price"),
                    P(product['description'], cls="description"),
                    Div(
                        *[Span(tag, cls="tag") for tag in product['tags']],
                        cls="tags"
                    ),
                    cls="product-card",
                    **{"data-id": str(product['id'])}
                ) for product in data['products']],
                cls="products"
            ),
            cls="product-list"
        ).render()
    
    def _print_suite_results(self, suite_name: str, results: Dict[str, Dict[int, Dict[str, float]]]):
        """Print formatted results for a benchmark suite."""
        print(f"\\n📈 {suite_name} - Time to Process Requests:")
        print("-" * 80)
        
        # Headers
        print(f"{'Engine':<12} ", end="")
        for count in self.request_counts:
            print(f"{count:>8} req", end="")
        print()
        
        print("-" * 80)
        
        for engine_name, engine_results in results.items():
            print(f"{engine_name:<12} ", end="")
            for count in self.request_counts:
                if count in engine_results:
                    time_ms = engine_results[count]['total_time'] * 1000
                    print(f"{time_ms:>7.1f}ms", end="")
                else:
                    print(f"{'N/A':>8}", end="")
            print()
        
        # Show requests per second for largest request count
        largest_count = max(self.request_counts)
        print(f"\\n📊 Requests/Second ({largest_count:,} requests):")
        print("-" * 40)
        
        engine_rps = []
        for engine_name, engine_results in results.items():
            if largest_count in engine_results:
                rps = engine_results[largest_count]['requests_per_second']
                engine_rps.append((engine_name, rps))
        
        # Sort by RPS descending
        engine_rps.sort(key=lambda x: x[1], reverse=True)
        
        for i, (engine_name, rps) in enumerate(engine_rps, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal} {engine_name:<12} {rps:>8.0f} req/sec")
    
    def _print_overall_summary(self, all_results):
        """Print overall benchmark summary."""
        print("\\n🏆 REALISTIC TEMPLATE BENCHMARK SUMMARY")
        print("=" * 60)
        
        print("\\n📊 Key Findings:")
        print("• Templates loaded from files (realistic usage)")
        print("• Includes file I/O overhead (template loading)")
        print("• Time-based metrics (easier to understand)")
        print("• Production-like scenarios tested")
        
        print("\\n🎯 When to Use Each Engine:")
        print("• RustyTags: High-performance apps needing Python syntax")
        print("• Air: Simple Python apps prioritizing readability")
        print("• Jinja2: Complex templating with advanced features")
        print("• Mako: Maximum template performance with Python expressions")

def main():
    """Run the realistic template engine benchmark."""
    print("🌐 Realistic Template Engine Benchmark Suite")
    print("Testing templates as they're used in real applications...")
    
    benchmark = RealisticTemplateBenchmark(request_counts=[100, 500, 1000, 5000])
    results = benchmark.run_realistic_benchmark_suite()
    
    print("\\n✨ Benchmark Complete!")
    print("This shows real-world performance including file I/O overhead.")

if __name__ == "__main__":
    main()