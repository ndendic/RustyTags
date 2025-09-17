# RustyTags Web Components Architecture Plan

## 🎯 **Vision**
Create a **headless UI component library** for Python web development built on RustyTags' high-performance foundation with native Datastar reactivity. Components focus on **complex anatomical patterns** and **behavioral interactions** that are hard to implement correctly, while leaving simple HTML elements to be used directly via RustyTags base tags.

## 🧠 **Key Implementation Lessons Learned**

### **Critical Pattern: Function Closures for Signal Sharing**
**✅ DO**: Use function closures that return functions for clean composition:
```python
def TabsTrigger(*children, id: str, **attrs):
    def create_trigger(signal: str, default_tab: str):
        return rt.Button(
            *children, 
            on_click=f"${signal} = '{id}'",
            **attrs
        )
    return create_trigger

def Tabs(*children, default_tab: str, **attrs):
    signal = f"tabs_{next(_tab_ids)}"
    processed_children = [
        child(signal, default_tab) if callable(child) else child
        for child in children
    ]
    return rt.Div(*processed_children, signals=Signals(**{signal: default_tab}))
```

**❌ DON'T**: Create monolithic components with complex internal structure and signal management.

### **Critical Pattern: Simple String-Based State**
**✅ DO**: Use simple string identifiers for state management:
```python
# Simple and clear
signals=Signals(active_tab="tab1")
on_click=f"$active_tab = 'tab2'"
show=f"$active_tab === 'tab1'"
```

**❌ DON'T**: Use complex nested dictionaries or numeric indices that are hard to work with.

### **Critical Pattern: Datastar Reactive Attributes**
**✅ DO**: Use `data-attr-*` for dynamic HTML attributes:
```python
**{
    "aria-selected": "true" if is_active else f"${signal} === '{id}'",
    "data-attr-aria-selected": f"${signal} === '{id}'",  # Updates dynamically
    "data-attr-tabindex": f"${signal} === '{id}' ? '0' : '-1'"
}
```

**❌ DON'T**: Try to manage complex conditional attributes without Datastar's reactive system.

### **Critical Pattern: Component Composition Philosophy**
**✅ DO**: Build components that solve **anatomical complexity**:
- Multiple coordinated DOM elements
- Complex ARIA relationships
- State synchronization between parts
- Focus management and keyboard navigation

**❌ DON'T**: Wrap simple HTML elements just for styling - use `rt.Button()`, `rt.Input()` directly.

### **Critical Pattern: Native HTML First**
**✅ DO**: Use native HTML features when they exist:
```python
# Native HTML accordion using details/summary + name attribute
def AccordionItem(trigger, *content, name=None, **attrs):
    return rt.Details(
        rt.Summary(trigger, cls="accordion-trigger"),
        rt.Div(*content, cls="accordion-content"),
        name=name,  # Native accordion behavior!
        **attrs
    )
```

**❌ DON'T**: Reinvent native functionality with complex JavaScript/signal management:
```python
# Avoid: 190+ lines of complex state management for something HTML does natively
def ComplexAccordion(*children, type="single", signal=""):
    # Complex lambda closures, signal coordination, custom animations...
    pass
```

### **Critical Pattern: Minimal API Surface**
**✅ DO**: Keep component APIs focused and composable:
```python
# Clean, focused API
Tabs(
    TabsList(
        TabsTrigger("Tab 1", id="tab1"),
        TabsTrigger("Tab 2", id="tab2"),
    ),
    TabsContent(P("Content 1"), id="tab1"),
    TabsContent(P("Content 2"), id="tab2"),
    default_tab="tab1"
)
```

**❌ DON'T**: Create overly complex APIs with too many configuration options.

### **Critical Pattern: CSS Requirements**
**✅ DO**: Accept that some components need minimal CSS for functionality:
- Positioning for popovers/dropdowns
- Show/hide states
- Focus management
- Transitions and animations

**❌ DON'T**: Try to make everything work with zero CSS when positioning/layout is required.

---

## 🏗️ **Core Architecture Decisions**

### **Component Philosophy: Anatomical Patterns Over Element Wrapping**

**What We Build:**
- **Complex anatomical patterns** requiring multiple coordinated DOM elements
- **Behavioral interactions** with non-trivial state management
- **Accessibility-heavy patterns** that developers often get wrong
- **Form composition patterns** that require proper element relationships

**What We Don't Build:**
- Simple element wrappers (use `rt.Button`, `rt.Input`, etc. directly)
- Pure styling components (use CSS/Tailwind/Open Props)
- Basic layout elements (use native HTML + CSS)

