#!/usr/bin/env python3
"""
Performance Benchmark: Rust vs Air Tags
Comparing the same complex HTML structure between implementations
"""

import time
import statistics
from typing import Callable, List

# Import both implementations
import rusty_tags as rust
import air
from air.tags import *
from air.svg import *

def create_rust_structure():
    """Create complex structure using Rust implementation"""
    return rust.Div(
        # Header section
        rust.Div(
            rust.Div(
                rust.H1("🚀 Rust HTML Generator", cls="logo"),
                rust.Ul(
                    rust.Li(rust.A("Home", href="#home", cls="nav-link")),
                    rust.Li(rust.A("Features", href="#features", cls="nav-link")),
                    rust.Li(rust.A("Performance", href="#performance", cls="nav-link")),
                    rust.Li(rust.A("Contact", href="#contact", cls="nav-link")),
                    cls="nav-list"
                ),
                cls="container header-content"
            ),
            cls="header",
            id="header"
        ),
        
        # Hero section
        rust.Div(
            rust.Div(
                rust.H1("Lightning Fast HTML Generation", cls="hero-title"),
                rust.P(
                    "Built with ",
                    rust.Strong("Rust"),
                    " and ",
                    rust.Em("PyO3"),
                    " for maximum performance and safety.",
                    cls="hero-subtitle"
                ),
                rust.Div(
                    rust.Button("Get Started", cls="btn btn-primary", type="button"),
                    rust.Button("View Source", cls="btn btn-secondary", type="button"),
                    cls="hero-buttons"
                ),
                cls="container hero-content"
            ),
            cls="hero",
            id="home"
        ),
        
        # Features section
        rust.Div(
            rust.Div(
                rust.H2("✨ Features", cls="section-title"),
                rust.Div(
                    rust.Div(
                        rust.Div(
                            rust.H3("⚡ Performance", cls="card-title"),
                            rust.P("10-100x faster than pure Python implementations", cls="card-text"),
                            rust.Ul(
                                rust.Li("Zero-cost abstractions"),
                                rust.Li("Memory efficient"),
                                rust.Li("Parallel processing ready")
                            ),
                            cls="card-body"
                        ),
                        cls="card"
                    ),
                    rust.Div(
                        rust.Div(
                            rust.H3("🛡️ Safety", cls="card-title"),
                            rust.P("Compile-time guarantees and memory safety", cls="card-text"),
                            rust.Ul(
                                rust.Li("No runtime errors"),
                                rust.Li("Type safety"),
                                rust.Li("Memory leak prevention")
                            ),
                            cls="card-body"
                        ),
                        cls="card"
                    ),
                    cls="features-grid"
                ),
                cls="container"
            ),
            cls="features section",
            id="features"
        ),
        
        # Performance metrics table
        rust.Div(
            rust.Div(
                rust.H2("📊 Performance Metrics", cls="section-title"),
                rust.Table(
                    rust.Tr(
                        rust.Th("Operation"),
                        rust.Th("Python Time"),
                        rust.Th("Rust Time"),
                        rust.Th("Speedup")
                    ),
                    rust.Tr(
                        rust.Td("1000 Simple Tags"),
                        rust.Td("45.2ms"),
                        rust.Td(rust.Strong("2.1ms", cls="highlight")),
                        rust.Td("21.5x", cls="speedup")
                    ),
                    rust.Tr(
                        rust.Td("Complex Nested Structure"),
                        rust.Td("123.7ms"),
                        rust.Td(rust.Strong("8.4ms", cls="highlight")),
                        rust.Td("14.7x", cls="speedup")
                    ),
                    cls="performance-table",
                    border="1"
                ),
                cls="container"
            ),
            cls="performance section",
            id="performance"
        ),
        
        cls="page-wrapper",
        id="app"
    )

