#!/usr/bin/env python3
"""
Comprehensive Performance Benchmark: RustyTags vs Air vs Jinja2 vs Mako

This benchmark suite tests HTML generation performance across multiple scenarios
to demonstrate the performance benefits of RustyTags' Rust-powered optimizations.
"""

import time
import statistics
import sys
import os
from typing import Callable, List, Dict, Any

# Add parent directory to path to import our libraries
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all template engines
import rusty_tags as rt
from air.tags import *
from air.tags import Html as AirHtml
import jinja2
from mako.template import Template as MakoTemplate

class BenchmarkRunner:
    """Runs performance benchmarks with statistical analysis."""
    
    def __init__(self, warmup_runs=3, test_runs=10):
        self.warmup_runs = warmup_runs
        self.test_runs = test_runs
        self.results = {}
    
    def benchmark_function(self, name: str, func: Callable, *args, **kwargs) -> Dict[str, float]:
        """Benchmark a function with warmup and multiple runs."""
        # Warmup runs
        for _ in range(self.warmup_runs):
            func(*args, **kwargs)
        
        # Timed runs
        times = []
        for _ in range(self.test_runs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times),
            'times': times
        }
    
    def run_benchmark_suite(self, suite_name: str, benchmarks: Dict[str, Callable]):
        """Run a complete benchmark suite."""
        print(f"\n🚀 Running {suite_name} Benchmark Suite")
        print("=" * 60)
        
        suite_results = {}
        
        for name, func in benchmarks.items():
            print(f"Benchmarking {name}...")
            suite_results[name] = self.benchmark_function(name, func)
        
        self.results[suite_name] = suite_results
        self._print_suite_results(suite_name, suite_results)
    
    def _print_suite_results(self, suite_name: str, results: Dict[str, Dict[str, float]]):
        """Print formatted results for a benchmark suite."""
        print(f"\n📊 {suite_name} Results:")
        print("-" * 60)
        
        # Find the fastest implementation
        fastest_time = min(r['mean'] for r in results.values())
        
        for name, stats in results.items():
            mean_ms = stats['mean'] * 1000
            speedup = fastest_time / stats['mean'] if stats['mean'] > 0 else 0
            
            status = "🥇" if stats['mean'] == fastest_time else f"🔸 {speedup:.1f}x slower"
            
            print(f"{name:15} {mean_ms:8.3f}ms  ±{stats['stdev']*1000:6.3f}ms  {status}")
        
        print()

# =============================================================================
# BENCHMARK TEST CASES
# =============================================================================

def simple_tag_rusty():
    """RustyTags: Simple div with class."""
    return rt.Div("Hello World", class_="greeting")

def simple_tag_air():
    """Air: Simple div with class."""
    return Div("Hello World", cls="greeting").render()

def simple_tag_jinja():
    """Jinja2: Simple div with class."""
    template = jinja2.Template('<div class="greeting">Hello World</div>')
    return template.render()

def simple_tag_mako():
    """Mako: Simple div with class."""
    template = MakoTemplate('<div class="greeting">Hello World</div>')
    return template.render()

def complex_page_rusty():
    """RustyTags: Complex nested page structure."""
    return rt.Html(
        rt.Title("Complex Page"),
        rt.Div(
            rt.Header(
                rt.H1("Welcome to RustyTags"),
                rt.Nav(
                    rt.Ul(
                        rt.Li(rt.A("Home", href="/")),
                        rt.Li(rt.A("About", href="/about")),
                        rt.Li(rt.A("Contact", href="/contact"))
                    ),
                    class_="main-nav"
                ),
                class_="site-header"
            ),
            rt.Main(
                rt.Section(
                    rt.H2("Features"),
                    rt.P("Lightning-fast HTML generation with Rust performance."),
                    rt.Ul(
                        rt.Li("🚀 Blazing fast"),
                        rt.Li("🐍 Pythonic API"),
                        rt.Li("⚡ SIMD optimizations"),
                        rt.Li("🧠 Smart caching")
                    ),
                    class_="features"
                ),
                rt.Section(
                    rt.H2("Performance"),
                    rt.P("See the benchmark results below:"),
                    rt.Table(
                        rt.Tr(
                            rt.Th("Library"),
                            rt.Th("Speed"),
                            rt.Th("Memory")
                        ),
                        rt.Tr(
                            rt.Td("RustyTags"),
                            rt.Td("240k+ tags/sec"),
                            rt.Td("Optimized")
                        ),
                        class_="benchmark-table"
                    ),
                    class_="performance"
                ),
                class_="main-content"
            ),
            rt.Footer(
                rt.P("© 2024 RustyTags - Built with Rust + Python"),
                class_="site-footer"
            ),
            class_="page-container"
        ),
        lang="en"
    )

