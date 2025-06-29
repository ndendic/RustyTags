#!/usr/bin/env python3
"""
Stress Test: RustyTags vs Air vs Jinja2 vs Mako

This stress test pushes each template engine to its limits with
high-volume HTML generation scenarios.
"""

import sys
import os
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rusty_tags as rt
from air.tags import *
from air.tags import Html as AirHtml
import jinja2
from mako.template import Template as MakoTemplate

class StressTest:
    """High-volume stress testing for template engines."""
    
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
    
    def single_thread_stress(self, name: str, func: Callable, iterations: int = 50000):
        """Single-threaded stress test."""
        print(f"Single-thread stress test: {name} ({iterations:,} iterations)")
        
        start_time = time.perf_counter()
        
        for i in range(iterations):
            result = func(i)
            # Simulate some processing of the result
            len(result)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        ops_per_sec = iterations / duration if duration > 0 else 0
        
        print(f"  ✅ {duration:.3f}s | {ops_per_sec:,.0f} ops/sec | {duration*1000000/iterations:.1f}μs per op")
        return duration, ops_per_sec
    
    def multi_thread_stress(self, name: str, func: Callable, iterations: int = 20000, threads: int = None):
        """Multi-threaded stress test."""
        if threads is None:
            threads = self.cpu_count
        
        print(f"Multi-thread stress test: {name} ({iterations:,} total iterations, {threads} threads)")
        
        iterations_per_thread = iterations // threads
        
        def worker_func(thread_id):
            for i in range(iterations_per_thread):
                result = func(i + thread_id * iterations_per_thread)
                len(result)
        
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker_func, i) for i in range(threads)]
            for future in futures:
                future.result()
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        total_ops = iterations_per_thread * threads
        ops_per_sec = total_ops / duration if duration > 0 else 0
        
        print(f"  ✅ {duration:.3f}s | {ops_per_sec:,.0f} ops/sec | {duration*1000000/total_ops:.1f}μs per op")
        return duration, ops_per_sec
    
    def memory_pressure_test(self, name: str, func: Callable, iterations: int = 10000):
        """Test under memory pressure with large objects."""
        print(f"Memory pressure test: {name} ({iterations:,} large objects)")
        
        results = []
        start_time = time.perf_counter()
        
        for i in range(iterations):
            # Generate large HTML structures
            result = func(i, large=True)
            results.append(result)
            
            # Every 1000 iterations, check memory and potentially clean up
            if i % 1000 == 0 and i > 0:
                # Keep only recent results to prevent excessive memory usage
                if len(results) > 5000:
                    results = results[-2500:]
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        ops_per_sec = iterations / duration if duration > 0 else 0
        
        # Calculate average result size
        avg_size = sum(len(r) for r in results[-100:]) / min(100, len(results))
        
        print(f"  ✅ {duration:.3f}s | {ops_per_sec:,.0f} ops/sec | {avg_size:.0f} avg bytes")
        return duration, ops_per_sec
    
    def run_all_stress_tests(self):
        """Run comprehensive stress tests."""
        print("🔥 STRESS TEST SUITE")
        print("=" * 60)
        
        # Define test functions
        test_functions = {
            "RustyTags": self._rusty_stress_func,
            "Air": self._air_stress_func,
            "Jinja2": self._jinja_stress_func,
            "Mako": self._mako_stress_func,
        }
        
        results = {}
        
        # Single-threaded stress test
        print("\n🔸 Single-Threaded Stress Test")
        print("-" * 40)
        for name, func in test_functions.items():
            duration, ops_per_sec = self.single_thread_stress(name, func)
            results[f"{name}_single"] = {"duration": duration, "ops_per_sec": ops_per_sec}
        
        # Multi-threaded stress test
        print(f"\n🔸 Multi-Threaded Stress Test ({self.cpu_count} threads)")
        print("-" * 40)
        for name, func in test_functions.items():
            duration, ops_per_sec = self.multi_thread_stress(name, func)
            results[f"{name}_multi"] = {"duration": duration, "ops_per_sec": ops_per_sec}
        
        # Memory pressure test
        print("\n🔸 Memory Pressure Test")
        print("-" * 40)
        for name, func in test_functions.items():
            duration, ops_per_sec = self.memory_pressure_test(name, func)
            results[f"{name}_memory"] = {"duration": duration, "ops_per_sec": ops_per_sec}
        
        self._print_stress_summary(results)
        return results
    
    def _rusty_stress_func(self, iteration: int, large: bool = False) -> str:
        """RustyTags stress test function."""
        if large:
            # Generate large complex structure
            return rt.Html(
                rt.Title(f"Stress Test Page {iteration}"),
                rt.Div(
                    rt.Header(
                        rt.H1(f"Stress Test {iteration}"),
                        rt.Nav(*[rt.A(f"Link {i}", href=f"/page/{i}") for i in range(20)]),
                        class_="header"
                    ),
                    rt.Main(
                        *[rt.Section(
                            rt.H2(f"Section {i}"),
                            rt.P(f"Content for section {i} in iteration {iteration}"),
                            rt.Ul(*[rt.Li(f"Item {j}") for j in range(10)]),
                            class_=f"section-{i}"
                        ) for i in range(10)],
                        class_="main-content"
                    ),
                    rt.Footer(f"Footer {iteration}", class_="footer"),
                    class_="page-container"
                ),
                lang="en"
            ).render()
        else:
            # Simple structure for basic stress testing
            return rt.Div(
                rt.H1(f"Title {iteration}"),
                rt.P(f"Content {iteration}", class_="content"),
                rt.Ul(*[rt.Li(f"Item {i}") for i in range(5)]),
                class_=f"container-{iteration}"
            ).render()
    
    def _air_stress_func(self, iteration: int, large: bool = False) -> str:
        """Air stress test function."""
        if large:
            return AirHtml(
                Title(f"Stress Test Page {iteration}"),
                Div(
                    Header(
                        H1(f"Stress Test {iteration}"),
                        Nav(*[A(f"Link {i}", href=f"/page/{i}") for i in range(20)]),
                        cls="header"
                    ),
                    Main(
                        *[Section(
                            H2(f"Section {i}"),
                            P(f"Content for section {i} in iteration {iteration}"),
                            Ul(*[Li(f"Item {j}") for j in range(10)]),
                            cls=f"section-{i}"
                        ) for i in range(10)],
                        cls="main-content"
                    ),
                    Footer(f"Footer {iteration}", cls="footer"),
                    cls="page-container"
                ),
                lang="en"
            ).render()
        else:
            return Div(
                H1(f"Title {iteration}"),
                P(f"Content {iteration}", cls="content"),
                Ul(*[Li(f"Item {i}") for i in range(5)]),
                cls=f"container-{iteration}"
            ).render()
    
    def _jinja_stress_func(self, iteration: int, large: bool = False) -> str:
        """Jinja2 stress test function."""
        if large:
            template = jinja2.Template('''
<!doctype html><html lang="en">
<head><title>Stress Test Page {{ iteration }}</title></head>
<body>
<div class="page-container">
    <header class="header">
        <h1>Stress Test {{ iteration }}</h1>
        <nav>
        {% for i in range(20) %}
            <a href="/page/{{ i }}">Link {{ i }}</a>
        {% endfor %}
        </nav>
    </header>
    <main class="main-content">
    {% for i in range(10) %}
        <section class="section-{{ i }}">
            <h2>Section {{ i }}</h2>
            <p>Content for section {{ i }} in iteration {{ iteration }}</p>
            <ul>
            {% for j in range(10) %}
                <li>Item {{ j }}</li>
            {% endfor %}
            </ul>
        </section>
    {% endfor %}
    </main>
    <footer class="footer">Footer {{ iteration }}</footer>
</div>
</body>
</html>
            '''.strip())
            return template.render(iteration=iteration)
        else:
            template = jinja2.Template('''
<div class="container-{{ iteration }}">
    <h1>Title {{ iteration }}</h1>
    <p class="content">Content {{ iteration }}</p>
    <ul>
    {% for i in range(5) %}
        <li>Item {{ i }}</li>
    {% endfor %}
    </ul>
</div>
            '''.strip())
            return template.render(iteration=iteration)
    
    def _mako_stress_func(self, iteration: int, large: bool = False) -> str:
        """Mako stress test function."""
        if large:
            template = MakoTemplate('''
<!doctype html><html lang="en">
<head><title>Stress Test Page ${iteration}</title></head>
<body>
<div class="page-container">
    <header class="header">
        <h1>Stress Test ${iteration}</h1>
        <nav>
        % for i in range(20):
            <a href="/page/${i}">Link ${i}</a>
        % endfor
        </nav>
    </header>
    <main class="main-content">
    % for i in range(10):
        <section class="section-${i}">
            <h2>Section ${i}</h2>
            <p>Content for section ${i} in iteration ${iteration}</p>
            <ul>
            % for j in range(10):
                <li>Item ${j}</li>
            % endfor
            </ul>
        </section>
    % endfor
    </main>
    <footer class="footer">Footer ${iteration}</footer>
</div>
</body>
</html>
            '''.strip())
            return template.render(iteration=iteration)
        else:
            template = MakoTemplate('''
<div class="container-${iteration}">
    <h1>Title ${iteration}</h1>
    <p class="content">Content ${iteration}</p>
    <ul>
    % for i in range(5):
        <li>Item ${i}</li>
    % endfor
    </ul>
</div>
            '''.strip())
            return template.render(iteration=iteration)
    
    def _print_stress_summary(self, results):
        """Print stress test summary."""
        print("\n🏆 STRESS TEST SUMMARY")
        print("=" * 60)
        
        categories = ["single", "multi", "memory"]
        libraries = ["RustyTags", "Air", "Jinja2", "Mako"]
        
        for category in categories:
            print(f"\n📊 {category.title()} Thread Performance:")
            print("-" * 40)
            
            category_results = []
            for lib in libraries:
                key = f"{lib}_{category}"
                if key in results:
                    category_results.append((lib, results[key]["ops_per_sec"]))
            
            # Sort by performance
            category_results.sort(key=lambda x: x[1], reverse=True)
            
            for i, (lib, ops_per_sec) in enumerate(category_results, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                print(f"{medal} {lib:<12} {ops_per_sec:>10,.0f} ops/sec")
        
        print("\n🔥 Overall Assessment:")
        
        # Count wins for each library
        wins = {lib: 0 for lib in libraries}
        for category in categories:
            category_results = [(lib, results[f"{lib}_{category}"]["ops_per_sec"]) 
                              for lib in libraries if f"{lib}_{category}" in results]
            if category_results:
                winner = max(category_results, key=lambda x: x[1])[0]
                wins[winner] += 1
        
        winner = max(wins.items(), key=lambda x: x[1])
        print(f"🏆 Overall Winner: {winner[0]} ({winner[1]}/{len(categories)} categories)")
        
        for lib, win_count in sorted(wins.items(), key=lambda x: x[1], reverse=True):
            print(f"   {lib}: {win_count}/{len(categories)} wins")

def main():
    """Run stress tests."""
    print("🔥 High-Volume Stress Testing Suite")
    print("Testing template engines under extreme load conditions")
    print(f"System: {multiprocessing.cpu_count()} CPU cores available")
    
    stress_tester = StressTest()
    results = stress_tester.run_all_stress_tests()
    
    print("\n💪 Stress Test Insights:")
    print("• Single-threaded: Raw per-core performance")
    print("• Multi-threaded: Scalability and thread safety")
    print("• Memory pressure: Efficiency under memory constraints")
    print("• RustyTags optimizations: Object pooling, SIMD, caching")

if __name__ == "__main__":
    main()