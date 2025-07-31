use pyo3::prelude::*;
use pyo3::types::PyDict;
use ahash::AHashMap as HashMap;
use smallvec::{SmallVec, smallvec};
use dashmap::DashMap;
use once_cell::sync::Lazy;
use std::borrow::Cow;
use std::cell::RefCell;
use std::sync::atomic::{AtomicUsize, Ordering};
use bumpalo::Bump;

// =============================================================================
// MEMORY MANAGEMENT & OBJECT POOLING
// =============================================================================

// Thread-local string pool for efficient memory reuse
thread_local! {
    static STRING_POOL: RefCell<Vec<String>> = RefCell::new(Vec::with_capacity(32));
    static ARENA_POOL: RefCell<Vec<Bump>> = RefCell::new(Vec::with_capacity(8));
}

// Global stats for monitoring pool effectiveness
static POOL_HITS: AtomicUsize = AtomicUsize::new(0);
static POOL_MISSES: AtomicUsize = AtomicUsize::new(0);

#[inline(always)]
fn get_pooled_string(capacity: usize) -> String {
    STRING_POOL.with(|pool| {
        if let Some(mut s) = pool.borrow_mut().pop() {
            s.clear();
            if s.capacity() < capacity {
                s.reserve(capacity - s.capacity());
            }
            POOL_HITS.fetch_add(1, Ordering::Relaxed);
            s
        } else {
            POOL_MISSES.fetch_add(1, Ordering::Relaxed);
            String::with_capacity(capacity)
        }
    })
}

#[inline(always)]
fn return_to_pool(s: String) {
    // Only pool reasonably sized strings to prevent memory hoarding
    if s.capacity() <= 2048 && s.capacity() >= 16 {
        STRING_POOL.with(|pool| {
            let mut pool = pool.borrow_mut();
            if pool.len() < 64 {
                pool.push(s);
            }
        });
    }
}

// =============================================================================
// LOCK-FREE CACHING SYSTEM
// =============================================================================

// Thread-local caches for hot paths
thread_local! {
    static LOCAL_ATTR_CACHE: RefCell<HashMap<String, Cow<'static, str>>> = 
        RefCell::new(HashMap::with_capacity(128));
    static LOCAL_TAG_CACHE: RefCell<HashMap<String, Cow<'static, str>>> = 
        RefCell::new(HashMap::with_capacity(64));
}

// Global lock-free caches for fallback
static GLOBAL_ATTR_CACHE: Lazy<DashMap<String, Cow<'static, str>>> = 
    Lazy::new(|| DashMap::with_capacity(1000));
static GLOBAL_TAG_CACHE: Lazy<DashMap<String, Cow<'static, str>>> = 
    Lazy::new(|| DashMap::with_capacity(200));

// String interning for ultimate memory efficiency
static INTERNED_STRINGS: Lazy<DashMap<&'static str, &'static str>> = Lazy::new(|| {
    let map = DashMap::with_capacity(200);
    
    // Common tag names
    let tags = [
        "div", "span", "p", "a", "img", "input", "button", "form",
        "table", "tr", "td", "th", "ul", "ol", "li", "h1", "h2", 
        "h3", "h4", "h5", "h6", "head", "body", "html", "title",
        "meta", "link", "script", "style", "nav", "header", "footer",
        "main", "section", "article", "aside", "details", "summary"
    ];
    
    // Common attribute names  
    let attrs = [
        "class", "id", "type", "name", "value", "href", "src", "alt",
        "title", "for", "method", "action", "target", "rel", "media",
        "charset", "content", "property", "role", "data", "aria"
    ];
    
    for &tag in &tags {
        map.insert(tag, tag);
    }
    for &attr in &attrs {
        map.insert(attr, attr);
    }
    
    map
});

#[inline(always)]
fn intern_string(s: &str) -> &str {
    INTERNED_STRINGS.get(s).map(|r| *r.value()).unwrap_or(s)
}

// =============================================================================
// OPTIMIZED ATTRIBUTE AND TAG PROCESSING
// =============================================================================

// Smart attribute value conversion with type support
#[inline(always)]
fn convert_attribute_value(value_obj: &Bound<'_, pyo3::PyAny>, _py: Python) -> PyResult<String> {
    // Fast path for strings
    if let Ok(s) = value_obj.extract::<String>() {
        return Ok(s);
    }
    
    // Fast path for booleans - check first since bool can be extracted as int
    if let Ok(b) = value_obj.extract::<bool>() {
        return Ok(if b { "true".to_string() } else { "false".to_string() });
    }
    
    // Fast path for integers
    if let Ok(i) = value_obj.extract::<i64>() {
        let mut buffer = itoa::Buffer::new();
        return Ok(buffer.format(i).to_string());
    }
    
    // Fast path for floats
    if let Ok(f) = value_obj.extract::<f64>() {
        let mut buffer = ryu::Buffer::new();
        return Ok(buffer.format(f).to_string());
    }
    
    // Try to convert to string using __str__
    if let Ok(str_result) = value_obj.str() {
        if let Ok(str_value) = str_result.extract::<String>() {
            return Ok(str_value);
        }
    }
    
    // Final fallback - get type name for error
    let value_type = value_obj.get_type().name()?;
    Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
        format!("Cannot convert {} to string for HTML attribute", value_type)
    ))
}

