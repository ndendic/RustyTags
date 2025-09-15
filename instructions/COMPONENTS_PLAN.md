# RustyTags Web Components Architecture Plan

## 🎯 **Vision**
Create a **headless UI component library** for Python web development built on RustyTags' high-performance foundation with native Datastar reactivity. Components should be unstyled but provide core skeleton for interactive web components with excellent developer experience.

## 🏗️ **Core Architecture Decisions**

### **Component Structure Philosophy**
- **Primary**: Flat structure wherever possible for performance
- **Exception**: Use hierarchical structure only when justified by our criteria
- **Decision Framework** (in priority order):
  1. **Customization complexity** (primary) - Keep APIs simple, "less is more"
  2. **Reusability** (secondary) - Sub-components useful standalone
  3. **State interdependence** (tertiary) - Complex shared state needs

### **Component Structure Examples**
```python
# Simple components (clearly flat)
Button(), Input(), Badge()

# Medium complexity (decide per component)  
Dropdown(), Tabs(), Accordion()

# Complex components (might benefit from hierarchy)
DataTable(), Form(), Modal()
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
**Decision: Prioritize Functional/Behavioral Components Over Styling-Only Components**

**Tier 1 - Core Interactive Elements (MVP):**
- `Button` - Click interactions, loading states, disabled states
- `Input` - Text, email, password with validation states
- `Toggle` - Boolean switches with state management
- `Checkbox` - Multi-select with intermediate states
- `RadioGroup` - Single-select groups with state coordination
- `Select` - Dropdown selection with search/filtering
- `TextArea` - Multi-line text input with auto-resize
- `SearchInput` - Search with debouncing, clear actions

**Tier 2 - Advanced Interactions:**
- `Modal` - Focus trap, backdrop, ESC handling
- `Popover` - Positioning, click-outside, arrow placement
- `Tooltip` - Hover/focus triggers, positioning
- `Dropdown` - Menu positioning, keyboard navigation
- `DatePicker` - Calendar interaction, date validation
- `Slider` - Range selection, step controls
- `Tabs` - Tab switching, keyboard navigation
- `Accordion` - Expand/collapse with smooth transitions

**Tier 3 - Complex Components:**
- `Form` - Validation orchestration, submission handling
- `DataTable` - Sorting, filtering, pagination
- `Autocomplete` - Async search, result navigation
- `FileUpload` - Drag-drop, progress, preview

**Deprioritized (Pure Layout/Styling):**
- Cards, Grids, Containers, Spacers, Dividers
- These can be easily created with basic HTML tags + CSS

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

### **Phase 2: MVP Components** (Next)
1. 🔄 Create component base class/utilities
2. 🔄 Implement Tier 1 components:
   - Button (click interactions, loading states)
   - Input (validation states, types)
   - Toggle (boolean switches)
   - Checkbox (multi-select, intermediate states)
3. 🔄 Establish styling patterns and variant system
4. 🔄 Implement automatic accessibility features
5. 🔄 Create comprehensive tests

### **Phase 3: Advanced Components** (Future)
1. ⏳ Tier 2 components (Modal, Popover, Dropdown, etc.)
2. ⏳ Complex positioning and interaction patterns
3. ⏳ Advanced Datastar integration patterns
4. ⏳ Performance optimization and caching

### **Phase 4: Ecosystem** (Future)
1. ⏳ Documentation and examples
2. ⏳ Framework-specific helpers (if needed)
3. ⏳ Community themes and variants
4. ⏳ TypeScript definitions