def complex_page_air():
    """Air: Complex nested page structure."""
    return AirHtml(
        Title("Complex Page"),
        Div(
            Header(
                H1("Welcome to RustyTags"),
                Nav(
                    Ul(
                        Li(A("Home", href="/")),
                        Li(A("About", href="/about")),
                        Li(A("Contact", href="/contact"))
                    ),
                    cls="main-nav"
                ),
                cls="site-header"
            ),
            Main(
                Section(
                    H2("Features"),
                    P("Lightning-fast HTML generation with Rust performance."),
                    Ul(
                        Li("🚀 Blazing fast"),
                        Li("🐍 Pythonic API"),
                        Li("⚡ SIMD optimizations"),
                        Li("🧠 Smart caching")
                    ),
                    cls="features"
                ),
                Section(
                    H2("Performance"),
                    P("See the benchmark results below:"),
                    Table(
                        Tr(
                            Th("Library"),
                            Th("Speed"),
                            Th("Memory")
                        ),
                        Tr(
                            Td("RustyTags"),
                            Td("240k+ tags/sec"),
                            Td("Optimized")
                        ),
                        cls="benchmark-table"
                    ),
                    cls="performance"
                ),
                cls="main-content"
            ),
            Footer(
                P("© 2024 RustyTags - Built with Rust + Python"),
                cls="site-footer"
            ),
            cls="page-container"
        ),
        lang="en"
    ).render()

def complex_page_jinja():
    """Jinja2: Complex nested page structure."""
    template = jinja2.Template('''
<!doctype html><html lang="en">
<head><title>Complex Page</title></head>
<body>
<div class="page-container">
    <header class="site-header">
        <h1>Welcome to RustyTags</h1>
        <nav class="main-nav">
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main class="main-content">
        <section class="features">
            <h2>Features</h2>
            <p>Lightning-fast HTML generation with Rust performance.</p>
            <ul>
                <li>🚀 Blazing fast</li>
                <li>🐍 Pythonic API</li>
                <li>⚡ SIMD optimizations</li>
                <li>🧠 Smart caching</li>
            </ul>
        </section>
        <section class="performance">
            <h2>Performance</h2>
            <p>See the benchmark results below:</p>
            <table class="benchmark-table">
                <tr><th>Library</th><th>Speed</th><th>Memory</th></tr>
                <tr><td>RustyTags</td><td>240k+ tags/sec</td><td>Optimized</td></tr>
            </table>
        </section>
    </main>
    <footer class="site-footer">
        <p>© 2024 RustyTags - Built with Rust + Python</p>
    </footer>
</div>
</body>
</html>
    '''.strip())
    return template.render()

def complex_page_mako():
    """Mako: Complex nested page structure."""
    template = MakoTemplate('''
<!doctype html><html lang="en">
<head><title>Complex Page</title></head>
<body>
<div class="page-container">
    <header class="site-header">
        <h1>Welcome to RustyTags</h1>
        <nav class="main-nav">
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main class="main-content">
        <section class="features">
            <h2>Features</h2>
            <p>Lightning-fast HTML generation with Rust performance.</p>
            <ul>
                <li>🚀 Blazing fast</li>
                <li>🐍 Pythonic API</li>
                <li>⚡ SIMD optimizations</li>
                <li>🧠 Smart caching</li>
            </ul>
        </section>
        <section class="performance">
            <h2>Performance</h2>
            <p>See the benchmark results below:</p>
            <table class="benchmark-table">
                <tr><th>Library</th><th>Speed</th><th>Memory</th></tr>
                <tr><td>RustyTags</td><td>240k+ tags/sec</td><td>Optimized</td></tr>
            </table>
        </section>
    </main>
    <footer class="site-footer">
        <p>© 2024 RustyTags - Built with Rust + Python</p>
    </footer>
</div>
</body>
</html>
    '''.strip())
    return template.render()

