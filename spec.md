# HTML Parsing Feature Specification

## Idea

**What:** Add optional HTML parsing to convert rendered `HtmlString` into inspectable/modifiable tree structures.

**Why:** Enable post-creation validation, sanitization, and context-dependent attribute modification without rebuilding core rendering architecture.

**DX - How it should be used:**
```python
# Fast path - normal rendering (unchanged)
html = Div(Input(name="email"), Button("Submit"))

# Slow path - when inspection/modification needed
doc = html.parse()  # Returns HtmlElement tree

# Pure Python traversal
for child in doc.children:
    if child.tag == "input":
        child.attributes["required"] = "true"

# Serialize back
modified_html = doc.to_html()  # Returns HtmlString
```

**Key principle:** Parsing is opt-in. Users only pay parsing costs when explicitly needed.

## Technical Implementation Guidelines

**Phase 1: Core Parsing (Option A)**

1. Add `scraper` dependency to `Cargo.toml`
2. Create `HtmlElement` PyClass with flat structure:
   - `tag: String` - element tag name
   - `attributes: HashMap<String, String>` - mutable attribute dict
   - `children: Vec<PyObject>` - mixed text strings and HtmlElement objects
   - `is_text: bool` - flag to distinguish text nodes from elements

3. Implement `HtmlString.parse()` method:
   - Use `scraper::Html::parse_fragment()` for fragments
   - Recursively convert scraper nodes to `HtmlElement` tree
   - Handle text nodes as plain Python strings in children list
   - Return root `HtmlElement`

4. Implement `HtmlElement.to_html()` method:
   - Recursively serialize tree back to HTML string
   - Return new `HtmlString` instance

**Phase 2: Hybrid Selectors (Option C - Future)**
- Add `select(selector: str)` method to `HtmlElement`
- Expose scraper's CSS selector engine
- Return `Vec<Py<HtmlElement>>` for matches

**Memory considerations:** Parsed trees are separate from rendered strings. No impact on normal rendering performance.

## Testing Guidelines

**Unit tests (Rust side):**
- Parse simple single elements: `<div id="test">content</div>`
- Parse nested structures with multiple children
- Parse mixed text and element children
- Preserve all attributes during parse roundtrip
- Handle self-closing tags: `<br/>`, `<img/>`
- Text node handling in children lists

**Integration tests (Python side):**
```python
def test_parse_and_modify():
    html = Form(Input(name="email"), Button("Submit"))
    doc = html.parse()
    
    # Find and modify
    for child in doc.children:
        if child.tag == "input":
            child.attributes["required"] = "true"
    
    result = doc.to_html()
    assert 'required="true"' in result.content

def test_nested_traversal():
    html = Div(Form(Input(type="text")))
    doc = html.parse()
    
    # Deep traversal
    form = doc.children[0]
    inp = form.children[0]
    assert inp.tag == "input"
    assert inp.attributes["type"] == "text"
```

**Performance benchmarks:**
- Measure parse overhead vs normal rendering
- Document when to use parsing vs construction-time validation
- Target: Parsing should be <2x slower than initial rendering
```
