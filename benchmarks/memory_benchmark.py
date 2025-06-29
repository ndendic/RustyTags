#!/usr/bin/env python3
"""
Memory Usage Benchmark: RustyTags vs Air vs Jinja2 vs Mako

This benchmark measures memory consumption patterns for different
HTML generation scenarios.
"""

import sys
import os
import gc
import psutil
import tracemalloc
from typing import Callable, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rusty_tags as rt
from air.tags import *
from air.tags import Html as AirHtml
import jinja2
from mako.template import Template as MakoTemplate

class MemoryBenchmark:
    """Measures memory usage for HTML generation tasks."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def measure_memory_usage(self, name: str, func: Callable, iterations: int = 1000):
        """Measure memory usage for a function."""
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Start tracing malloc
        tracemalloc.start()
        
        # Run the function multiple times
        results = []
        for _ in range(iterations):
            results.append(func())
        
        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Final memory measurement
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Force cleanup
        del results
        gc.collect()
        
        return {
            'name': name,
            'iterations': iterations,
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_increase_mb': final_memory - initial_memory,
            'traced_current_mb': current / 1024 / 1024,
            'traced_peak_mb': peak / 1024 / 1024,
            'memory_per_iteration_kb': (peak / 1024) / iterations if iterations > 0 else 0
        }
    
    def run_memory_benchmark_suite(self):
        """Run comprehensive memory benchmarks."""
        print("🧠 Memory Usage Benchmark Suite")
        print("=" * 50)
        
        benchmarks = [
            ("RustyTags Simple", lambda: rt.Div("Hello", class_="test").render()),
            ("Air Simple", lambda: Div("Hello", cls="test").render()),
            ("Jinja2 Simple", lambda: jinja2.Template('<div class="test">Hello</div>').render()),
            ("Mako Simple", lambda: MakoTemplate('<div class="test">Hello</div>').render()),
            
            ("RustyTags Complex", self._complex_rusty),
            ("Air Complex", self._complex_air),
            ("Jinja2 Complex", self._complex_jinja),
            ("Mako Complex", self._complex_mako),
            
            ("RustyTags List", self._list_rusty),
            ("Air List", self._list_air),
            ("Jinja2 List", self._list_jinja),
            ("Mako List", self._list_mako),
        ]
        
        results = []
        
        for name, func in benchmarks:
            print(f"Measuring {name}...")
            result = self.measure_memory_usage(name, func, iterations=1000)
            results.append(result)
        
        self._print_memory_results(results)
        return results
    
    def _complex_rusty(self):
        """Complex page generation with RustyTags."""
        return rt.Html(
            rt.Title("Test Page"),
            rt.Div(
                rt.H1("Title"),
                rt.P("Content", class_="text"),
                rt.Ul(*[rt.Li(f"Item {i}") for i in range(10)]),
                class_="container"
            ),
            lang="en"
        ).render()
    
    def _complex_air(self):
        """Complex page generation with Air."""
        return AirHtml(
            Title("Test Page"),
            Div(
                H1("Title"),
                P("Content", cls="text"),
                Ul(*[Li(f"Item {i}") for i in range(10)]),
                cls="container"
            ),
            lang="en"
        ).render()
    
    def _complex_jinja(self):
        """Complex page generation with Jinja2."""
        template = jinja2.Template('''
<!doctype html><html lang="en">
<head><title>Test Page</title></head>
<body>
<div class="container">
    <h1>Title</h1>
    <p class="text">Content</p>
    <ul>
    {% for i in range(10) %}
        <li>Item {{ i }}</li>
    {% endfor %}
    </ul>
</div>
</body>
</html>
        '''.strip())
        return template.render()
    
    def _complex_mako(self):
        """Complex page generation with Mako."""
        template = MakoTemplate('''
<!doctype html><html lang="en">
<head><title>Test Page</title></head>
<body>
<div class="container">
    <h1>Title</h1>
    <p class="text">Content</p>
    <ul>
    % for i in range(10):
        <li>Item ${i}</li>
    % endfor
    </ul>
</div>
</body>
</html>
        '''.strip())
        return template.render()
    
    def _list_rusty(self):
        """List generation with RustyTags."""
        return rt.Ul(*[rt.Li(f"Item {i}", class_=f"item-{i}") for i in range(50)]).render()
    
    def _list_air(self):
        """List generation with Air."""
        return Ul(*[Li(f"Item {i}", cls=f"item-{i}") for i in range(50)]).render()
    
    def _list_jinja(self):
        """List generation with Jinja2."""
        template = jinja2.Template('''
<ul>
{% for i in range(50) %}
    <li class="item-{{ i }}">Item {{ i }}</li>
{% endfor %}
</ul>
        '''.strip())
        return template.render()
    
    def _list_mako(self):
        """List generation with Mako."""
        template = MakoTemplate('''
<ul>
% for i in range(50):
    <li class="item-${i}">Item ${i}</li>
% endfor
</ul>
        '''.strip())
        return template.render()
    
    def _print_memory_results(self, results):
        """Print formatted memory usage results."""
        print("\n📊 Memory Usage Results (1000 iterations each):")
        print("-" * 70)
        print(f"{'Library':<15} {'Peak MB':<8} {'Per Op KB':<10} {'Increase MB':<12}")
        print("-" * 70)
        
        for result in results:
            print(f"{result['name']:<15} "
                  f"{result['traced_peak_mb']:<8.2f} "
                  f"{result['memory_per_iteration_kb']:<10.2f} "
                  f"{result['memory_increase_mb']:<12.2f}")
        
        print("\n🏆 Memory Efficiency Ranking:")
        sorted_results = sorted(results, key=lambda x: x['memory_per_iteration_kb'])
        
        for i, result in enumerate(sorted_results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2d}."
            print(f"{medal} {result['name']:<20} {result['memory_per_iteration_kb']:>8.2f} KB/op")

def main():
    """Run memory benchmark."""
    benchmark = MemoryBenchmark()
    results = benchmark.run_memory_benchmark_suite()
    
    print("\n💡 Memory Analysis:")
    print("• Lower 'Per Op KB' = more memory efficient")
    print("• RustyTags uses object pooling to reduce allocations")
    print("• String interning reduces memory footprint")
    print("• SIMD operations process data more efficiently")

if __name__ == "__main__":
    main()