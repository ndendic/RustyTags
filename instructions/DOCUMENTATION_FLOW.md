# Documentation Flow for RustyTags Components

## Overview

The RustyTags documentation app uses a modular structure where each component has its own documentation page file. This keeps the main app.py clean and makes it easy to add new component documentation.

## File Structure

```
lab/docs/
├── app.py              # Main FastAPI app (home page + event handlers only)
├── pages/
│   ├── __init__.py     # Registers all page routes
│   ├── base.py         # Shared utilities and configuration
│   ├── codeblock.py    # CodeBlock component documentation
│   ├── tabs.py         # Tabs component documentation
│   ├── accordion.py    # Accordion component documentation
│   └── [new_component].py  # Future component pages
```

## Creating New Component Documentation

### Step 1: Create the Component Page File

Create a new file: `lab/docs/pages/[component_name].py`

```python
"""[ComponentName] component documentation page"""

from .base import *

# Define example functions that return component instances
def example_1():
    """Basic usage example"""
    return ComponentName(
        # Basic component configuration
        "Hello World",
        cls="example-class"
    )

def example_2():
    """Advanced usage example"""
    return ComponentName(
        "Advanced Example",
        variant="primary",
        size="large",
        cls="custom-styling"
    )

def get_routes(app: FastAPI):
    """Register routes for [ComponentName] documentation"""
    
    @app.get("/xtras/[component-name]")
    @page(title="[ComponentName] Component Documentation", wrap_in=HTMLResponse)
    def component_name_docs():
        return Main(
            H1("[ComponentName] Component"),
            P("Brief description of what the component does."),
            
            Section("Component Purpose",
                P("This component solves:"),
                Ul(
                    Li("🏗️ Problem 1"),
                    Li("♿️ Problem 2"),
                    Li("⚡ Problem 3"),
                ),
            ),
            
            Section("Basic Usage Demo",
                P("Try the component below:"),
                ComponentShowcase(example_1),  # 🆕 Uses ComponentShowcase!
            ),
            
            Section("Advanced Usage",
                P("More complex example:"),
                ComponentShowcase(example_2),  # 🆕 Multiple showcases!
            ),
            
            Section("API Reference",
                CodeBlock("""
def ComponentName(
    # Parameters with descriptions
) -> rt.HtmlString""", code_cls="language-python")
            ),
            
            BackLink(),
            
            signals=Signals(message=""),
        )
```

### Step 2: Register the New Page

Update `lab/docs/pages/__init__.py`:

```python
from . import codeblock, tabs, accordion, [new_component]

def register_all_routes(app):
    """Register all component documentation routes with the app"""
    codeblock.get_routes(app)
    tabs.get_routes(app)
    accordion.get_routes(app)
    [new_component].get_routes(app)  # Add this line
```

### Step 3: Add Link to Home Page

Update `lab/docs/app.py` home page to include the new component:

```python
Li(A("[ComponentName] Component", href="/xtras/[component-name]", cls="color-blue-6 text-decoration-underline")),
```

## The ComponentShowcase System

### How ComponentShowcase Works

`ComponentShowcase` is a powerful utility in `pages/base.py` that automatically creates tabbed demos:

```python
def ComponentShowcase(component: Callable):
    return Tabs(
        TabsList(
            TabsTrigger("Preview", id="tab1"),
            TabsTrigger("Code", id="tab2"),
        ),
        TabsContent(component(), id="tab1"),  # Live component
        TabsContent(CodeBlock(get_code(component)), id="tab2"),  # Auto-extracted code
        default_tab="tab1",
    )
```

### Key Benefits

✅ **Always Accurate** - Code is extracted directly from the function, no manual sync needed  
✅ **Live Demos** - Users see the actual component in action  
✅ **DRY Principle** - No duplication between demo and code example  
✅ **Interactive** - Users can switch between preview and code  
✅ **Consistent UI** - All component showcases have the same tabbed interface  

### Best Practices for Example Functions

1. **Name examples descriptively**: `example_basic()`, `example_advanced()`, `example_with_variants()`
2. **Keep functions focused**: One clear use case per function
3. **Add docstrings**: Brief description of what the example demonstrates
4. **Use realistic data**: Show practical, real-world usage
5. **Progressive complexity**: Start simple, then show advanced features

### Example Function Patterns

```python
# ✅ Good: Clear, focused, realistic
def example_basic():
    """Simple accordion with FAQ content"""
    return Accordion(
        AccordionItem("What is RustyTags?", P("A high-performance HTML library...")),
        AccordionItem("How does it work?", P("It combines Rust performance...")),
        cls="border-1 border-radius-2"
    )

# ✅ Good: Shows advanced feature (name grouping)
def example_single_open():
    """Accordion with single-open behavior using name attribute"""
    return Accordion(
        AccordionItem("Section 1", P("Content 1"), name="demo"),
        AccordionItem("Section 2", P("Content 2"), name="demo"),
        AccordionItem("Section 3", P("Content 3"), name="demo")
    )

# ❌ Avoid: Too complex, unclear purpose
def example_everything():
    return Accordion(
        AccordionItem("Test", Div(Span("Complex"), Button("Nested")), open=True, name="x"),
        # ... lots more complex stuff
    )
```

## Documentation Standards

### Required Sections

Every component documentation page should include:

1. **Component Purpose** - What problems does it solve?
2. **Basic Usage Demo** - Using `ComponentShowcase(example_function)`
3. **API Reference** - Function signature and parameters

### Recommended Sections

