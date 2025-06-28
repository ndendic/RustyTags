#!/usr/bin/env python3
"""
Test immediate rendering and dict explosion functionality
"""

import rusty_tags as rt

def test_immediate_rendering():
    """Test that tags return strings immediately."""
    print("🧪 Testing Immediate Rendering")
    
    # Test simple tag
    result = rt.Div("Hello World")
    print(f"Simple tag: {result}")
    print(f"Type: {type(result)}")
    assert isinstance(result, str)
    assert result == "<div>Hello World</div>"
    
    # Test nested tags
    result = rt.Div(
        rt.H1("Title"),
        rt.P("Content"),
        class_="container"
    )
    print(f"Nested tags: {result}")
    assert isinstance(result, str)
    assert "<div class=\"container\">" in result
    assert "<h1>Title</h1>" in result
    assert "<p>Content</p>" in result
    
    print("✅ Immediate rendering works!")

def test_dict_explosion():
    """Test that dictionaries are exploded as attributes."""
    print("\n🧪 Testing Dict Explosion")
    
    # Test dict as attributes
    attrs = {"class": "test-class", "data-id": "123"}
    result = rt.Div("Content", attrs)
    print(f"Dict explosion: {result}")
    assert isinstance(result, str)
    assert 'class="test-class"' in result
    assert 'data-id="123"' in result
    
    # Test dict + kwargs (kwargs should override)
    attrs = {"class": "original", "id": "test"}
    result = rt.Div("Content", attrs, class_="overridden")
    print(f"Dict + kwargs: {result}")
    assert 'class="overridden"' in result  # kwargs override dict
    assert 'id="test"' in result  # dict attributes preserved
    
    # Test multiple children with dict
    result = rt.Div(
        rt.Span("Child 1"),
        {"class": "parent"},
        rt.Span("Child 2"),
        id="container"
    )
    print(f"Mixed children: {result}")
    assert 'class="parent"' in result
    assert 'id="container"' in result
    assert "<span>Child 1</span>" in result
    assert "<span>Child 2</span>" in result
    
    print("✅ Dict explosion works!")

def test_performance_comparison():
    """Quick performance test comparing immediate vs deferred rendering."""
    print("\n🧪 Testing Performance")
    
    import time
    
    # Test immediate rendering (current)
    start = time.perf_counter()
    for i in range(1000):
        html = rt.Div(
            rt.H1(f"Title {i}"),
            rt.P(f"Content {i}"),
            class_=f"item-{i}"
        )
        len(html)  # Force evaluation
    end = time.perf_counter()
    immediate_time = end - start
    
    print(f"Immediate rendering (1000 tags): {immediate_time:.4f}s")
    print(f"Performance: {1000/immediate_time:.0f} tags/sec")
    
    print("✅ Performance test complete!")

def test_complex_nesting():
    """Test complex nested structures."""
    print("\n🧪 Testing Complex Nesting")
    
    page = rt.Html(
        rt.Head(rt.Title("Test Page")),
        rt.Body(
            rt.Header(
                rt.H1("Welcome"),
                rt.Nav(
                    rt.Ul(
                        *[rt.Li(rt.A(f"Link {i}", href=f"/page/{i}")) for i in range(3)]
                    )
                )
            ),
            rt.Main(
                rt.Section(
                    rt.H2("Content"),
                    rt.P("This is a test of complex nesting."),
                    class_="content"
                )
            ),
            rt.Footer("© 2024 Test"),
            class_="main-body"
        ),
        lang="en"
    )
    
    print(f"Complex page length: {len(page)} characters")
    print(f"Type: {type(page)}")
    
    # Verify structure
    assert isinstance(page, str)
    assert page.startswith("<!doctype html><html")
    assert "lang=\"en\"" in page
    assert "<title>Test Page</title>" in page
    assert "class=\"main-body\"" in page
    
    print("✅ Complex nesting works!")

if __name__ == "__main__":
    test_immediate_rendering()
    test_dict_explosion() 
    test_performance_comparison()
    test_complex_nesting()
    
    print("\n🎉 All tests passed! Immediate rendering with dict explosion is working!")