**Decision Framework** (ALL must be true):
1. **Anatomical complexity**: Requires multiple coordinated DOM elements
2. **Behavioral complexity**: Non-trivial interaction patterns or state management
3. **Accessibility burden**: Significant ARIA requirements or focus management
4. **Developer pain point**: Commonly implemented incorrectly or tediously

### **Component Examples**
```python
# ❌ Don't build - use base tags directly
rt.Button("Click me", cls="my-styles", on_click="$clicked = true")
rt.Input(type="email", placeholder="Email", cls="my-input-styles")

# ✅ Build - complex anatomical patterns
Dropdown(
    trigger=rt.Button("Options"),
    items=[DropdownItem("Edit"), DropdownItem("Delete")]
)

FormField(
    label="Email",
    input=rt.Input(type="email"),
    error_message="$emailError"
)
```

## 🧬 **Anatomical Pattern Philosophy**

### **What Makes a Good Component Candidate**

A component should solve **structural complexity** and **behavioral coordination** problems:

**✅ Good candidates:**
- **Multiple DOM elements** that need to work together
- **Complex ARIA relationships** between elements  
- **State coordination** between multiple interactive parts
- **Positioning logic** for popups, dropdowns, tooltips
- **Focus management** and keyboard navigation patterns
- **Event coordination** (click-outside, ESC handling, etc.)

**❌ Poor candidates:**
- Single DOM elements with just styling differences
- Pure layout/presentation components
- Simple event handlers that can be added directly

### **Component Composition Strategy**

**Accept base elements as parameters:**
```python
# Let users provide their own styled elements
FormField(
    label="Email Address",
    input=rt.Input(type="email", cls="my-custom-input-styles"),
    help_text="We'll never share this"
)

Dropdown(
    trigger=rt.Button("My Styled Button", cls="custom-btn"),
    items=[...]
)
```

**Focus on the structural relationships:**
```python
# The component handles the complex parts:
# - Label/input associations
# - Error state management  
# - ARIA attributes
# - Validation state coordination
def FormField(label, input, error_message=None, help_text=None, **attrs):
    field_id = generate_component_id("form-field")
    input_id = f"{field_id}-input"
    error_id = f"{field_id}-error"
    help_id = f"{field_id}-help"
    
    # Add proper IDs and ARIA to the user's input element
    enhanced_input = input.copy_with(
        id=input_id,
        **{"aria-describedby": f"{help_id} {error_id}" if error_message else help_id}
    )
    
    return rt.Div(
        rt.Label(label, for_=input_id),
        enhanced_input,
        rt.Div(help_text, id=help_id, cls="help-text") if help_text else "",
        rt.Div(error_message, id=error_id, cls="error-text", role="alert") if error_message else "",
        **attrs
    )
```

## 🔄 **State Management Strategy**

### **Signal Visibility System**
1. **Component defaults**: Each component defines which signals are private (`_signal`) by default
2. **Global override**: `expose_signals=True` makes all default-private signals public  
3. **Manual control**: Users can always override individual signal names in `signals={}` parameter

### **Component ID and Signal Naming**
- **User-provided ID**: Use exactly as provided
  ```python
  Button("Save", id="save-btn")
  # → id="save-btn", signals={"_save-btn_clicked": False}
  ```
- **Auto-generated ID**: `{component_type}-{short_hash}` format
  ```python
  Button("Click me")  
  # → id="button-a1b2c3", signals={"_button-a1b2c3_clicked": False}
  ```
- **Signal naming**: Always include ID in signal names for page-level uniqueness
- **Dashes preserved**: Keep dashes in signal names (e.g., `$save-btn_clicked` is valid in Datastar)

## 🎨 **Theming Architecture**

### **Multi-Level Styling Support**
All components support multiple styling approaches with clear precedence:

#### **1. Direct Styling (Highest Precedence)**
```python
Button("Save", cls="my-btn", style={"color": "red"})
# Always overrides everything else
```

#### **2. Sub-element Specific Styling**
```python
Form("My form", 
     label_cls="text-sm font-bold", 
     label_style={"margin-bottom": "4px"},
     input_cls="border rounded px-2")
# For components with multiple styleable elements
```

#### **3. Variant-based Styling (Lowest Precedence)**
```python
# Component definition level
ButtonStyles = AttrDict({
    "primary": {
        "cls": "bg-blue-500 text-white",
        "hover_cls": "bg-blue-600"
    },
    "secondary": {
        "cls": "bg-gray-200 text-gray-800", 
        "style": {"border": "1px solid gray"}
    }
})

# Usage
Button("Save", variant="primary")  # Uses ButtonStyles.primary
Button("Cancel", variant="secondary", cls="my-override")  # cls overrides variant.cls
```

