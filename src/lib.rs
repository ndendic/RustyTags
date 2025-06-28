use pyo3::prelude::*;
use pyo3::types::PyDict;
use ahash::AHashMap as HashMap; // Faster hash algorithm - significant performance win
use smallvec::{SmallVec, smallvec}; // Stack allocation for small collections
use std::sync::OnceLock; // For thread-safe lazy static initialization

// Global string constants to avoid repeated allocations
const EMPTY_STRING: &str = "";
const SPACE: &str = " ";
const QUOTE: &str = "\"";
const EQUALS_QUOTE: &str = "=\"";
const QUOTE_SPACE: &str = "\" ";
const OPEN_BRACKET: &str = "<";
const CLOSE_BRACKET: &str = ">";
const CLOSE_TAG_PREFIX: &str = "</";

// String interning for common HTML elements - reduces memory usage and improves cache locality
static INTERNED_STRINGS: OnceLock<HashMap<&'static str, &'static str>> = OnceLock::new();

fn get_interned_strings() -> &'static HashMap<&'static str, &'static str> {
    INTERNED_STRINGS.get_or_init(|| {
        let mut map = HashMap::default();
        // Common tag names
        map.insert("div", "div");
        map.insert("span", "span");
        map.insert("p", "p");
        map.insert("a", "a");
        map.insert("img", "img");
        map.insert("input", "input");
        map.insert("button", "button");
        map.insert("form", "form");
        map.insert("table", "table");
        map.insert("tr", "tr");
        map.insert("td", "td");
        map.insert("th", "th");
        map.insert("ul", "ul");
        map.insert("ol", "ol");
        map.insert("li", "li");
        map.insert("h1", "h1");
        map.insert("h2", "h2");
        map.insert("h3", "h3");
        map.insert("h4", "h4");
        map.insert("h5", "h5");
        map.insert("h6", "h6");
        // Common attribute names
        map.insert("class", "class");
        map.insert("id", "id");
        map.insert("type", "type");
        map.insert("name", "name");
        map.insert("value", "value");
        map.insert("href", "href");
        map.insert("src", "src");
        map.insert("alt", "alt");
        map.insert("title", "title");
        map.insert("for", "for");
        map.insert("method", "method");
        map.insert("action", "action");
        map
    })
}

// Get interned string if available, otherwise return the original
#[inline(always)]
fn intern_string(s: &str) -> &str {
    get_interned_strings().get(s).unwrap_or(&s)
}

// Thread-safe cache for attribute mappings not covered by fast paths
static ATTR_MAPPING_CACHE: OnceLock<std::sync::RwLock<HashMap<String, String>>> = OnceLock::new();

fn get_attr_cache() -> &'static std::sync::RwLock<HashMap<String, String>> {
    ATTR_MAPPING_CACHE.get_or_init(|| {
        std::sync::RwLock::new(HashMap::default())
    })
}

// Simple and fast attribute key fixing with caching
#[inline(always)]
fn fix_k_optimized(k: &str) -> String {
    if k == "_" {
        return k.to_string();
    }
    
    // Fast path for small strings - most HTML attributes are short
    if k.len() <= 16 {
        let mut result = String::with_capacity(k.len());
        let chars: Vec<char> = if k.starts_with('_') {
            k.chars().skip(1).collect()
        } else {
            k.chars().collect()
        };
        
        for ch in chars {
            if ch == '_' {
                result.push('-');
            } else {
                result.push(ch);
            }
        }
        return result;
    }
    
    // For longer strings, check cache first
    let cache = get_attr_cache();
    
    // Try read lock first (fast path)
    if let Ok(read_cache) = cache.read() {
        if let Some(cached_result) = read_cache.get(k) {
            return cached_result.clone();
        }
    }
    
    // Compute result and cache it
    let result = k.strip_prefix('_').unwrap_or(k).replace('_', "-");
    
    // Write to cache (fallback if lock fails is just to return without caching)
    if let Ok(mut write_cache) = cache.write() {
        // Limit cache size to prevent memory growth
        if write_cache.len() < 1000 {
            write_cache.insert(k.to_string(), result.clone());
        }
    }
    
    result
}