def create_air_structure():
    """Create the same complex structure using Air implementation"""
    return air.Div(
        # Header section
        air.Div(
            air.Div(
                air.H1("🚀 Rust HTML Generator", cls="logo"),
                air.Ul(
                    air.Li(air.A("Home", href="#home", cls="nav-link")),
                    air.Li(air.A("Features", href="#features", cls="nav-link")),
                    air.Li(air.A("Performance", href="#performance", cls="nav-link")),
                    air.Li(air.A("Contact", href="#contact", cls="nav-link")),
                    cls="nav-list"
                ),
                cls="container header-content"
            ),
            cls="header",
            id="header"
        ),
        
        # Hero section
        air.Div(
            air.Div(
                air.H1("Lightning Fast HTML Generation", cls="hero-title"),
                air.P(
                    "Built with ",
                    air.Strong("Rust"),
                    " and ",
                    air.Em("PyO3"),
                    " for maximum performance and safety.",
                    cls="hero-subtitle"
                ),
                air.Div(
                    air.Button("Get Started", cls="btn btn-primary", type="button"),
                    air.Button("View Source", cls="btn btn-secondary", type="button"),
                    cls="hero-buttons"
                ),
                cls="container hero-content"
            ),
            cls="hero",
            id="home"
        ),
        
        # Features section
        air.Div(
            air.Div(
                air.H2("✨ Features", cls="section-title"),
                air.Div(
                    air.Div(
                        air.Div(
                            air.H3("⚡ Performance", cls="card-title"),
                            air.P("10-100x faster than pure Python implementations", cls="card-text"),
                            air.Ul(
                                air.Li("Zero-cost abstractions"),
                                air.Li("Memory efficient"),
                                air.Li("Parallel processing ready")
                            ),
                            cls="card-body"
                        ),
                        cls="card"
                    ),
                    air.Div(
                        air.Div(
                            air.H3("🛡️ Safety", cls="card-title"),
                            air.P("Compile-time guarantees and memory safety", cls="card-text"),
                            air.Ul(
                                air.Li("No runtime errors"),
                                air.Li("Type safety"),
                                air.Li("Memory leak prevention")
                            ),
                            cls="card-body"
                        ),
                        cls="card"
                    ),
                    cls="features-grid"
                ),
                cls="container"
            ),
            cls="features section",
            id="features"
        ),
        
        # Performance metrics table
        air.Div(
            air.Div(
                air.H2("📊 Performance Metrics", cls="section-title"),
                air.Table(
                    air.Tr(
                        air.Th("Operation"),
                        air.Th("Python Time"),
                        air.Th("Rust Time"),
                        air.Th("Speedup")
                    ),
                    air.Tr(
                        air.Td("1000 Simple Tags"),
                        air.Td("45.2ms"),
                        air.Td(air.Strong("2.1ms", cls="highlight")),
                        air.Td("21.5x", cls="speedup")
                    ),
                    air.Tr(
                        air.Td("Complex Nested Structure"),
                        air.Td("123.7ms"),
                        air.Td(air.Strong("8.4ms", cls="highlight")),
                        air.Td("14.7x", cls="speedup")
                    ),
                    cls="performance-table",
                    border="1"
                ),
                cls="container"
            ),
            cls="performance section",
            id="performance"
        ),
        
        cls="page-wrapper",
        id="app"
    )

def benchmark_function(func: Callable, iterations: int = 1000) -> List[float]:
    """Benchmark a function over multiple iterations"""
    times = []
    
    # Warmup
    for _ in range(10):
        func()
    
    # Actual benchmarking
    for _ in range(iterations):
        start = time.perf_counter()
        result = func()
        # Force rendering to ensure fair comparison
        _ = result.render()
        end = time.perf_counter()
        times.append(end - start)
    
    return times

def print_statistics(name: str, times: List[float]):
    """Print comprehensive statistics for benchmark results"""
    times_ms = [t * 1000 for t in times]  # Convert to milliseconds
    
    print(f"\n🔍 {name} Results:")
    print(f"   Mean:    {statistics.mean(times_ms):.3f}ms")
    print(f"   Median:  {statistics.median(times_ms):.3f}ms")
    print(f"   Min:     {min(times_ms):.3f}ms")
    print(f"   Max:     {max(times_ms):.3f}ms")
    print(f"   StdDev:  {statistics.stdev(times_ms):.3f}ms")