#### **4. Multi-Element Variant Structure**
```python
FormStyles = AttrDict({
    "default": {
        "cls": "form-container",
        "label": {"cls": "form-label", "style": {"font-weight": "bold"}},
        "input": {"cls": "form-input"},
        "error": {"cls": "text-red-500 text-sm"}
    }
})
```

### **Component Styling Boundaries**
**Principle**: A component only provides styling configuration for:
1. **Structural/layout elements** it creates (containers, wrappers)
2. **Tightly coupled sub-elements** it manages (button icons, form labels)  
3. **NOT independent child components** that users compose themselves

**Examples**:
- **Form component**: Only styles layout, spacing, direct labels, fieldsets
- **Button component**: Styles all internal elements (self-contained)
- **Modal component**: Styles backdrop, container, but NOT the content children

## 📋 **API Design Philosophy**

### **Flexibility Requirements**
- Support minimal usage: `Button("Click me")`
- Support basic customization through multiple approaches
- Support full customization with arbitrary args
- Smart placement and usage of `*args` and `**kwargs`
- Assume users can submit many arbitrary arguments

### **No Built-in Variants Initially**
- Components are unstyled by default
- Variants and sizes left for styling configuration
- Focus on functionality and structure, not appearance

## 🔄 **Datastar Integration**

### **Signal Management**
- State managed using Datastar signals
- Private signals by default (prefixed with `_`)
- Component-specific named signals based on component ID
- Auto-generation when ID not provided

### **Signal Exposure Control**
```python
# Default behavior
Button("Click me")  # → {"_button-a1b2c3_clicked": false}

# Expose private signals  
Button("Click me", expose_signals=True)  # → {"button-a1b2c3_clicked": false}

# Manual signal control
Button("Click me", signals={"my_click_state": False})  # → Uses exactly what user provided
```

## 📋 **Outstanding Questions**

### **Accessibility Integration** ✅
**Decision: Fully Automatic (Opinionated)**
- All accessibility features enabled by default
- Developers get WCAG compliance "for free" 
- Components automatically include appropriate ARIA attributes, keyboard navigation, focus management
- Minimal configuration needed - accessibility just works

**Examples**:
```python
Button("Save")  
# Automatically gets: role="button", tabindex="0", keyboard handlers

Modal("Settings")
# Automatically gets: role="dialog", aria-modal="true", focus trap, ESC handler

Input("email", placeholder="Email")
# Automatically gets: proper labeling associations, validation attributes
```

### **Component Priority** ✅
**Decision: Focus on Complex Anatomical Patterns and Behavioral Interactions**

**Tier 1 - Complex Anatomical Patterns (MVP):**
- `Dropdown/Select` - Trigger + positioned menu + option selection + keyboard nav + click-outside
- `Modal/Dialog` - Backdrop + content + focus trap + ESC handling + scroll lock
- `FormField` - Label + input + error + help text with proper associations and validation states
- `RadioGroup` - Multiple radio inputs with grouping, labels, and state coordination
- `Tabs` - Tab buttons + panels + ARIA relationships + keyboard navigation
- ✅ `Accordion` - **COMPLETED** - Simplified to use native HTML details/summary elements with name-based grouping

**Tier 2 - Advanced Interactive Patterns:**
- `Combobox/Autocomplete` - Input + dropdown + filtering + selection + async search + keyboard nav
- `DatePicker` - Input + calendar popup + date selection + validation + positioning
- `Toggle/Switch` - Custom styled checkbox with proper ARIA and animation states
- `CheckboxGroup` - Multiple checkboxes with group validation and state management
- `Popover` - Trigger + positioned content + click-outside + arrow placement
- `Tooltip` - Hover/focus triggers + positioned content + timing controls

**Tier 3 - Complex Composition Patterns:**
- `DataTable` - Headers + sortable columns + filtering + pagination + row selection
- `Form` - Form wrapper with validation orchestration and submission handling
- `Slider/Range` - Custom range input with multiple handles, labels, formatting
- `Pagination` - Page numbers + prev/next + jump-to with proper navigation
- `FileUpload` - Drag-drop area + progress + preview + validation

**Not Component-ized (Use Base Tags + CSS):**
- `Button`, `Input`, `Link` - Use `rt.Button()`, `rt.Input()`, `rt.A()` directly
- Cards, Grids, Containers, Spacers, Dividers - Use native HTML + CSS
- Badges, Avatars, Icons - Simple styling, no complex behavior