4. **Advanced Usage** - Additional `ComponentShowcase` examples for complex features
5. **Architecture Notes** - For components with interesting design decisions (like Accordion's native HTML approach)

### Optional Sections

Based on component complexity:

- **Architecture Principles** (for simplified components like Accordion)
- **Advanced Usage** (for components with multiple modes)
- **Comparison** (if replacing a more complex approach)
- **Accessibility Features** (if notable)

### Writing Guidelines

- **Start with the component's value proposition** - what problem does it solve?
- **Use ComponentShowcase for all demos** - provides live preview + auto-synced code
- **Create focused example functions** - one clear use case per function
- **Show progressive complexity** - start simple, then demonstrate advanced features
- **Explain architectural decisions** - the "why" behind design choices matters
- **Use realistic, practical examples** - avoid contrived demos

## Testing New Documentation

Before committing new component documentation:

1. **Check imports work correctly** - Verify all components import properly
2. **Test example functions** - Ensure each example function returns valid component
3. **Verify ComponentShowcase integration** - Check both Preview and Code tabs work
4. **Validate route responds** - Test the documentation page loads
5. **Check code extraction** - Ensure `get_code()` produces clean, readable code
6. **Test navigation** - Verify back links and home page links work

## ComponentShowcase Implementation Details

### How Code Extraction Works

The `get_code()` function in `base.py` uses Python's `inspect` module:

```python
def get_code(component: Callable):
    code = ""
    for line in inspect.getsource(component).split("\n"):
        if not line.strip().startswith("def"):  # Skip function definition
            code += line[4:] + "\n"  # Remove 4-space indentation
    code = code.replace("return ", "")  # Remove return statement
    return code
```

### Troubleshooting ComponentShowcase

**Problem**: Code tab shows messy/incorrect code  
**Solution**: Ensure example functions use consistent 4-space indentation and simple return statements

**Problem**: Example function throws error  
**Solution**: Test each example function individually: `example_1()` should return valid component

**Problem**: Preview tab is empty  
**Solution**: Check that example function returns a component, not None or a string

**Problem**: Import errors in example functions  
**Solution**: Ensure all components are imported in `base.py` or the page file

### Example Function Requirements

1. **Must return a component instance** (not a string or None)
2. **Use 4-space indentation consistently** 
3. **Keep simple structure** - avoid complex nested logic
4. **Import dependencies** - ensure all components are available
5. **Test independently** - function should work when called directly

## Benefits of This Structure

✅ **Maintainable** - Each component has its own file  
✅ **Scalable** - Easy to add new components  
✅ **Consistent** - Shared base utilities ensure uniformity  
✅ **Clean** - Main app.py stays focused  
✅ **Testable** - Each page can be tested independently  
✅ **Always Accurate** - ComponentShowcase eliminates code/demo sync issues

## Architecture Alignment

This documentation structure follows our core principles:

- **Native HTML First** - Document native solutions prominently
- **Focus on Anatomical Patterns** - Show complex DOM coordination
- **Accessibility by Default** - Highlight built-in accessibility features
- **Open Props Integration** - Demonstrate semantic design tokens
- **Less is More** - Simple, clear examples over complex configurations

---

## 🤖 AI Agent Quick Reference

### ComponentShowcase Checklist

When creating component documentation:

✅ **Define example functions at top of file**  
```python
def example_basic():
    return ComponentName("Hello", cls="example")
```

✅ **Use ComponentShowcase for all demos**  
```python
Section("Demo", ComponentShowcase(example_basic))
```

✅ **Test example functions independently**  
```python
# This should work without errors:
print(example_basic())
```

✅ **Keep example functions simple and focused**  
- One clear use case per function
- Realistic, practical examples
- Consistent 4-space indentation
- No complex logic or loops

✅ **Register the new page in `pages/__init__.py`**  
✅ **Add link to home page in `app.py`**  

### Template for New Component Page

```python
"""[ComponentName] component documentation page"""

from .base import *

# Example functions first
def example_basic():
    """Basic usage"""
    return ComponentName(
        "Example content",
        cls="demo-class"
    )

def example_advanced():
    """Advanced features"""
    return ComponentName(
        "Advanced example",
        variant="primary",
        size="large"
    )

def get_routes(app: FastAPI):
    """Register routes"""
    
    @app.get("/xtras/component-name")
    @page(title="ComponentName Documentation", wrap_in=HTMLResponse)
    def component_docs():
        return Main(
            H1("ComponentName Component"),
            P("Brief description..."),
            
            Section("Basic Usage",
                P("Description..."),
                ComponentShowcase(example_basic),  # 🐈 Key pattern!
            ),
            
            Section("Advanced Usage", 
                P("Description..."),
                ComponentShowcase(example_advanced),
            ),
            
            Section("API Reference",
                CodeBlock("""
def ComponentName(
    # Parameters...
) -> rt.HtmlString""", code_cls="language-python")
            ),
            
            BackLink(),
            signals=Signals(message=""),
        )
```

### Common Patterns

**Multiple Examples**: Use descriptive names  
`example_basic()`, `example_with_variants()`, `example_advanced()`

**Component Variants**: Show different configurations  
```python
def example_variants():
    return Div(
        ComponentName("Primary", variant="primary"),
        ComponentName("Secondary", variant="secondary"),
        style="display: flex; gap: 1rem;"
    )
```

**Architecture Notes**: For components with interesting design decisions  
```python
Section("Design Philosophy",
    P("This component uses native HTML because..."),
    Ul(
        Li("🏗️ Reason 1"),
        Li("♿️ Reason 2"),
    )
)
```