// Enhanced child processing with smart type conversion and __html__ support
#[inline(always)]
fn process_child_object(child_obj: &PyObject, py: Python) -> PyResult<String> {
    // Fast path for HtmlString - direct access to content
    if let Ok(html_string) = child_obj.extract::<PyRef<HtmlString>>(py) {
        return Ok(html_string.content.clone());
    }
    
    // Fast path for strings
    if let Ok(s) = child_obj.extract::<&str>(py) {
        return Ok(s.to_string());
    }
    
    // Fast path for booleans
    if let Ok(b) = child_obj.extract::<bool>(py) {
        return Ok(if b { "true".to_string() } else { "false".to_string() });
    }
    
    // Fast path for integers  
    if let Ok(i) = child_obj.extract::<i64>(py) {
        let mut buffer = itoa::Buffer::new();
        return Ok(buffer.format(i).to_string());
    }
    
    // Fast path for floats
    if let Ok(f) = child_obj.extract::<f64>(py) {
        let mut buffer = ryu::Buffer::new();
        return Ok(buffer.format(f).to_string());
    }
    
    let child_bound = child_obj.bind(py);
    
    // Check for __html__ method (common in web frameworks like Flask, Django)
    if let Ok(html_method) = child_bound.getattr("__html__") {
        if html_method.is_callable() {
            if let Ok(html_result) = html_method.call0() {
                if let Ok(html_str) = html_result.extract::<String>() {
                    return Ok(html_str);
                }
            }
        }
    }
    
    // Check for _repr_html_ method (Jupyter/IPython style)
    if let Ok(repr_html_method) = child_bound.getattr("_repr_html_") {
        if repr_html_method.is_callable() {
            if let Ok(html_result) = repr_html_method.call0() {
                if let Ok(html_str) = html_result.extract::<String>() {
                    return Ok(html_str);
                }
            }
        }
    }
    
    // Check for render method (common in template libraries)
    if let Ok(render_method) = child_bound.getattr("render") {
        if render_method.is_callable() {
            if let Ok(render_result) = render_method.call0() {
                if let Ok(render_str) = render_result.extract::<String>() {
                    return Ok(render_str);
                }
            }
        }
    }
    
    // Try to convert to string using __str__
    if let Ok(str_result) = child_bound.str() {
        if let Ok(str_value) = str_result.extract::<String>() {
            return Ok(str_value);
        }
    }
    
    // Final fallback - get type name for error
    let child_type = child_bound.get_type().name()?;
    Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
        format!("Cannot convert {} to string for HTML content", child_type)
    ))
}

// Fast child processing with type-specific paths and SmallVec optimization
#[inline(always)]
fn process_children_optimized(children: &[PyObject], py: Python) -> PyResult<String> {
    if children.is_empty() {
        return Ok(String::new());
    }
    
    // Fast path for small collections using stack allocation
    if children.len() <= 4 {
        let mut result = String::with_capacity(children.len() * 32);
        
        for child_obj in children {
            let child_str = process_child_object(child_obj, py)?;
            result.push_str(&child_str);
        }
        
        return Ok(result);
    }
    
    // Larger collections use arena allocation
    let estimated_capacity = children.len() * 64; // Conservative estimate
    let mut result = get_pooled_string(estimated_capacity);
    
    for child_obj in children {
        let child_str = process_child_object(child_obj, py)?;
        result.push_str(&child_str);
    }
    
    Ok(result)
}

// Cached attribute key transformation
#[inline(always)]
fn fix_k_optimized(k: &str) -> String {
    if k == "_" {
        return "_".to_string();
    }
    
    // Fast path for short strings
    if k.len() <= 16 {
        return if k.starts_with('_') {
            k[1..].replace('_', "-")
        } else {
            k.replace('_', "-")
        };
    }
    
    // Check thread-local cache first
    LOCAL_ATTR_CACHE.with(|cache| {
        let cache_ref = cache.borrow();
        if let Some(cached) = cache_ref.get(k) {
            return cached.to_string();
        }
        drop(cache_ref);
        
        // Check global cache
        if let Some(cached) = GLOBAL_ATTR_CACHE.get(k) {
            let result = cached.to_string();
            cache.borrow_mut().insert(k.to_string(), Cow::Owned(result.clone()));
            return result;
        }
        
        // Compute and cache
        let result = if k.starts_with('_') {
            k[1..].replace('_', "-")
        } else {
            k.replace('_', "-")
        };
        
        cache.borrow_mut().insert(k.to_string(), Cow::Owned(result.clone()));
        GLOBAL_ATTR_CACHE.insert(k.to_string(), Cow::Owned(result.clone()));
        result
    })
}

