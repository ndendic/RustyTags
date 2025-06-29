#!/usr/bin/env python3
"""
Test if batch operations can overcome boundary overhead
"""

import time
import rusty_tags as rt

def test_individual_vs_batch():
    """Compare individual tag creation vs batch operations."""
    
    print("🧪 Testing Individual vs Batch Operations")
    
    # Individual operations (current approach)
    def individual_operations():
        results = []
        for i in range(100):
            result = rt.Div(f"Content {i}", class_=f"item-{i}")
            results.append(result)
        return ''.join(results)
    
    # Pure Python equivalent
    def python_equivalent():
        results = []
        for i in range(100):
            result = f'<div class="item-{i}">Content {i}</div>'
            results.append(result)
        return ''.join(results)
    
    # Test individual operations
    start = time.perf_counter()
    for _ in range(100):
        individual_operations()
    individual_time = time.perf_counter() - start
    
    # Test Python equivalent
    start = time.perf_counter()
    for _ in range(100):
        python_equivalent()
    python_time = time.perf_counter() - start
    
    print(f"Individual RustyTags: {individual_time:.4f}s")
    print(f"Pure Python: {python_time:.4f}s")
    print(f"Python is {individual_time/python_time:.1f}x faster")
    
    # Test complex single operation
    def complex_single_operation():
        return rt.Html(
            rt.Head(rt.Title("Test")),
            rt.Body(
                rt.Header(rt.H1("Title")),
                rt.Main(
                    *[rt.Section(
                        rt.H2(f"Section {i}"),
                        rt.P(f"Content for section {i}"),
                        rt.Ul(*[rt.Li(f"Item {j}") for j in range(5)])
                    ) for i in range(10)]
                ),
                rt.Footer("Footer")
            )
        )
    
    def python_complex():
        sections = []
        for i in range(10):
            items = ''.join(f'<li>Item {j}</li>' for j in range(5))
            section = f'<section><h2>Section {i}</h2><p>Content for section {i}</p><ul>{items}</ul></section>'
            sections.append(section)
        
        return f'''<html>
<head><title>Test</title></head>
<body>
<header><h1>Title</h1></header>
<main>{''.join(sections)}</main>
<footer>Footer</footer>
</body>
</html>'''
    
    # Test complex operations
    start = time.perf_counter()
    for _ in range(100):
        complex_single_operation()
    complex_rust_time = time.perf_counter() - start
    
    start = time.perf_counter()
    for _ in range(100):
        python_complex()
    complex_python_time = time.perf_counter() - start
    
    print(f"\nComplex RustyTags: {complex_rust_time:.4f}s")
    print(f"Complex Python: {complex_python_time:.4f}s")
    
    if complex_rust_time < complex_python_time:
        print(f"🎉 RustyTags is {complex_python_time/complex_rust_time:.1f}x faster for complex operations!")
    else:
        print(f"😅 Python is still {complex_rust_time/complex_python_time:.1f}x faster")

if __name__ == "__main__":
    test_individual_vs_batch()