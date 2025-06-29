#!/usr/bin/env python3
"""
Direct performance comparison: RustyTags vs Air vs pure Python string building
"""

import time
import statistics
import rusty_tags as rt
from air.tags import Div as AirDiv, H1 as AirH1, P as AirP, Ul as AirUl, Li as AirLi

def benchmark_function(name, func, iterations=10000, warmup=1000):
    """Benchmark a function with warmup and multiple runs."""
    print(f"\n🧪 Testing {name}")
    
    # Warmup
    for _ in range(warmup):
        func()
    
    # Actual benchmark
    times = []
    for _ in range(10):  # 10 test runs
        start = time.perf_counter()
        for _ in range(iterations):
            result = func()
            len(result)  # Force evaluation
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = statistics.mean(times)
    ops_per_sec = iterations / avg_time
    
    print(f"  ⏱️  {avg_time:.4f}s for {iterations:,} operations")
    print(f"  🚀 {ops_per_sec:,.0f} ops/sec")
    print(f"  📊 {avg_time*1000000/iterations:.2f}μs per operation")
    
    return ops_per_sec

def test_simple_tags():
    """Test simple tag generation."""
    print("=" * 60)
    print("🔍 SIMPLE TAG GENERATION")
    print("=" * 60)
    
    results = {}
    
    # RustyTags (immediate rendering)
    def rusty_simple():
        return rt.Div("Hello World", class_="test")
    
    # Air (deferred rendering)
    def air_simple():
        return AirDiv("Hello World", cls="test").render()
    
    # Pure Python string building
    def python_simple():
        return '<div class="test">Hello World</div>'
    
    results['RustyTags'] = benchmark_function("RustyTags", rusty_simple)
    results['Air'] = benchmark_function("Air", air_simple)
    results['Pure Python'] = benchmark_function("Pure Python", python_simple)
    
    print(f"\n📊 Simple Tag Results:")
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for i, (name, ops) in enumerate(sorted_results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"  {medal} {name}: {ops:,.0f} ops/sec")
    
    return results

def test_nested_tags():
    """Test nested tag generation."""
    print("\n" + "=" * 60)
    print("🔍 NESTED TAG GENERATION") 
    print("=" * 60)
    
    results = {}
    
    # RustyTags
    def rusty_nested():
        return rt.Div(
            rt.H1("Title"),
            rt.P("Content", class_="text"),
            class_="container"
        )
    
    # Air
    def air_nested():
        return AirDiv(
            AirH1("Title"),
            AirP("Content", cls="text"),
            cls="container"
        ).render()
    
    # Pure Python
    def python_nested():
        return '<div class="container"><h1>Title</h1><p class="text">Content</p></div>'
    
    results['RustyTags'] = benchmark_function("RustyTags", rusty_nested)
    results['Air'] = benchmark_function("Air", air_nested)
    results['Pure Python'] = benchmark_function("Pure Python", python_nested)
    
    print(f"\n📊 Nested Tag Results:")
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for i, (name, ops) in enumerate(sorted_results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"  {medal} {name}: {ops:,.0f} ops/sec")
    
    return results

def test_list_generation():
    """Test dynamic list generation."""
    print("\n" + "=" * 60)
    print("🔍 DYNAMIC LIST GENERATION (25 items)")
    print("=" * 60)
    
    results = {}
    
    items = [f"Item {i}" for i in range(25)]
    
    # RustyTags
    def rusty_list():
        return rt.Ul(
            *[rt.Li(item, class_=f"item-{i}") for i, item in enumerate(items)],
            class_="item-list"
        )
    
    # Air  
    def air_list():
        return AirUl(
            *[AirLi(item, cls=f"item-{i}") for i, item in enumerate(items)],
            cls="item-list"
        ).render()
    
    # Pure Python
    def python_list():
        items_html = ''.join(f'<li class="item-{i}">{item}</li>' for i, item in enumerate(items))
        return f'<ul class="item-list">{items_html}</ul>'
    
    results['RustyTags'] = benchmark_function("RustyTags", rusty_list, iterations=5000)
    results['Air'] = benchmark_function("Air", air_list, iterations=5000)
    results['Pure Python'] = benchmark_function("Pure Python", python_list, iterations=5000)
    
    print(f"\n📊 List Generation Results:")
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for i, (name, ops) in enumerate(sorted_results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"  {medal} {name}: {ops:,.0f} ops/sec")
    
    return results

def test_attribute_handling():
    """Test attribute handling performance."""
    print("\n" + "=" * 60)
    print("🔍 ATTRIBUTE HANDLING")
    print("=" * 60)
    
    results = {}
    
    attrs = {"class": "container", "id": "main", "data-test": "value"}
    
    # RustyTags with dict explosion
    def rusty_attrs():
        return rt.Div("Content", attrs, style="color: red")
    
    # Air with **kwargs
    def air_attrs():
        return AirDiv("Content", **attrs, style="color: red").render()
    
    # Pure Python
    def python_attrs():
        all_attrs = {**attrs, "style": "color: red"}
        attr_str = ' '.join(f'{k}="{v}"' for k, v in all_attrs.items())
        return f'<div {attr_str}>Content</div>'
    
    results['RustyTags'] = benchmark_function("RustyTags", rusty_attrs)
    results['Air'] = benchmark_function("Air", air_attrs)
    results['Pure Python'] = benchmark_function("Pure Python", python_attrs)
    
    print(f"\n📊 Attribute Handling Results:")
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for i, (name, ops) in enumerate(sorted_results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"  {medal} {name}: {ops:,.0f} ops/sec")
    
    return results

def main():
    print("🚀" * 30)
    print("🔬 DIRECT PERFORMANCE COMPARISON")
    print("🚀" * 30)
    print("Testing RustyTags immediate rendering vs Air vs Pure Python")
    
    simple_results = test_simple_tags()
    nested_results = test_nested_tags()
    list_results = test_list_generation()
    attr_results = test_attribute_handling()
    
    print("\n" + "🏆" * 30)
    print("📊 OVERALL SUMMARY")
    print("🏆" * 30)
    
    all_categories = [
        ("Simple Tags", simple_results),
        ("Nested Tags", nested_results), 
        ("List Generation", list_results),
        ("Attribute Handling", attr_results)
    ]
    
    # Count wins
    wins = {"RustyTags": 0, "Air": 0, "Pure Python": 0}
    
    for category, results in all_categories:
        winner = max(results.items(), key=lambda x: x[1])
        wins[winner[0]] += 1
        print(f"\n{category} Winner: {winner[0]} ({winner[1]:,.0f} ops/sec)")
    
    print(f"\n🎯 Final Standings:")
    for engine, win_count in sorted(wins.items(), key=lambda x: x[1], reverse=True):
        print(f"  {engine}: {win_count}/4 wins")

if __name__ == "__main__":
    main()