### **Package Structure** ✅
**Decision: RustyTags Extension Module - Single Flat Structure**

```
rusty_tags/
├── components/
│   ├── __init__.py      # Export all components
│   ├── button.py        # Button component
│   ├── input.py         # Input component  
│   ├── toggle.py        # Toggle component
│   ├── checkbox.py      # Checkbox component
│   ├── radio_group.py   # RadioGroup component
│   ├── select.py        # Select component
│   ├── textarea.py      # TextArea component
│   ├── search_input.py  # SearchInput component
│   ├── modal.py         # Modal component
│   ├── popover.py       # Popover component
│   └── ...
```

**Advantages**:
- Tight integration with RustyTags core
- Shared theming system and Datastar integration
- Single installation and import
- Simple flat structure for easy navigation
- Can reorganize later if needed

### **Framework Integration** ✅
**Decision: Component-Level Integration (Universal Approach)**

Components work identically across all frameworks - focus on simple HTML generation:

```python
# Universal usage across frameworks
from rusty_tags.components import Button, Modal, Input

# FastAPI
@app.get("/")
def home():
    return Button("Click me", on_click=DS.post("/api/action"))

# Flask  
@app.route("/")
def home():
    return str(Button("Click me", on_click=DS.post("/api/action")))

# Django
def home(request):
    return HttpResponse(Button("Click me", on_click=DS.post("/api/action")))
```

**Advantages**:
- Simple, consistent API across frameworks
- Focus on HTML generation excellence
- Can extend with framework-specific helpers later
- Reduces complexity and maintenance burden

---

## 📝 **Implementation Roadmap**

### **Phase 1: Foundation** ✅
1. ✅ Define component architecture and patterns
2. ✅ Establish styling system with variants
3. ✅ Design signal management and ID generation
4. ✅ Choose accessibility approach (fully automatic)
5. ✅ Prioritize functional components over layout
6. ✅ Set package structure (flat extension module)
7. ✅ Framework integration strategy (universal)

### **Phase 2: MVP Anatomical Patterns** (Current)
1. ✅ Create component base utilities for ID generation, signals, and styling
2. 🔄 Implement Tier 1 anatomical patterns:
   - FormField (label + input + error + help text associations)
   - Dropdown/Select (trigger + menu + options + positioning + keyboard nav)
   - Modal/Dialog (backdrop + content + focus trap + ESC + scroll lock)
   - RadioGroup (grouped radio inputs + labels + state coordination)
   - ✅ **Accordion** - **COMPLETED** using native HTML details/summary
3. ✅ **Establish documentation system** - **COMPLETED** with ComponentShowcase pattern
4. 🔄 Implement automatic accessibility for complex patterns
5. 🔄 Create comprehensive demos and tests
6. 🔄 Document pattern usage and customization

### **Key Lessons Learned**

#### **Accordion Simplification: Native HTML First**
Our accordion component taught us the critical importance of **native HTML first**:
- **Before**: 190+ lines of complex signal management, lambda closures, and custom animations
- **After**: ~100 lines using native `<details>` elements with `name` attribute for accordion behavior
- **Result**: Better accessibility, performance, and developer experience with less code

**Rule**: Always check if native HTML can solve the problem before building complex abstractions.

#### **Documentation Innovation: ComponentShowcase System**
Developed an automated documentation system that eliminates code/demo sync issues:
- **ComponentShowcase** utility automatically extracts code from example functions
- **Tabbed interface** shows live preview + auto-generated code examples
- **Always accurate** - no manual maintenance of code examples needed
- **Consistent UX** - all component demos follow the same interactive pattern

**Rule**: Use ComponentShowcase for all component demos to ensure accuracy and consistency.

**Reference**: See `instructions/DOCUMENTATION_FLOW.md` for complete implementation guide.

### **Phase 3: Advanced Interactive Patterns** (Future)
1. ⏳ Tier 2 interactive patterns (Combobox, DatePicker, Toggle, CheckboxGroup, etc.)
2. ⏳ Advanced positioning and popup management (Popover, Tooltip)
3. ⏳ Complex Datastar integration patterns for async interactions
4. ⏳ Performance optimization for complex DOM manipulations

### **Phase 4: Ecosystem** (Future)
1. ⏳ Documentation and examples
2. ⏳ Framework-specific helpers (if needed)
3. ⏳ Community themes and variants
4. ⏳ TypeScript definitions