// Fast attribute mapping with common case optimization + caching
#[inline(always)]
fn attrmap_optimized(attr: &str) -> String {
    // Handle most common cases first - these cover 80% of usage
    match attr {
        "cls" => return intern_string("class").to_string(),
        "_class" => return intern_string("class").to_string(),
        "htmlClass" => return intern_string("class").to_string(),
        "klass" => return intern_string("class").to_string(),
        "_for" => return intern_string("for").to_string(),
        "fr" => return intern_string("for").to_string(),
        "htmlFor" => return intern_string("for").to_string(),
        // Add more common fast paths
        "id" => return intern_string("id").to_string(),
        "type" => return intern_string("type").to_string(),
        "name" => return intern_string("name").to_string(),
        "value" => return intern_string("value").to_string(),
        "href" => return intern_string("href").to_string(),
        "src" => return intern_string("src").to_string(),
        "alt" => return intern_string("alt").to_string(),
        "title" => return intern_string("title").to_string(),
        "method" => return intern_string("method").to_string(),
        "action" => return intern_string("action").to_string(),
        _ => {}
    }
    
    // Fast special character check for remaining cases
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

// Thread-safe cache for tag name normalization
static TAG_NAME_CACHE: OnceLock<std::sync::RwLock<HashMap<String, String>>> = OnceLock::new();

fn get_tag_cache() -> &'static std::sync::RwLock<HashMap<String, String>> {
    TAG_NAME_CACHE.get_or_init(|| {
        std::sync::RwLock::new(HashMap::default())
    })
}

// Optimized tag name normalization with caching
#[inline(always)]
fn normalize_tag_name(tag_name: &str) -> String {
    // Fast path for already lowercase strings
    if tag_name.chars().all(|c| c.is_ascii_lowercase()) {
        return intern_string(tag_name).to_string();
    }
    
    let cache = get_tag_cache();
    
    // Try read lock first (fast path)
    if let Ok(read_cache) = cache.read() {
        if let Some(cached_result) = read_cache.get(tag_name) {
            return cached_result.clone();
        }
    }
    
    // Compute result
    let normalized = tag_name.to_ascii_lowercase();
    let interned = intern_string(&normalized).to_string();
    
    // Cache the result
    if let Ok(mut write_cache) = cache.write() {
        // Limit cache size to prevent memory growth
        if write_cache.len() < 100 {
            write_cache.insert(tag_name.to_string(), interned.clone());
        }
    }
    
    interned
}

// High-performance string arena with simple, fast operations
struct StringArena {
    buffer: String,
}

impl StringArena {
    #[inline(always)]
    fn new(initial_capacity: usize) -> Self {
        StringArena {
            buffer: String::with_capacity(initial_capacity),
        }
    }
    
    #[inline(always)]
    fn append(&mut self, s: &str) {
        self.buffer.push_str(s);
    }
    
    #[inline(always)]
    fn append_char(&mut self, c: char) {
        self.buffer.push(c);
    }
    
    #[inline(always)]
    fn into_string(self) -> String {
        self.buffer
    }
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
    
    let mut arena = StringArena::new(total_capacity);
    arena.append_char(' ');
    
    // Process attributes in a single pass
    for (k, v) in attrs {
        let mapped_key = attrmap_optimized(k);
        arena.append(&mapped_key);
        arena.append(EQUALS_QUOTE);
        arena.append(v);
        arena.append(QUOTE_SPACE);
    }
    
    let mut result = arena.into_string();
    // Remove trailing space
    result.pop();
    result
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
            // Optimized type checking for small collections
            if let Ok(html_string) = child_obj.extract::<PyRef<HtmlString>>(py) {
                result.push_str(&html_string.content);
                continue;
            }
            
            if let Ok(s) = child_obj.extract::<&str>(py) {
                result.push_str(s);
                continue;
            }
            
            if let Ok(i) = child_obj.extract::<i64>(py) {
                let mut buffer = itoa::Buffer::new();
                result.push_str(buffer.format(i));
                continue;
            }
            
            if let Ok(f) = child_obj.extract::<f64>(py) {
                let mut buffer = ryu::Buffer::new();
                result.push_str(buffer.format(f));
                continue;
            }
            