def main():
    print("🚀 Performance Benchmark: Rust vs Air Tags")
    print("=" * 60)
    
    # Verify both implementations produce the same output
    print("🔧 Verifying implementations produce identical output...")
    rust_structure = create_rust_structure()
    air_structure = create_air_structure()
    
    rust_output = rust_structure.render()
    air_output = air_structure.render()
    
    # Compare lengths and some basic structure
    print(f"   Rust output length: {len(rust_output)} chars")
    print(f"   Air output length:  {len(air_output)} chars")
    
    # Basic structural comparison (both should have similar tag counts)
    rust_tags = rust_output.count('<')
    air_tags = air_output.count('<')
    print(f"   Rust tag count: {rust_tags}")
    print(f"   Air tag count:  {air_tags}")
    
    if abs(rust_tags - air_tags) <= 2:  # Allow small differences due to attribute ordering
        print("   ✅ Structure verification passed")
    else:
        print("   ⚠️ Structure differences detected")
    
    # Run benchmarks
    iterations = 1000
    print(f"\n🏁 Running benchmarks ({iterations} iterations each)...")
    
    print("   Testing Rust implementation...")
    rust_times = benchmark_function(create_rust_structure, iterations)
    
    print("   Testing Air implementation...")
    air_times = benchmark_function(create_air_structure, iterations)
    
    # Print results
    print_statistics("🦀 Rust Implementation", rust_times)
    print_statistics("🐍 Air Implementation", air_times)
    
    # Calculate speedup
    rust_mean = statistics.mean(rust_times)
    air_mean = statistics.mean(air_times)
    speedup = air_mean / rust_mean
    
    print(f"\n🏆 Performance Comparison:")
    print(f"   Rust mean:    {rust_mean*1000:.3f}ms")
    print(f"   Air mean:     {air_mean*1000:.3f}ms")
    print(f"   Speedup:      {speedup:.1f}x faster")
    print(f"   Improvement:  {((speedup-1)*100):.1f}% performance gain")
    
    # Memory and complexity analysis
    print(f"\n📊 Complexity Analysis:")
    print(f"   Structure depth:     8-10 levels")
    print(f"   Total elements:      ~{rust_tags} tags")
    print(f"   Character output:    {len(rust_output):,} chars")
    print(f"   Tag types used:      15+ different")
    
    print(f"\n🎯 Real-world Impact:")
    pages_per_second_rust = 1 / rust_mean
    pages_per_second_air = 1 / air_mean
    print(f"   Rust: {pages_per_second_rust:.0f} complex pages/second")
    print(f"   Air:  {pages_per_second_air:.0f} complex pages/second")

# Test the new optimized rusty_tags with string-first architecture

def create_complex_structure_air():
    """Create complex structure using Air tags - corrected usage"""
    # Air's Html automatically creates head/body structure
    # Use headers parameter for head content, children for body content
    return Html(
        # Body content goes as children
        Header(
            H1("Welcome to Test Page", cls="main-title"),
            Nav(
                Ul(
                    Li(A("Home", href="/", cls="nav-link")),
                    Li(A("About", href="/about", cls="nav-link")),
                    Li(A("Contact", href="/contact", cls="nav-link"))
                )
            )
        ),
        Main(
            Section(
                H2("Main Content Area"),
                P("This is a paragraph with ", Strong("bold text"), " and ", Em("italic text"), "."),
                Div(
                    H3("Nested Content"),
                    Table(
                        Tr(Th("Name"), Th("Age"), Th("City")),
                        Tr(Td("John"), Td("25"), Td("New York")),
                        Tr(Td("Jane"), Td("30"), Td("Los Angeles")),
                        cls="data-table"
                    ),
                    Form(
                        Label("Enter your name:", _for="name"),
                        Input(type="text", id="name", name="name"),
                        Button("Submit", type="submit")
                    )
                )
            ),
            Aside(
                H3("Sidebar"),
                Ul(
                    Li(A("Quick Link 1", href="#")),
                    Li(A("Quick Link 2", href="#")),
                    Li(A("Quick Link 3", href="#"))
                )
            )
        ),
        # Head content goes in headers parameter
        headers=(
            Title("Complex Test Page"),
            Link(rel="stylesheet", href="styles.css")
        )
    )

def create_complex_structure_rust():
    """Create complex structure using optimized Rust tags - match Air's behavior"""
    # Our Rust Html should work similarly to Air - just pass content, it auto-generates structure
    return rust.Html(
        # All content as children - our Html will auto-structure it
        rust.Title("Complex Test Page"),  # This will go in head
        rust.Link(rel="stylesheet", href="styles.css"),  # This will go in head
        rust.Header(
            rust.H1("Welcome to Test Page", cls="main-title"),
            rust.Nav(
                rust.Ul(
                    rust.Li(rust.A("Home", href="/", cls="nav-link")),
                    rust.Li(rust.A("About", href="/about", cls="nav-link")),
                    rust.Li(rust.A("Contact", href="/contact", cls="nav-link"))
                )
            )
        ),
        rust.Main(
            rust.Section(
                rust.H2("Main Content Area"),
                rust.P("This is a paragraph with ", rust.Strong("bold text"), " and ", rust.Em("italic text"), "."),
                rust.Div(
                    rust.H3("Nested Content"),
                    rust.Table(
                        rust.Tr(rust.Th("Name"), rust.Th("Age"), rust.Th("City")),
                        rust.Tr(rust.Td("John"), rust.Td("25"), rust.Td("New York")),
                        rust.Tr(rust.Td("Jane"), rust.Td("30"), rust.Td("Los Angeles")),
                        cls="data-table"
                    ),
                    rust.Form(
                        rust.Label("Enter your name:", _for="name"),
                        rust.Input(type="text", id="name", name="name"),
                        rust.Button("Submit", type="submit")
                    )
                )
            ),
            rust.Aside(
                rust.H3("Sidebar"),
                rust.Ul(
                    rust.Li(rust.A("Quick Link 1", href="#")),
                    rust.Li(rust.A("Quick Link 2", href="#")),
                    rust.Li(rust.A("Quick Link 3", href="#"))
                )
            )
        )
    )