def attribute_heavy_rusty():
    """RustyTags: Tag with many attributes."""
    return rt.Div(
        "Content with many attributes",
        class_="main-content primary-section",
        id="content-section-1",
        data_role="content",
        data_level="primary", 
        data_index="1",
        data_category="main",
        style="color: blue; margin: 10px; padding: 20px;",
        title="Main content section",
        role="main",
        aria_label="Primary content area"
    )

def attribute_heavy_air():
    """Air: Tag with many attributes."""
    return Div(
        "Content with many attributes",
        cls="main-content primary-section",
        id="content-section-1",
        data_role="content",
        data_level="primary",
        data_index="1", 
        data_category="main",
        style="color: blue; margin: 10px; padding: 20px;",
        title="Main content section",
        role="main",
        aria_label="Primary content area"
    ).render()

def attribute_heavy_jinja():
    """Jinja2: Tag with many attributes."""
    template = jinja2.Template('''
<div class="main-content primary-section" id="content-section-1" data-role="content" data-level="primary" data-index="1" data-category="main" style="color: blue; margin: 10px; padding: 20px;" title="Main content section" role="main" aria-label="Primary content area">Content with many attributes</div>
    '''.strip())
    return template.render()

def attribute_heavy_mako():
    """Mako: Tag with many attributes."""
    template = MakoTemplate('''
<div class="main-content primary-section" id="content-section-1" data-role="content" data-level="primary" data-index="1" data-category="main" style="color: blue; margin: 10px; padding: 20px;" title="Main content section" role="main" aria-label="Primary content area">Content with many attributes</div>
    '''.strip())
    return template.render()

def list_generation_rusty():
    """RustyTags: Generate a list with 100 items."""
    return rt.Ul(
        *[rt.Li(f"List item {i}", class_=f"item-{i}") for i in range(100)],
        class_="large-list"
    )

def list_generation_air():
    """Air: Generate a list with 100 items."""
    return Ul(
        *[Li(f"List item {i}", cls=f"item-{i}") for i in range(100)],
        cls="large-list"
    ).render()

def list_generation_jinja():
    """Jinja2: Generate a list with 100 items."""
    template = jinja2.Template('''
<ul class="large-list">
{% for i in range(100) %}
    <li class="item-{{ i }}">List item {{ i }}</li>
{% endfor %}
</ul>
    '''.strip())
    return template.render()

def list_generation_mako():
    """Mako: Generate a list with 100 items."""
    template = MakoTemplate('''
<ul class="large-list">
% for i in range(100):
    <li class="item-${i}">List item ${i}</li>
% endfor
</ul>
    '''.strip())
    return template.render()

def table_generation_rusty():
    """RustyTags: Generate a table with 50 rows."""
    return rt.Table(
        rt.Thead(
            rt.Tr(
                rt.Th("ID"),
                rt.Th("Name"),
                rt.Th("Email"),
                rt.Th("Status")
            )
        ),
        rt.Tbody(
            *[rt.Tr(
                rt.Td(str(i)),
                rt.Td(f"User {i}"),
                rt.Td(f"user{i}@example.com"),
                rt.Td("Active" if i % 2 == 0 else "Inactive"),
                class_="row-" + ("even" if i % 2 == 0 else "odd")
            ) for i in range(50)]
        ),
        class_="data-table"
    )

def table_generation_air():
    """Air: Generate a table with 50 rows."""
    return Table(
        Thead(
            Tr(
                Th("ID"),
                Th("Name"),
                Th("Email"),
                Th("Status")
            )
        ),
        Tbody(
            *[Tr(
                Td(str(i)),
                Td(f"User {i}"),
                Td(f"user{i}@example.com"),
                Td("Active" if i % 2 == 0 else "Inactive"),
                cls="row-" + ("even" if i % 2 == 0 else "odd")
            ) for i in range(50)]
        ),
        cls="data-table"
    ).render()

def table_generation_jinja():
    """Jinja2: Generate a table with 50 rows."""
    template = jinja2.Template('''
<table class="data-table">
    <thead>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
    </thead>
    <tbody>
    {% for i in range(50) %}
        <tr class="row-{{ 'even' if i % 2 == 0 else 'odd' }}">
            <td>{{ i }}</td>
            <td>User {{ i }}</td>
            <td>user{{ i }}@example.com</td>
            <td>{{ 'Active' if i % 2 == 0 else 'Inactive' }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
    '''.strip())
    return template.render()