            let child_type = child_obj.bind(py).get_type().name()?;
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                format!("Unsupported child type: {}", child_type)
            ));
        }
        
        return Ok(result);
    }
    
    // Larger collections use arena allocation
    let estimated_capacity = children.len() * 64; // Conservative estimate
    let mut arena = StringArena::new(estimated_capacity);
    
    for child_obj in children {
        // Fast path for HtmlString - direct access to content
        if let Ok(html_string) = child_obj.extract::<PyRef<HtmlString>>(py) {
            arena.append(&html_string.content);
            continue;
        }
        
        // Fast path for strings
        if let Ok(s) = child_obj.extract::<&str>(py) {
            arena.append(s);
            continue;
        }
        
        // Fast path for integers  
        if let Ok(i) = child_obj.extract::<i64>(py) {
            // Use faster integer to string conversion
            let mut buffer = itoa::Buffer::new();
            arena.append(buffer.format(i));
            continue;
        }
        
        // Fast path for floats
        if let Ok(f) = child_obj.extract::<f64>(py) {
            let mut buffer = ryu::Buffer::new();
            arena.append(buffer.format(f));
            continue;
        }
        
        // Fallback for other types
        let child_type = child_obj.bind(py).get_type().name()?;
        return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            format!("Unsupported child type: {}", child_type)
        ));
    }
    
    Ok(arena.into_string())
}

// Core HtmlString with optimized memory layout
#[pyclass]
pub struct HtmlString {
    #[pyo3(get)]
    content: String,
}

#[pymethods]
impl HtmlString {
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
}

