#!/usr/bin/env python3
"""
Fair Template Engine Benchmark: RustyTags vs Air vs Jinja2 vs Mako

This benchmark provides a fair comparison by:
1. Pre-compiling all templates (Jinja2/Mako compilation overhead excluded)
2. Only measuring rendering performance
3. Using equivalent template structures across all engines
4. Testing both static and dynamic content scenarios
"""

import sys
import os
import time
import statistics
from typing import Callable, List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rusty_tags as rt
from air.tags import *
from air.tags import Html as AirHtml
import jinja2
from mako.template import Template as MakoTemplate

class TemplateEngineBenchmark:
    """Fair comparison of template engines with pre-compiled templates."""
    
    def __init__(self, warmup_runs=3, test_runs=15):
        self.warmup_runs = warmup_runs
        self.test_runs = test_runs
        self.results = {}
        
        # Pre-compile all templates to ensure fair comparison
        self._setup_templates()
    
    def _setup_templates(self):
        """Pre-compile all templates for fair performance comparison."""
        print("🔧 Pre-compiling templates for fair comparison...")
        
        # Jinja2 templates (pre-compiled)
        jinja_env = jinja2.Environment()
        
        self.jinja_simple = jinja_env.from_string('<div class="{{ cls }}">{{ content }}</div>')
        
        self.jinja_complex = jinja_env.from_string('''
<!doctype html><html lang="{{ lang }}">
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
</html>
        '''.strip())
        
        self.jinja_list = jinja_env.from_string('''
<ul class="{{ list_class }}">
{% for item in items %}
    <li class="item-{{ loop.index0 }}">{{ item.name }} - {{ item.value }}</li>
{% endfor %}
</ul>
        '''.strip())
        
        self.jinja_table = jinja_env.from_string('''
<table class="{{ table_class }}">
    <thead>
        <tr>
        {% for header in headers %}
            <th>{{ header }}</th>
        {% endfor %}
        </tr>
    </thead>
    <tbody>
    {% for row in rows %}
        <tr class="row-{{ 'even' if loop.index0 % 2 == 0 else 'odd' }}">
        {% for cell in row %}
            <td>{{ cell }}</td>
        {% endfor %}
        </tr>
    {% endfor %}
    </tbody>
</table>
        '''.strip())
        
        # Mako templates (pre-compiled)
        self.mako_simple = MakoTemplate('<div class="${cls}">${content}</div>')
        
        self.mako_complex = MakoTemplate('''
<!doctype html><html lang="${lang}">
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
</html>
        '''.strip())
        
        self.mako_list = MakoTemplate('''
<ul class="${list_class}">
% for i, item in enumerate(items):
    <li class="item-${i}">${item['name']} - ${item['value']}</li>
% endfor
</ul>
        '''.strip())
        
        self.mako_table = MakoTemplate('''
<table class="${table_class}">
    <thead>
        <tr>
        % for header in headers:
            <th>${header}</th>
        % endfor
        </tr>
    </thead>
    <tbody>
    % for i, row in enumerate(rows):
        <tr class="row-${'even' if i % 2 == 0 else 'odd'}">
        % for cell in row:
            <td>${cell}</td>
        % endfor
        </tr>
    % endfor
    </tbody>
</table>
        '''.strip())
        
        print("✅ All templates pre-compiled successfully!")
    
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
    
    def run_template_benchmark_suite(self):
        """Run comprehensive template engine benchmarks."""
        print("\n🏁 FAIR TEMPLATE ENGINE BENCHMARK")
        print("=" * 60)
        print("🔧 All templates pre-compiled for fair comparison")
        print("⚡ Only measuring rendering performance")
        
        # Test data for dynamic content
        test_data = self._get_test_data()
        
        # Define benchmark suites
        benchmark_suites = [
            ("Simple Tag Rendering", self._simple_benchmarks, test_data['simple']),
            ("Complex Page Rendering", self._complex_benchmarks, test_data['complex']),
            ("Dynamic List Rendering", self._list_benchmarks, test_data['list']),
            ("Data Table Rendering", self._table_benchmarks, test_data['table']),
        ]
        
        all_results = {}
        
        for suite_name, benchmark_funcs, data in benchmark_suites:
            print(f"\n🚀 Running {suite_name} Benchmark")
            print("=" * 60)
            
            suite_results = {}
            benchmark_funcs_dict = benchmark_funcs()
            
            for name, func in benchmark_funcs_dict.items():
                print(f"Benchmarking {name}...")
                suite_results[name] = self.benchmark_function(name, func, data)
            
            all_results[suite_name] = suite_results
            self._print_suite_results(suite_name, suite_results)
        
        self._print_overall_summary(all_results)
        return all_results
    
    def _get_test_data(self):
        """Generate test data for dynamic content."""
        return {
            'simple': {
                'cls': 'test-class',
                'content': 'Hello, World!'
            },
            'complex': {
                'lang': 'en',
                'title': 'Complex Page Test',
                'heading': 'Welcome to Template Benchmark',
                'nav_links': [
                    {'url': '/', 'text': 'Home'},
                    {'url': '/about', 'text': 'About'},
                    {'url': '/contact', 'text': 'Contact'}
                ],
                'section_title': 'Performance Testing',
                'description': 'Comparing template engine rendering performance.',
                'features': [
                    '🚀 Fast rendering',
                    '🐍 Pythonic syntax', 
                    '⚡ Optimized performance',
                    '🧠 Smart caching'
                ],
                'footer_text': '© 2024 Template Benchmark Suite'
            },
            'list': {
                'list_class': 'dynamic-list',
                'items': [
                    {'name': f'Item {i}', 'value': f'Value {i}'} 
                    for i in range(50)
                ]
            },
            'table': {
                'table_class': 'data-table',
                'headers': ['ID', 'Name', 'Email', 'Status'],
                'rows': [
                    [str(i), f'User {i}', f'user{i}@example.com', 'Active' if i % 2 == 0 else 'Inactive']
                    for i in range(25)
                ]
            }
        }
    
    def _simple_benchmarks(self):
        """Simple tag rendering benchmarks."""
        return {
            'RustyTags': lambda data: rt.Div(data['content'], class_=data['cls']).render(),
            'Air': lambda data: Div(data['content'], cls=data['cls']).render(),
            'Jinja2': lambda data: self.jinja_simple.render(**data),
            'Mako': lambda data: self.mako_simple.render(**data),
        }
    
    def _complex_benchmarks(self):
        """Complex page rendering benchmarks."""
        return {
            'RustyTags': self._rusty_complex,
            'Air': self._air_complex, 
            'Jinja2': lambda data: self.jinja_complex.render(**data),
            'Mako': lambda data: self.mako_complex.render(**data),
        }
    
    def _list_benchmarks(self):
        """Dynamic list rendering benchmarks."""
        return {
            'RustyTags': self._rusty_list,
            'Air': self._air_list,
            'Jinja2': lambda data: self.jinja_list.render(**data),
            'Mako': lambda data: self.mako_list.render(**data),
        }
    
    def _table_benchmarks(self):
        """Data table rendering benchmarks."""
        return {
            'RustyTags': self._rusty_table,
            'Air': self._air_table,
            'Jinja2': lambda data: self.jinja_table.render(**data),
            'Mako': lambda data: self.mako_table.render(**data),
        }
    
    def _rusty_complex(self, data):
        """RustyTags complex page rendering."""
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
        ).render()
    
    def _air_complex(self, data):
        """Air complex page rendering."""
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
    
    def _rusty_list(self, data):
        """RustyTags list rendering."""
        return rt.Ul(
            *[rt.Li(f"{item['name']} - {item['value']}", class_=f"item-{i}") 
              for i, item in enumerate(data['items'])],
            class_=data['list_class']
        ).render()
    
    def _air_list(self, data):
        """Air list rendering."""
        return Ul(
            *[Li(f"{item['name']} - {item['value']}", cls=f"item-{i}") 
              for i, item in enumerate(data['items'])],
            cls=data['list_class']
        ).render()
    
    def _rusty_table(self, data):
        """RustyTags table rendering."""
        return rt.Table(
            rt.Thead(
                rt.Tr(*[rt.Th(header) for header in data['headers']])
            ),
            rt.Tbody(
                *[rt.Tr(
                    *[rt.Td(cell) for cell in row],
                    class_="row-" + ("even" if i % 2 == 0 else "odd")
                ) for i, row in enumerate(data['rows'])]
            ),
            class_=data['table_class']
        ).render()
    
    def _air_table(self, data):
        """Air table rendering."""
        return Table(
            Thead(
                Tr(*[Th(header) for header in data['headers']])
            ),
            Tbody(
                *[Tr(
                    *[Td(cell) for cell in row],
                    cls="row-" + ("even" if i % 2 == 0 else "odd")
                ) for i, row in enumerate(data['rows'])]
            ),
            cls=data['table_class']
        ).render()
    
    def _print_suite_results(self, suite_name: str, results: Dict[str, Dict[str, float]]):
        """Print formatted results for a benchmark suite."""
        print(f"\n📊 {suite_name} Results:")
        print("-" * 60)
        
        # Find the fastest implementation
        fastest_time = min(r['mean'] for r in results.values())
        
        for name, stats in results.items():
            mean_ms = stats['mean'] * 1000
            ops_per_sec = 1 / stats['mean'] if stats['mean'] > 0 else 0
            speedup = fastest_time / stats['mean'] if stats['mean'] > 0 else 0
            
            if stats['mean'] == fastest_time:
                status = "🥇"
            elif speedup >= 0.8:
                status = f"🥈 {speedup:.1f}x slower"
            else:
                status = f"🔸 {speedup:.1f}x slower"
            
            print(f"{name:12} {mean_ms:8.3f}ms  {ops_per_sec:8.0f} ops/sec  {status}")
    
    def _print_overall_summary(self, all_results):
        """Print overall benchmark summary."""
        print("\n🏆 TEMPLATE ENGINE BENCHMARK SUMMARY")
        print("=" * 60)
        
        # Count wins for each engine
        engines = ['RustyTags', 'Air', 'Jinja2', 'Mako']
        wins = {engine: 0 for engine in engines}
        
        for suite_name, results in all_results.items():
            fastest_time = min(r['mean'] for r in results.values())
            winner = None
            for name, stats in results.items():
                if stats['mean'] == fastest_time:
                    winner = name
                    break
            
            if winner:
                wins[winner] += 1
            
            # Calculate average performance for each engine in this suite
            suite_avg = {}
            for name, stats in results.items():
                suite_avg[name] = 1 / stats['mean']  # ops per second
            
            print(f"\n{suite_name}:")
            sorted_engines = sorted(suite_avg.items(), key=lambda x: x[1], reverse=True)
            for i, (name, ops_per_sec) in enumerate(sorted_engines, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                print(f"  {medal} {name:<12} {ops_per_sec:>8.0f} ops/sec")
        
        print(f"\n🎯 Overall Championship Results:")
        sorted_wins = sorted(wins.items(), key=lambda x: x[1], reverse=True)
        total_suites = len(all_results)
        
        for i, (engine, win_count) in enumerate(sorted_wins, 1):
            medal = "🏆" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            percentage = (win_count / total_suites) * 100 if total_suites > 0 else 0
            print(f"  {medal} {engine:<12} {win_count}/{total_suites} wins ({percentage:.0f}%)")
        
        champion = sorted_wins[0][0] if sorted_wins else "Unknown"
        print(f"\n🎉 Template Engine Champion: {champion}!")
        
        print(f"\n💡 Key Insights:")
        print(f"• This benchmark pre-compiles templates for fair comparison")
        print(f"• Only pure rendering performance is measured")
        print(f"• RustyTags & Air: Direct function calls (no template compilation)")  
        print(f"• Jinja2 & Mako: Pre-compiled templates (compilation overhead excluded)")
        print(f"• All engines tested with identical dynamic content")

def main():
    """Run the fair template engine benchmark."""
    print("🏁 Fair Template Engine Benchmark Suite")
    print("Pre-compiling templates for accurate performance comparison...")
    
    benchmark = TemplateEngineBenchmark(warmup_runs=5, test_runs=20)
    results = benchmark.run_template_benchmark_suite()
    
    print("\n✨ Benchmark Complete!")
    print("This provides a fair comparison of pure rendering performance.")

if __name__ == "__main__":
    main()