def table_generation_mako():
    """Mako: Generate a table with 50 rows."""
    template = MakoTemplate('''
<table class="data-table">
    <thead>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
    </thead>
    <tbody>
    % for i in range(50):
        <tr class="row-${'even' if i % 2 == 0 else 'odd'}">
            <td>${i}</td>
            <td>User ${i}</td>
            <td>user${i}@example.com</td>
            <td>${'Active' if i % 2 == 0 else 'Inactive'}</td>
        </tr>
    % endfor
    </tbody>
</table>
    '''.strip())
    return template.render()

# =============================================================================
# MAIN BENCHMARK EXECUTION
# =============================================================================

def main():
    """Run all benchmark suites."""
    print("🏁 RustyTags Comprehensive Performance Benchmark")
    print("Testing against Air, Jinja2, and Mako template engines")
    print("🦀 Rust-powered optimizations vs Pure Python implementations")
    
    runner = BenchmarkRunner(warmup_runs=5, test_runs=20)
    
    # Test suite 1: Simple tag generation
    simple_benchmarks = {
        "RustyTags": simple_tag_rusty,
        "Air": simple_tag_air,
        "Jinja2": simple_tag_jinja,
        "Mako": simple_tag_mako,
    }
    
    # Test suite 2: Complex page generation
    complex_benchmarks = {
        "RustyTags": complex_page_rusty,
        "Air": complex_page_air,
        "Jinja2": complex_page_jinja,
        "Mako": complex_page_mako,
    }
    
    # Test suite 3: Attribute-heavy tags
    attribute_benchmarks = {
        "RustyTags": attribute_heavy_rusty,
        "Air": attribute_heavy_air,
        "Jinja2": attribute_heavy_jinja,
        "Mako": attribute_heavy_mako,
    }
    
    # Test suite 4: List generation
    list_benchmarks = {
        "RustyTags": list_generation_rusty,
        "Air": list_generation_air,
        "Jinja2": list_generation_jinja,
        "Mako": list_generation_mako,
    }
    
    # Test suite 5: Table generation
    table_benchmarks = {
        "RustyTags": table_generation_rusty,
        "Air": table_generation_air,
        "Jinja2": table_generation_jinja,
        "Mako": table_generation_mako,
    }
    
    # Run all benchmark suites
    runner.run_benchmark_suite("Simple Tag Generation", simple_benchmarks)
    runner.run_benchmark_suite("Complex Page Generation", complex_benchmarks)
    runner.run_benchmark_suite("Attribute-Heavy Tags", attribute_benchmarks)
    runner.run_benchmark_suite("List Generation (100 items)", list_benchmarks)
    runner.run_benchmark_suite("Table Generation (50 rows)", table_benchmarks)
    
    # Summary
    print("\n🎯 BENCHMARK SUMMARY")
    print("=" * 60)
    
    rusty_wins = 0
    total_suites = len(runner.results)
    
    for suite_name, results in runner.results.items():
        fastest_time = min(r['mean'] for r in results.values())
        fastest_library = None
        for name, stats in results.items():
            if stats['mean'] == fastest_time:
                fastest_library = name
                break
        
        if fastest_library == "RustyTags":
            rusty_wins += 1
        
        print(f"{suite_name:30} Winner: {fastest_library}")
    
    print(f"\nRustyTags won {rusty_wins}/{total_suites} benchmark suites! 🏆")
    
    if rusty_wins == total_suites:
        print("\n🚀 RustyTags DOMINATED all benchmarks!")
        print("💪 Rust-powered performance is the clear winner!")
    elif rusty_wins >= total_suites // 2:
        print(f"\n⚡ RustyTags won {rusty_wins}/{total_suites} benchmarks - excellent performance!")
    else:
        print(f"\n📊 RustyTags competitive in {rusty_wins}/{total_suites} benchmarks")
    
    print("\n🔬 Performance characteristics:")
    print("• RustyTags: Rust optimizations, SIMD, object pooling, caching")
    print("• Air: Pure Python, optimized for simplicity")
    print("• Jinja2: Mature template engine with compilation")
    print("• Mako: Fast template engine with compilation")
    print("\n✨ Choose RustyTags for maximum performance with Pythonic syntax!")

if __name__ == "__main__":
    main()