// Ultra-fast attribute mapping with comprehensive caching
#[inline(always)]
fn attrmap_optimized(attr: &str) -> String {
    // Handle most common cases first - these cover 90% of usage
    match attr {
        "cls" | "_class" | "htmlClass" | "klass" | "class_" => return "class".to_string(),
        "_for" | "fr" | "htmlFor" | "for_" => return "for".to_string(),
        "id" => return "id".to_string(),
        "type" | "type_" => return "type".to_string(),
        "name" => return "name".to_string(),
        "value" => return "value".to_string(),
        "href" => return "href".to_string(),
        "src" => return "src".to_string(),
        "alt" => return "alt".to_string(),
        "title" => return "title".to_string(),
        "method" => return "method".to_string(),
        "action" => return "action".to_string(),
        "target" => return "target".to_string(),
        "rel" => return "rel".to_string(),
        _ => {}
    }
    
    // Fast special character check
    if attr.contains('@') || attr.contains('.') || attr.contains('-') || 
       attr.contains('!') || attr.contains('~') || attr.contains(':') ||
       attr.contains('[') || attr.contains(']') || attr.contains('(') ||
       attr.contains(')') || attr.contains('{') || attr.contains('}') ||
       attr.contains('$') || attr.contains('%') || attr.contains('^') ||
       attr.contains('&') || attr.contains('*') || attr.contains('+') ||
       attr.contains('=') || attr.contains('|') || attr.contains('/') ||
       attr.contains('?') || attr.contains('<') || attr.contains('>') ||
       attr.contains(',') || attr.contains('`') {
        return attr.to_string();
    }
    
    fix_k_optimized(attr)
}

// Cached tag name normalization
#[inline(always)]
fn normalize_tag_name(tag_name: &str) -> String {
    // Fast path for already normalized strings
    if tag_name.len() <= 16 && tag_name.chars().all(|c| c.is_ascii_lowercase()) {
        return intern_string(tag_name).to_string();
    }
    
    LOCAL_TAG_CACHE.with(|cache| {
        let cache_ref = cache.borrow();
        if let Some(cached) = cache_ref.get(tag_name) {
            return cached.to_string();
        }
        drop(cache_ref);
        
        // Check global cache
        if let Some(cached) = GLOBAL_TAG_CACHE.get(tag_name) {
            let result = cached.to_string();
            cache.borrow_mut().insert(tag_name.to_string(), Cow::Owned(result.clone()));
            return result;
        }
        
        // Compute using lowercase
        let normalized = tag_name.to_ascii_lowercase();
        let interned = intern_string(&normalized).to_string();
        
        cache.borrow_mut().insert(tag_name.to_string(), Cow::Owned(interned.clone()));
        GLOBAL_TAG_CACHE.insert(tag_name.to_string(), Cow::Owned(interned.clone()));
        interned
    })
}

// Optimized attribute building with exact capacity calculation
#[inline(always)]
fn build_attributes_optimized(attrs: &HashMap<String, String>) -> String {
    if attrs.is_empty() {
        return String::new();
    }
    
    // Pre-calculate exact capacity needed
    let total_capacity: usize = attrs.iter()
        .map(|(k, v)| {
            let mapped_key_len = attrmap_optimized(k).len();
            mapped_key_len + v.len() + 4 // +4 for =" " and quote
        })
        .sum::<usize>() + 1; // +1 for leading space
    
    let mut result = get_pooled_string(total_capacity);
    result.push(' ');
    
    // Process attributes in a single pass
    for (k, v) in attrs {
        let mapped_key = attrmap_optimized(k);
        result.push_str(&mapped_key);
        result.push_str("=\"");
        result.push_str(v);
        result.push_str("\" ");
    }
    
    // Remove trailing space
    result.pop();
    result
}

// Core HtmlString with optimized memory layout
#[pyclass(module = "rusty_tags")]
pub struct HtmlString {
    #[pyo3(get)]
    content: String,
}

// TagBuilder for callable functionality - preserves tag structure
#[pyclass]
pub struct TagBuilder {
    tag_name: String,
    pub attrs: HashMap<String, String>,
}

#[pymethods]
impl HtmlString {
    #[new]
    #[inline(always)]
    fn py_new(content: String) -> Self {
        HtmlString { content }
    }
    
    #[inline(always)]
    fn __str__(&self) -> &str {
        &self.content
    }
    
    #[inline(always)]
    fn __repr__(&self) -> &str {
        &self.content
    }
    
    #[inline(always)]
    fn render(&self) -> &str {
        &self.content
    }
    
    #[inline(always)]
    fn _repr_html_(&self) -> &str {
        &self.content
    }
    
    #[inline(always)]
    fn __html__(&self) -> &str {
        &self.content
    }

    
    // Pickle support using __getnewargs_ex__
    #[inline(always)]
    fn __getnewargs_ex__(&self, py: Python) -> PyResult<((String,), PyObject)> {
        let args = (self.content.clone(),);
        let kwargs = pyo3::types::PyDict::new(py);
        Ok((args, kwargs.into()))
    }
}

impl HtmlString {
    #[inline(always)]
    fn new(content: String) -> Self {
        HtmlString { content }
    }
}

#[pymethods]
impl TagBuilder {
    #[new]
    #[inline(always)]
    fn new(tag_name: String) -> Self {
        TagBuilder {
            tag_name,
            attrs: HashMap::default(),
        }
    }
    