impl HtmlString {
    #[inline(always)]
    fn new(content: String) -> Self {
        HtmlString { content }
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
    let mut arena = StringArena::new(capacity);
    
    // Build HTML in a single pass with minimal function calls
    arena.append_char('<');
    arena.append(&tag_lower);
    arena.append(&attr_string);
    arena.append_char('>');
    arena.append(&children_string);
    arena.append(CLOSE_TAG_PREFIX);
    arena.append(&tag_lower);
    arena.append_char('>');
    
    Ok(HtmlString::new(arena.into_string()))
}

// Optimized macro with aggressive inlining and fast paths
macro_rules! html_tag_optimized {
    ($name:ident, $doc:expr) => {
        #[pyfunction]
        #[doc = $doc]
        #[pyo3(signature = (*children, **kwargs))]
        #[inline(always)]
        fn $name(children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<HtmlString> {
            // Fast path for no attributes
            if kwargs.is_none() {
                let children_string = process_children_optimized(&children, py)?;
                let tag_name = normalize_tag_name(stringify!($name));
                
                let capacity = tag_name.len() * 2 + children_string.len() + 5;
                let mut arena = StringArena::new(capacity);
                
                arena.append_char('<');
                arena.append(&tag_name);
                arena.append_char('>');
                arena.append(&children_string);
                arena.append(CLOSE_TAG_PREFIX);
                arena.append(&tag_name);
                arena.append_char('>');
                
                return Ok(HtmlString::new(arena.into_string()));
            }
            
            // Full path with attributes - use optimized HashMap
            let mut attrs = HashMap::default();
            
            if let Some(kwargs) = kwargs {
                for (key, value) in kwargs.iter() {
                    let key_str = key.extract::<String>()?;
                    let value_str = value.extract::<String>()?;
                    attrs.insert(key_str, value_str);
                }
            }
            
            build_html_tag_optimized(stringify!($name), children, attrs, py)
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
            let value_str = value.extract::<String>()?;
            attrs.insert(key_str, value_str);
        }
    }
    
    // Separate head and body content automatically like Air does
    // Use SmallVec for stack allocation - most HTML has few head elements
    let mut head_content: SmallVec<[PyObject; 4]> = smallvec![];
    let mut body_content: SmallVec<[PyObject; 8]> = smallvec![];
    
    for child_obj in children {
        // Check if this is a head-specific tag by looking at the content string
        if let Ok(html_string) = child_obj.extract::<PyRef<HtmlString>>(py) {
            let content = &html_string.content;
            // Check if content starts with head-specific tags
            if content.starts_with("<title") || content.starts_with("<link") || 
               content.starts_with("<meta") || content.starts_with("<style") || 
               content.starts_with("<script") || content.starts_with("<base") {
                head_content.push(child_obj);
            } else {
                body_content.push(child_obj);
            }
        } else {
            // Non-HtmlString content goes to body
            body_content.push(child_obj);
        }
    }
    
    // Process head and body content separately
    let head_string = process_children_optimized(&head_content, py)?;
    let body_string = process_children_optimized(&body_content, py)?;
    
    let attr_string = build_attributes_optimized(&attrs);
    
    // Calculate capacity: DOCTYPE + html structure + head + body + attributes
    let capacity = 15 + 26 + attr_string.len() + head_string.len() + body_string.len(); // "<!doctype html><html><head></head><body></body></html>"
    let mut arena = StringArena::new(capacity);
    
    // Build complete HTML structure like Air
    arena.append("<!doctype html>");
    arena.append("<html");
    arena.append(&attr_string);
    arena.append(">");
    arena.append("<head>");
    arena.append(&head_string);
    arena.append("</head>");
    arena.append("<body>");
    arena.append(&body_string);
    arena.append("</body>");
    arena.append("</html>");
    
    Ok(HtmlString::new(arena.into_string()))
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

// Keep the old Tag class for backwards compatibility
#[pyclass(subclass)]
pub struct Tag {
    #[pyo3(get)]
    _name: String,
    #[pyo3(get)]  
    _module: String,
    _children: Vec<PyObject>,
    _attrs: HashMap<String, String>,
}

impl Tag {
    fn render_child(&self, child_obj: &PyObject, py: Python) -> PyResult<String> {
        if let Ok(html_string) = child_obj.extract::<PyRef<HtmlString>>(py) {
            return Ok(html_string.content.clone());
        }
        if let Ok(tag) = child_obj.extract::<PyRef<Tag>>(py) {
            return tag.render(py);
        }
        if let Ok(s) = child_obj.extract::<String>(py) {
            return Ok(s);
        }
        if let Ok(i) = child_obj.extract::<i64>(py) {
            return Ok(i.to_string());
        }
        if let Ok(f) = child_obj.extract::<f64>(py) {
            return Ok(f.to_string());
        }
        
        let child_type = child_obj.bind(py).get_type().name()?;
        let error_msg = format!(
            "Unsupported child type: {}\n in tag {}\n child {:?}\n data {:?}",
            child_type,
            self.name(),
            child_obj,
            self._attrs
        );
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(error_msg))
    }
}

#[pymethods]
impl Tag {
    #[new]
    #[pyo3(signature = (*children, **kwargs))]
    fn new(children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut attrs = HashMap::default();
        
        if let Some(kwargs) = kwargs {
            for (key, value) in kwargs.iter() {
                let key_str = key.extract::<String>()?;
                let value_str = value.extract::<String>()?;
                attrs.insert(key_str, value_str);
            }
        }
        
        Ok(Tag {
            _name: "Tag".to_string(),
            _module: "rusty_tags".to_string(),
            _children: children,
            _attrs: attrs,
        })
    }
    
    #[getter]
    fn name(&self) -> String {
        normalize_tag_name(&self._name)
    }
    
    #[getter]
    fn attrs(&self) -> String {
        build_attributes_optimized(&self._attrs)
    }
    
    #[getter]
    fn children(&self, py: Python) -> PyResult<String> {
        let mut elements = Vec::new();
        
        for child_obj in &self._children {
            elements.push(self.render_child(child_obj, py)?);
        }
        
        Ok(elements.join(""))
    }
    
    fn render(&self, py: Python) -> PyResult<String> {
        let name = self.name();
        let attrs = self.attrs();
        let children = self.children(py)?;
        
        Ok(format!("<{}{}>{}</{}>", name, attrs, children, name))
    }
    
    fn __repr__(&self, py: Python) -> PyResult<String> {
        self.render(py)
    }
    
    fn __str__(&self, py: Python) -> PyResult<String> {
        self.render(py)
    }
    
    fn _repr_html_(&self, py: Python) -> PyResult<String> {
        self.render(py)
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn rusty_tags(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core classes
    m.add_class::<HtmlString>()?;
    m.add_class::<Tag>()?; // For backwards compatibility
    
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
    
    Ok(())
}