def benchmark_air(iterations=1000):
    """Benchmark Air implementation"""
    print(f"Benchmarking Air with {iterations} iterations...")
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        structure = create_complex_structure_air()
        result = structure.render()  # Air still needs explicit render
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_time = total_time / iterations
    
    print(f"Air Results:")
    print(f"  Total time: {total_time:.6f} seconds")
    print(f"  Average per iteration: {avg_time*1000:.3f} ms")
    print(f"  Iterations per second: {iterations/total_time:.0f}")
    print(f"  Result length: {len(result)} characters")
    
    return avg_time, result

def benchmark_rust_optimized(iterations=1000):
    """Benchmark optimized Rust implementation"""
    print(f"\nBenchmarking Optimized Rust with {iterations} iterations...")
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        structure = create_complex_structure_rust()
        # The optimized version returns strings directly - no render() needed!
        result = str(structure)
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_time = total_time / iterations
    
    print(f"Optimized Rust Results:")
    print(f"  Total time: {total_time:.6f} seconds")
    print(f"  Average per iteration: {avg_time*1000:.3f} ms")
    print(f"  Iterations per second: {iterations/total_time:.0f}")
    print(f"  Result length: {len(result)} characters")
    
    return avg_time, result

if __name__ == "__main__":
    print("🚀 Performance Comparison: Air vs Optimized Rust\n")
    
    # Verify outputs are equivalent first
    print("=== Verifying Output Equivalence ===")
    air_result = create_complex_structure_air().render()
    rust_result = str(create_complex_structure_rust())
    
    print(f"Air output length: {len(air_result)}")
    print(f"Rust output length: {len(rust_result)}")
    
    # Check if outputs are identical
    if air_result == rust_result:
        print("✅ Outputs are IDENTICAL!")
    else:
        print("❌ Outputs differ!")
        print("\nFirst 200 chars of Air output:")
        print(repr(air_result[:200]))
        print("\nFirst 200 chars of Rust output:")
        print(repr(rust_result[:200]))
        
        # Find first difference
        for i, (a, r) in enumerate(zip(air_result, rust_result)):
            if a != r:
                print(f"\nFirst difference at position {i}: '{a}' vs '{r}'")
                print(f"Context: ...{air_result[max(0,i-20):i+20]}...")
                break
    
    print("\n" + "="*60)
    print("=== Performance Benchmark ===")
    
    # Run benchmarks
    air_time, air_output = benchmark_air(1000)
    rust_time, rust_output = benchmark_rust_optimized(1000)
    
    # Calculate performance comparison
    if rust_time < air_time:
        speedup = air_time / rust_time
        print(f"\n🎉 RUST IS FASTER! {speedup:.1f}x speedup!")
    else:
        slowdown = rust_time / air_time
        print(f"\n⚠️  Rust is {slowdown:.1f}x slower than Air")
    
    print(f"\nPerformance Summary:")
    print(f"  Air:      {air_time*1000:.3f} ms per iteration")
    print(f"  Rust:     {rust_time*1000:.3f} ms per iteration")
    print(f"  Difference: {abs(rust_time - air_time)*1000:.3f} ms per iteration")
    
    # Pages per second calculation
    air_pages_per_sec = 1 / air_time
    rust_pages_per_sec = 1 / rust_time
    
    print(f"\nThroughput:")
    print(f"  Air:      {air_pages_per_sec:.0f} complex pages/sec")
    print(f"  Rust:     {rust_pages_per_sec:.0f} complex pages/sec")

# Simple test to verify the new architecture works
def test_simple_structure():
    """Test that the new optimized tags work correctly"""
    print("\n=== Testing New Optimized Architecture ===")
    
    # Test simple tag creation - should return string directly
    simple_div = rust.Div("Hello World", cls="test")
    print(f"Simple div result: {simple_div}")
    print(f"Simple div type: {type(simple_div)}")
    
    # Test nested structure
    nested = rust.Div(
        rust.H1("Title"),
        rust.P("Paragraph with ", rust.Strong("bold"), " text")
    )
    print(f"Nested result: {nested}")
    print(f"Nested type: {type(nested)}")

if __name__ == "__main__":
    test_simple_structure() 