    #[inline(always)]
    #[pyo3(signature = (*children, **kwargs))]
    fn __call__(&mut self, children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<HtmlString> {
        // Merge new attributes with existing ones
        if let Some(kwargs) = kwargs {
            for (key, value) in kwargs.iter() {
                let key_str = key.extract::<String>()?;
                let value_str = convert_attribute_value(&value, py)?;
                self.attrs.insert(key_str, value_str);
            }
        }
        
        // Build the final HTML using existing optimized functions
        build_html_tag_optimized(&self.tag_name, children, self.attrs.clone(), py)
    }
    
    #[inline(always)]
    fn __str__(&self) -> PyResult<String> {
        // Return empty tag without children for inspection
        let tag_lower = normalize_tag_name(&self.tag_name);
        let attr_string = build_attributes_optimized(&self.attrs);
        
        let capacity = tag_lower.len() * 2 + attr_string.len() + 5;
        let mut result = get_pooled_string(capacity);
        
        result.push('<');
        result.push_str(&tag_lower);
        result.push_str(&attr_string);
        result.push_str("/>");
        
        Ok(result)
    }
    
    #[inline(always)]
    fn __repr__(&self) -> PyResult<String> {
        // Return empty tag without children for inspection
        self.__str__()
    }
    
    #[inline(always)]
    fn render(&self) -> PyResult<String> {
        // Return empty tag without children for inspection
        self.__str__()
    }
    
    #[inline(always)]
    fn _repr_html_(&self) -> PyResult<String> {
        // Return empty tag without children for inspection
        self.__str__()
    }
    
    #[inline(always)]
    fn __html__(&self) -> PyResult<String> {
        // Return empty tag without children for inspection
        self.__str__()
    }

}

// Optimized tag builder with minimal allocations
#[inline(always)]
fn build_html_tag_optimized(
    tag_name: &str, 
    children: Vec<PyObject>, 
    attrs: HashMap<String, String>,
    py: Python
) -> PyResult<HtmlString> {
    let tag_lower = normalize_tag_name(tag_name);
    let attr_string = build_attributes_optimized(&attrs);
    let children_string = process_children_optimized(&children, py)?;
    
    // Calculate exact capacity to avoid any reallocations
    let capacity = tag_lower.len() * 2 + attr_string.len() + children_string.len() + 5;
    let mut result = get_pooled_string(capacity);
    
    // Build HTML in a single pass with minimal function calls
    result.push('<');
    result.push_str(&tag_lower);
    result.push_str(&attr_string);
    result.push('>');
    result.push_str(&children_string);
    result.push_str("</");
    result.push_str(&tag_lower);
    result.push('>');
    
    Ok(HtmlString::new(result))
}

// Optimized macro with aggressive inlining and fast paths
macro_rules! html_tag_optimized {
    ($name:ident, $doc:expr) => {
        #[pyfunction]
        #[doc = $doc]
        #[pyo3(signature = (*children, **kwargs))]
        #[inline(always)]
        fn $name(children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<PyObject> {
            // If no children AND no attributes, return TagBuilder for chaining
            if children.is_empty() && kwargs.is_none() {
                let tag_builder = TagBuilder::new(stringify!($name).to_string());
                return Ok(Py::new(py, tag_builder)?.into());
            }
            
            // If no children but has attributes, create self-closing tag immediately
            if children.is_empty() {
                let mut attrs = HashMap::default();
                
                if let Some(kwargs) = kwargs {
                    for (key, value) in kwargs.iter() {
                        let key_str = key.extract::<String>()?;
                        let value_str = convert_attribute_value(&value, py)?;
                        attrs.insert(key_str, value_str);
                    }
                }
                
                let html_string = build_html_tag_optimized(stringify!($name), children, attrs, py)?;
                return Ok(Py::new(py, html_string)?.into());
            }
            
            // Fast path for no attributes but with children
            if kwargs.is_none() {
                let children_string = process_children_optimized(&children, py)?;
                let tag_name = normalize_tag_name(stringify!($name));
                
                let capacity = tag_name.len() * 2 + children_string.len() + 5;
                let mut result = get_pooled_string(capacity);
                
                result.push('<');
                result.push_str(&tag_name);
                result.push('>');
                result.push_str(&children_string);
                result.push_str("</");
                result.push_str(&tag_name);
                result.push('>');
                
                let html_string = HtmlString::new(result);
                return Ok(Py::new(py, html_string)?.into());
            }
            
            // Full path with attributes - use optimized HashMap
            let mut attrs = HashMap::default();
            
            if let Some(kwargs) = kwargs {
                for (key, value) in kwargs.iter() {
                    let key_str = key.extract::<String>()?;
                    let value_str = convert_attribute_value(&value, py)?;
                    attrs.insert(key_str, value_str);
                }
            }
            
            let html_string = build_html_tag_optimized(stringify!($name), children, attrs, py)?;
            Ok(Py::new(py, html_string)?.into())
        }
    };
}

// Generate optimized HTML tag functions
html_tag_optimized!(A, "Defines a hyperlink");
html_tag_optimized!(Aside, "Defines aside content");
html_tag_optimized!(B, "Defines bold text");
html_tag_optimized!(Body, "Defines the document body");
html_tag_optimized!(Br, "Defines a line break");
html_tag_optimized!(Button, "Defines a clickable button");
html_tag_optimized!(Code, "Defines computer code");
html_tag_optimized!(Div, "Defines a division or section");
html_tag_optimized!(Em, "Defines emphasized text");
html_tag_optimized!(Form, "Defines an HTML form");
html_tag_optimized!(H1, "Defines a level 1 heading");
html_tag_optimized!(H2, "Defines a level 2 heading");
html_tag_optimized!(H3, "Defines a level 3 heading");
html_tag_optimized!(H4, "Defines a level 4 heading");
html_tag_optimized!(H5, "Defines a level 5 heading");
html_tag_optimized!(H6, "Defines a level 6 heading");
html_tag_optimized!(Head, "Defines the document head");
html_tag_optimized!(Header, "Defines a page header");

// Special handling for Html tag - includes DOCTYPE and auto head/body separation like Air
#[pyfunction]
#[doc = "Defines the HTML document"]
#[pyo3(signature = (*children, **kwargs))]
#[inline(always)]
fn Html(children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<HtmlString> {
    // Handle attributes if present - use optimized HashMap
    let mut attrs = HashMap::default();
    if let Some(kwargs) = kwargs {
        for (key, value) in kwargs.iter() {
            let key_str = key.extract::<String>()?;
            let value_str = convert_attribute_value(&value, py)?;
            attrs.insert(key_str, value_str);
        }
    }
    
    // Process all children directly - no automatic separation
    let children_string = process_children_optimized(&children, py)?;
    let attr_string = build_attributes_optimized(&attrs);
    
    // Calculate capacity: DOCTYPE + html structure + children + attributes
    let capacity = 15 + 17 + attr_string.len() + children_string.len(); // "<!doctype html><html></html>"
    let mut result = get_pooled_string(capacity);
    
    // Build HTML structure with all children directly inside
    result.push_str("<!doctype html>");
    result.push_str("<html");
    result.push_str(&attr_string);
    result.push_str(">");
    result.push_str(&children_string);
    result.push_str("</html>");
    
    Ok(HtmlString::new(result))
}

html_tag_optimized!(I, "Defines italic text");
html_tag_optimized!(Img, "Defines an image");
html_tag_optimized!(Input, "Defines an input field");
html_tag_optimized!(Label, "Defines a label for a form element");
html_tag_optimized!(Li, "Defines a list item");
html_tag_optimized!(Link, "Defines a document link");
html_tag_optimized!(Main, "Defines the main content");
html_tag_optimized!(Nav, "Defines navigation links");
html_tag_optimized!(P, "Defines a paragraph");
html_tag_optimized!(Script, "Defines a client-side script");
html_tag_optimized!(Section, "Defines a section");
html_tag_optimized!(Span, "Defines an inline section");
html_tag_optimized!(Strong, "Defines strong/important text");
html_tag_optimized!(Table, "Defines a table");
html_tag_optimized!(Td, "Defines a table cell");
html_tag_optimized!(Th, "Defines a table header cell");
html_tag_optimized!(Title, "Defines the document title");
html_tag_optimized!(Tr, "Defines a table row");
html_tag_optimized!(Ul, "Defines an unordered list");
html_tag_optimized!(Ol, "Defines an ordered list");

// Phase 1: Critical High Priority HTML tags (10 tags)
html_tag_optimized!(Meta, "Defines metadata about an HTML document");
html_tag_optimized!(Hr, "Defines a thematic break/horizontal rule");
html_tag_optimized!(Iframe, "Defines an inline frame");
html_tag_optimized!(Textarea, "Defines a multiline text input control");
html_tag_optimized!(Select, "Defines a dropdown list");
html_tag_optimized!(Figure, "Defines self-contained content");
html_tag_optimized!(Figcaption, "Defines a caption for a figure element");
html_tag_optimized!(Article, "Defines independent, self-contained content");
html_tag_optimized!(Footer, "Defines a footer for a document or section");
html_tag_optimized!(Details, "Defines additional details that can be viewed or hidden");
html_tag_optimized!(Summary, "Defines a visible heading for a details element");
html_tag_optimized!(Address, "Defines contact information for the author");

// Phase 2: Table Enhancement Tags (6 tags)
html_tag_optimized!(Tbody, "Defines a table body");
html_tag_optimized!(Thead, "Defines a table header");
html_tag_optimized!(Tfoot, "Defines a table footer");
html_tag_optimized!(Caption, "Defines a table caption");
html_tag_optimized!(Col, "Defines a table column");
html_tag_optimized!(Colgroup, "Defines a group of table columns");

// SVG Tags
html_tag_optimized!(Svg, "Defines an SVG graphics container");
html_tag_optimized!(Circle, "Defines a circle in SVG");
html_tag_optimized!(Rect, "Defines a rectangle in SVG");
html_tag_optimized!(Line, "Defines a line in SVG");
html_tag_optimized!(Path, "Defines a path in SVG");
html_tag_optimized!(Polygon, "Defines a polygon in SVG");
html_tag_optimized!(Polyline, "Defines a polyline in SVG");
html_tag_optimized!(Ellipse, "Defines an ellipse in SVG");
html_tag_optimized!(Text, "Defines text in SVG");
html_tag_optimized!(G, "Defines a group in SVG");
html_tag_optimized!(Defs, "Defines reusable SVG elements");
html_tag_optimized!(Use, "Defines a reusable SVG element instance");
html_tag_optimized!(Symbol, "Defines a reusable SVG symbol");
html_tag_optimized!(Marker, "Defines a marker for SVG shapes");
html_tag_optimized!(LinearGradient, "Defines a linear gradient in SVG");
html_tag_optimized!(RadialGradient, "Defines a radial gradient in SVG");
html_tag_optimized!(Stop, "Defines a gradient stop in SVG");
html_tag_optimized!(Pattern, "Defines a pattern in SVG");
html_tag_optimized!(ClipPath, "Defines a clipping path in SVG");
html_tag_optimized!(Mask, "Defines a mask in SVG");
html_tag_optimized!(Image, "Defines an image in SVG");
html_tag_optimized!(ForeignObject, "Defines foreign content in SVG");

// All remaining HTML tags - comprehensive implementation
html_tag_optimized!(Abbr, "Defines an abbreviation");
html_tag_optimized!(Area, "Defines an area in an image map");
html_tag_optimized!(Audio, "Defines audio content");
html_tag_optimized!(Base, "Defines the base URL for all relative URLs");
html_tag_optimized!(Bdi, "Defines bidirectional text isolation");
html_tag_optimized!(Bdo, "Defines bidirectional text override");
html_tag_optimized!(Blockquote, "Defines a block quotation");
html_tag_optimized!(Canvas, "Defines a graphics canvas");
html_tag_optimized!(Cite, "Defines a citation");
html_tag_optimized!(Data, "Defines machine-readable data");
html_tag_optimized!(Datalist, "Defines a list of input options");
html_tag_optimized!(Dd, "Defines a description in a description list");
html_tag_optimized!(Del, "Defines deleted text");
html_tag_optimized!(Dfn, "Defines a definition term");
html_tag_optimized!(Dialog, "Defines a dialog box");
html_tag_optimized!(Dl, "Defines a description list");
html_tag_optimized!(Dt, "Defines a term in a description list");
html_tag_optimized!(Embed, "Defines external content");
html_tag_optimized!(Fieldset, "Defines a fieldset for form controls");
html_tag_optimized!(Hgroup, "Defines a heading group");
html_tag_optimized!(Ins, "Defines inserted text");
html_tag_optimized!(Kbd, "Defines keyboard input");
html_tag_optimized!(Legend, "Defines a caption for a fieldset");
html_tag_optimized!(Map, "Defines an image map");
html_tag_optimized!(Mark, "Defines highlighted text");
html_tag_optimized!(Menu, "Defines a menu list");
html_tag_optimized!(Meter, "Defines a scalar measurement");
html_tag_optimized!(Noscript, "Defines content for users without script support");
html_tag_optimized!(Object, "Defines an embedded object");
html_tag_optimized!(Optgroup, "Defines a group of options in a select list");
html_tag_optimized!(OptionEl, "Defines an option in a select list");
html_tag_optimized!(Picture, "Defines a picture container");
html_tag_optimized!(Pre, "Defines preformatted text");
html_tag_optimized!(Progress, "Defines progress of a task");
html_tag_optimized!(Q, "Defines a short quotation");
html_tag_optimized!(Rp, "Defines ruby parentheses");
html_tag_optimized!(Rt, "Defines ruby text");
html_tag_optimized!(Ruby, "Defines ruby annotation");
html_tag_optimized!(S, "Defines strikethrough text");
html_tag_optimized!(Samp, "Defines sample computer output");
html_tag_optimized!(Small, "Defines small text");
html_tag_optimized!(Source, "Defines media resources");
html_tag_optimized!(Style, "Defines style information");
html_tag_optimized!(Sub, "Defines subscript text");
html_tag_optimized!(Sup, "Defines superscript text");
html_tag_optimized!(Template, "Defines a template container");
html_tag_optimized!(Time, "Defines date/time information");
html_tag_optimized!(Track, "Defines media track");
html_tag_optimized!(U, "Defines underlined text");
html_tag_optimized!(Var, "Defines a variable");
html_tag_optimized!(Video, "Defines video content");
html_tag_optimized!(Wbr, "Defines a word break opportunity");

// Custom tag function for dynamic tag creation
#[pyfunction]
#[doc = "Creates a custom HTML tag with any tag name"]
#[pyo3(signature = (tag_name, *children, **kwargs))]
#[inline(always)]
fn CustomTag(tag_name: String, children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<HtmlString> {
    // Handle attributes if present - use optimized HashMap
    let mut attrs = HashMap::default();
    if let Some(kwargs) = kwargs {
        for (key, value) in kwargs.iter() {
            let key_str = key.extract::<String>()?;
            let value_str = convert_attribute_value(&value, py)?;
            attrs.insert(key_str, value_str);
        }
    }
    
    build_html_tag_optimized(&tag_name, children, attrs, py)
}

// Factory function for pickle support
#[pyfunction]
#[doc = "Internal factory function for creating HtmlString objects (used by pickle)"]
#[inline(always)]
fn create_html_string(content: String) -> HtmlString {
    HtmlString::new(content)
}



/// A Python module implemented in Rust.
#[pymodule]
fn rusty_tags(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core classes
    m.add_class::<HtmlString>()?;
    m.add_class::<TagBuilder>()?;
    
    // Optimized HTML tag functions
    m.add_function(wrap_pyfunction!(A, m)?)?;
    m.add_function(wrap_pyfunction!(Aside, m)?)?;
    m.add_function(wrap_pyfunction!(B, m)?)?;
    m.add_function(wrap_pyfunction!(Body, m)?)?;
    m.add_function(wrap_pyfunction!(Br, m)?)?;
    m.add_function(wrap_pyfunction!(Button, m)?)?;
    m.add_function(wrap_pyfunction!(Code, m)?)?;
    m.add_function(wrap_pyfunction!(Div, m)?)?;
    m.add_function(wrap_pyfunction!(Em, m)?)?;
    m.add_function(wrap_pyfunction!(Form, m)?)?;
    m.add_function(wrap_pyfunction!(H1, m)?)?;
    m.add_function(wrap_pyfunction!(H2, m)?)?;
    m.add_function(wrap_pyfunction!(H3, m)?)?;
    m.add_function(wrap_pyfunction!(H4, m)?)?;
    m.add_function(wrap_pyfunction!(H5, m)?)?;
    m.add_function(wrap_pyfunction!(H6, m)?)?;
    m.add_function(wrap_pyfunction!(Head, m)?)?;
    m.add_function(wrap_pyfunction!(Header, m)?)?;
    m.add_function(wrap_pyfunction!(Html, m)?)?;
    m.add_function(wrap_pyfunction!(I, m)?)?;
    m.add_function(wrap_pyfunction!(Img, m)?)?;
    m.add_function(wrap_pyfunction!(Input, m)?)?;
    m.add_function(wrap_pyfunction!(Label, m)?)?;
    m.add_function(wrap_pyfunction!(Li, m)?)?;
    m.add_function(wrap_pyfunction!(Link, m)?)?;
    m.add_function(wrap_pyfunction!(Main, m)?)?;
    m.add_function(wrap_pyfunction!(Nav, m)?)?;
    m.add_function(wrap_pyfunction!(P, m)?)?;
    m.add_function(wrap_pyfunction!(Script, m)?)?;
    m.add_function(wrap_pyfunction!(Section, m)?)?;
    m.add_function(wrap_pyfunction!(Span, m)?)?;
    m.add_function(wrap_pyfunction!(Strong, m)?)?;
    m.add_function(wrap_pyfunction!(Table, m)?)?;
    m.add_function(wrap_pyfunction!(Td, m)?)?;
    m.add_function(wrap_pyfunction!(Th, m)?)?;
    m.add_function(wrap_pyfunction!(Title, m)?)?;
    m.add_function(wrap_pyfunction!(Tr, m)?)?;
    m.add_function(wrap_pyfunction!(Ul, m)?)?;
    m.add_function(wrap_pyfunction!(Ol, m)?)?;
    
    // Phase 1: Critical High Priority HTML tags
    m.add_function(wrap_pyfunction!(Meta, m)?)?;
    m.add_function(wrap_pyfunction!(Hr, m)?)?;
    m.add_function(wrap_pyfunction!(Iframe, m)?)?;
    m.add_function(wrap_pyfunction!(Textarea, m)?)?;
    m.add_function(wrap_pyfunction!(Select, m)?)?;
    m.add_function(wrap_pyfunction!(Figure, m)?)?;
    m.add_function(wrap_pyfunction!(Figcaption, m)?)?;
    m.add_function(wrap_pyfunction!(Article, m)?)?;
    m.add_function(wrap_pyfunction!(Footer, m)?)?;
    m.add_function(wrap_pyfunction!(Details, m)?)?;
    m.add_function(wrap_pyfunction!(Summary, m)?)?;
    m.add_function(wrap_pyfunction!(Address, m)?)?;
    
    // Phase 2: Table Enhancement Tags
    m.add_function(wrap_pyfunction!(Tbody, m)?)?;
    m.add_function(wrap_pyfunction!(Thead, m)?)?;
    m.add_function(wrap_pyfunction!(Tfoot, m)?)?;
    m.add_function(wrap_pyfunction!(Caption, m)?)?;
    m.add_function(wrap_pyfunction!(Col, m)?)?;
    m.add_function(wrap_pyfunction!(Colgroup, m)?)?;
    
    // SVG Tags
    m.add_function(wrap_pyfunction!(Svg, m)?)?;
    m.add_function(wrap_pyfunction!(Circle, m)?)?;
    m.add_function(wrap_pyfunction!(Rect, m)?)?;
    m.add_function(wrap_pyfunction!(Line, m)?)?;
    m.add_function(wrap_pyfunction!(Path, m)?)?;
    m.add_function(wrap_pyfunction!(Polygon, m)?)?;
    m.add_function(wrap_pyfunction!(Polyline, m)?)?;
    m.add_function(wrap_pyfunction!(Ellipse, m)?)?;
    m.add_function(wrap_pyfunction!(Text, m)?)?;
    m.add_function(wrap_pyfunction!(G, m)?)?;
    m.add_function(wrap_pyfunction!(Defs, m)?)?;
    m.add_function(wrap_pyfunction!(Use, m)?)?;
    m.add_function(wrap_pyfunction!(Symbol, m)?)?;
    m.add_function(wrap_pyfunction!(Marker, m)?)?;
    m.add_function(wrap_pyfunction!(LinearGradient, m)?)?;
    m.add_function(wrap_pyfunction!(RadialGradient, m)?)?;
    m.add_function(wrap_pyfunction!(Stop, m)?)?;
    m.add_function(wrap_pyfunction!(Pattern, m)?)?;
    m.add_function(wrap_pyfunction!(ClipPath, m)?)?;
    m.add_function(wrap_pyfunction!(Mask, m)?)?;
    m.add_function(wrap_pyfunction!(Image, m)?)?;
    m.add_function(wrap_pyfunction!(ForeignObject, m)?)?;
    
    // All remaining HTML tags
    m.add_function(wrap_pyfunction!(Abbr, m)?)?;
    m.add_function(wrap_pyfunction!(Area, m)?)?;
    m.add_function(wrap_pyfunction!(Audio, m)?)?;
    m.add_function(wrap_pyfunction!(Base, m)?)?;
    m.add_function(wrap_pyfunction!(Bdi, m)?)?;
    m.add_function(wrap_pyfunction!(Bdo, m)?)?;
    m.add_function(wrap_pyfunction!(Blockquote, m)?)?;
    m.add_function(wrap_pyfunction!(Canvas, m)?)?;
    m.add_function(wrap_pyfunction!(Cite, m)?)?;
    m.add_function(wrap_pyfunction!(Data, m)?)?;
    m.add_function(wrap_pyfunction!(Datalist, m)?)?;
    m.add_function(wrap_pyfunction!(Dd, m)?)?;
    m.add_function(wrap_pyfunction!(Del, m)?)?;
    m.add_function(wrap_pyfunction!(Dfn, m)?)?;
    m.add_function(wrap_pyfunction!(Dialog, m)?)?;
    m.add_function(wrap_pyfunction!(Dl, m)?)?;
    m.add_function(wrap_pyfunction!(Dt, m)?)?;
    m.add_function(wrap_pyfunction!(Embed, m)?)?;
    m.add_function(wrap_pyfunction!(Fieldset, m)?)?;
    m.add_function(wrap_pyfunction!(Hgroup, m)?)?;
    m.add_function(wrap_pyfunction!(Ins, m)?)?;
    m.add_function(wrap_pyfunction!(Kbd, m)?)?;
    m.add_function(wrap_pyfunction!(Legend, m)?)?;
    m.add_function(wrap_pyfunction!(Map, m)?)?;
    m.add_function(wrap_pyfunction!(Mark, m)?)?;
    m.add_function(wrap_pyfunction!(Menu, m)?)?;
    m.add_function(wrap_pyfunction!(Meter, m)?)?;
    m.add_function(wrap_pyfunction!(Noscript, m)?)?;
    m.add_function(wrap_pyfunction!(Object, m)?)?;
    m.add_function(wrap_pyfunction!(Optgroup, m)?)?;
    m.add_function(wrap_pyfunction!(OptionEl, m)?)?;
    m.add_function(wrap_pyfunction!(Picture, m)?)?;
    m.add_function(wrap_pyfunction!(Pre, m)?)?;
    m.add_function(wrap_pyfunction!(Progress, m)?)?;
    m.add_function(wrap_pyfunction!(Q, m)?)?;
    m.add_function(wrap_pyfunction!(Rp, m)?)?;
    m.add_function(wrap_pyfunction!(Rt, m)?)?;
    m.add_function(wrap_pyfunction!(Ruby, m)?)?;
    m.add_function(wrap_pyfunction!(S, m)?)?;
    m.add_function(wrap_pyfunction!(Samp, m)?)?;
    m.add_function(wrap_pyfunction!(Small, m)?)?;
    m.add_function(wrap_pyfunction!(Source, m)?)?;
    m.add_function(wrap_pyfunction!(Style, m)?)?;
    m.add_function(wrap_pyfunction!(Sub, m)?)?;
    m.add_function(wrap_pyfunction!(Sup, m)?)?;
    m.add_function(wrap_pyfunction!(Template, m)?)?;
    m.add_function(wrap_pyfunction!(Time, m)?)?;
    m.add_function(wrap_pyfunction!(Track, m)?)?;
    m.add_function(wrap_pyfunction!(U, m)?)?;
    m.add_function(wrap_pyfunction!(Var, m)?)?;
    m.add_function(wrap_pyfunction!(Video, m)?)?;
    m.add_function(wrap_pyfunction!(Wbr, m)?)?;
    
    // Custom tag function
    m.add_function(wrap_pyfunction!(CustomTag, m)?)?;
    
    // Factory function for pickle support
    m.add_function(wrap_pyfunction!(create_html_string, m)?)?;
    
    Ok(())
}