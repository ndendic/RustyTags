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

#[inline(always)]
fn get_bump_arena() -> Bump {
    ARENA_POOL.with(|pool| {
        pool.borrow_mut().pop().unwrap_or_else(|| Bump::with_capacity(8192))
    })
}

#[inline(always)]
fn return_arena(mut arena: Bump) {
    arena.reset();
    ARENA_POOL.with(|pool| {
        let mut pool = pool.borrow_mut();
        if pool.len() < 8 {
            pool.push(arena);
        }
    });
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
// SIMD-ACCELERATED STRING OPERATIONS
// =============================================================================

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

// SIMD-accelerated ASCII lowercase conversion
#[inline(always)]
fn fast_ascii_lowercase(input: &str) -> String {
    let bytes = input.as_bytes();
    
    // Fast path for short strings
    if bytes.len() <= 16 {
        return input.to_ascii_lowercase();
    }
    
    #[cfg(target_arch = "x86_64")]
    {
        if is_x86_feature_detected!("avx2") && bytes.len() >= 32 {
            return unsafe { simd_lowercase_avx2(bytes) };
        }
        if is_x86_feature_detected!("sse2") && bytes.len() >= 16 {
            return unsafe { simd_lowercase_sse2(bytes) };
        }
    }
    
    // Fallback for other architectures or small strings
    input.to_ascii_lowercase()
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2")]
unsafe fn simd_lowercase_avx2(bytes: &[u8]) -> String {
    let mut result = Vec::with_capacity(bytes.len());
    let mask = _mm256_set1_epi8(0x20);
    let upper_a = _mm256_set1_epi8(b'A' as i8 - 1);
    let upper_z = _mm256_set1_epi8(b'Z' as i8 + 1);
    
    let chunks = bytes.chunks_exact(32);
    let remainder = chunks.remainder();
    
    for chunk in chunks {
        let data = _mm256_loadu_si256(chunk.as_ptr() as *const __m256i);
        let gt_a = _mm256_cmpgt_epi8(data, upper_a);
        let lt_z = _mm256_cmpgt_epi8(upper_z, data);
        let is_upper = _mm256_and_si256(gt_a, lt_z);
        let to_add = _mm256_and_si256(mask, is_upper);
        let lowered = _mm256_add_epi8(data, to_add);
        
        let mut temp = [0u8; 32];
        _mm256_storeu_si256(temp.as_mut_ptr() as *mut __m256i, lowered);
        result.extend_from_slice(&temp);
    }
    
    // Handle remainder with scalar operations
    for &byte in remainder {
        result.push(if byte.is_ascii_uppercase() { byte + 32 } else { byte });
    }
    
    String::from_utf8_unchecked(result)
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "sse2")]
unsafe fn simd_lowercase_sse2(bytes: &[u8]) -> String {
    let mut result = Vec::with_capacity(bytes.len());
    let mask = _mm_set1_epi8(0x20);
    let upper_a = _mm_set1_epi8(b'A' as i8 - 1);
    let upper_z = _mm_set1_epi8(b'Z' as i8 + 1);
    
    let chunks = bytes.chunks_exact(16);
    let remainder = chunks.remainder();
    
    for chunk in chunks {
        let data = _mm_loadu_si128(chunk.as_ptr() as *const __m128i);
        let gt_a = _mm_cmpgt_epi8(data, upper_a);
        let lt_z = _mm_cmpgt_epi8(upper_z, data);
        let is_upper = _mm_and_si128(gt_a, lt_z);
        let to_add = _mm_and_si128(mask, is_upper);
        let lowered = _mm_add_epi8(data, to_add);
        
        let mut temp = [0u8; 16];
        _mm_storeu_si128(temp.as_mut_ptr() as *mut __m128i, lowered);
        result.extend_from_slice(&temp);
    }
    
    // Handle remainder
    for &byte in remainder {
        result.push(if byte.is_ascii_uppercase() { byte + 32 } else { byte });
    }
    
    String::from_utf8_unchecked(result)
}

// Fast character contains check using SIMD when available
#[inline(always)]
fn contains_special_chars(s: &str) -> bool {
    // For very short strings, use simple check
    if s.len() <= 8 {
        return s.chars().any(|c| match c {
            '@' | '.' | '-' | '!' | '~' | ':' | '[' | ']' | '(' | ')' | 
            '{' | '}' | '$' | '%' | '^' | '&' | '*' | '+' | '=' | '|' | 
            '/' | '?' | '<' | '>' | ',' | '`' => true,
            _ => false,
        });
    }
    
    // Use memchr for longer strings (SIMD-accelerated)
    use memchr::memchr;
    let bytes = s.as_bytes();
    
    memchr(b'@', bytes).is_some() || 
    memchr(b'.', bytes).is_some() ||
    memchr(b'-', bytes).is_some() ||
    memchr(b'!', bytes).is_some() ||
    memchr(b'~', bytes).is_some() ||
    memchr(b':', bytes).is_some() ||
    memchr(b'[', bytes).is_some() ||
    memchr(b']', bytes).is_some() ||
    memchr(b'(', bytes).is_some() ||
    memchr(b')', bytes).is_some() ||
    memchr(b'{', bytes).is_some() ||
    memchr(b'}', bytes).is_some() ||
    memchr(b'$', bytes).is_some() ||
    memchr(b'%', bytes).is_some() ||
    memchr(b'^', bytes).is_some() ||
    memchr(b'&', bytes).is_some() ||
    memchr(b'*', bytes).is_some() ||
    memchr(b'+', bytes).is_some() ||
    memchr(b'=', bytes).is_some() ||
    memchr(b'|', bytes).is_some() ||
    memchr(b'/', bytes).is_some() ||
    memchr(b'?', bytes).is_some() ||
    memchr(b'<', bytes).is_some() ||
    memchr(b'>', bytes).is_some() ||
    memchr(b',', bytes).is_some() ||
    memchr(b'`', bytes).is_some()
}

// =============================================================================
// OPTIMIZED ATTRIBUTE AND TAG PROCESSING
// =============================================================================

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
    
    // Fast special character check using SIMD
    if contains_special_chars(attr) {
        return attr.to_string();
    }
    
    fix_k_optimized(attr)
}

// Cached tag name normalization
#[inline(always)]
fn normalize_tag_name(tag_name: &str) -> String {
    // Fast path for already normalized strings
    if tag_name.len() <= 16 && tag_name.chars().all(|c| c.is_ascii_lowercase()) {
        return tag_name.to_string();
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
        
        // Compute using SIMD-accelerated lowercase
        let normalized = fast_ascii_lowercase(tag_name);
        
        cache.borrow_mut().insert(tag_name.to_string(), Cow::Owned(normalized.clone()));
        GLOBAL_TAG_CACHE.insert(tag_name.to_string(), Cow::Owned(normalized.clone()));
        normalized
    })
}

// =============================================================================
// COMPACT ATTRIBUTE STORAGE
// =============================================================================

#[derive(Debug)]
enum AttributeStorage {
    Empty,
    Single(String, String),
    Double([(String, String); 2]),
    Triple([(String, String); 3]),
    Many(HashMap<String, String>),
}

impl AttributeStorage {
    #[inline(always)]
    fn from_hashmap(attrs: HashMap<String, String>) -> Self {
        let len = attrs.len();
        match len {
            0 => Self::Empty,
            1 => {
                let (k, v) = attrs.into_iter().next().unwrap();
                let mapped_k = attrmap_optimized(&k);
                Self::Single(mapped_k, v)
            },
            2 => {
                let mut iter = attrs.into_iter();
                let (k1, v1) = iter.next().unwrap();
                let (k2, v2) = iter.next().unwrap();
                let mapped_k1 = attrmap_optimized(&k1);
                let mapped_k2 = attrmap_optimized(&k2);
                Self::Double([(mapped_k1, v1), (mapped_k2, v2)])
            },
            3 => {
                let mut iter = attrs.into_iter();
                let (k1, v1) = iter.next().unwrap();
                let (k2, v2) = iter.next().unwrap();
                let (k3, v3) = iter.next().unwrap();
                let mapped_k1 = attrmap_optimized(&k1);
                let mapped_k2 = attrmap_optimized(&k2);
                let mapped_k3 = attrmap_optimized(&k3);
                Self::Triple([(mapped_k1, v1), (mapped_k2, v2), (mapped_k3, v3)])
            },
            _ => {
                let mapped: HashMap<String, String> = attrs.into_iter()
                    .map(|(k, v)| (attrmap_optimized(&k), v))
                    .collect();
                Self::Many(mapped)
            }
        }
    }
    
    #[inline(always)]
    fn build_string(&self) -> String {
        match self {
            Self::Empty => String::new(),
            Self::Single(k, v) => {
                let capacity = k.len() + v.len() + 5; // ' key="value"'
                let mut result = get_pooled_string(capacity);
                result.push(' ');
                result.push_str(k);
                result.push_str("=\"");
                result.push_str(v);
                result.push('"');
                result
            },
            Self::Double(attrs) => {
                let capacity = attrs.iter()
                    .map(|(k, v)| k.len() + v.len() + 4)
                    .sum::<usize>() + 1;
                let mut result = get_pooled_string(capacity);
                for (k, v) in attrs {
                    result.push(' ');
                    result.push_str(k);
                    result.push_str("=\"");
                    result.push_str(v);
                    result.push('"');
                }
                result
            },
            Self::Triple(attrs) => {
                let capacity = attrs.iter()
                    .map(|(k, v)| k.len() + v.len() + 4)
                    .sum::<usize>() + 1;
                let mut result = get_pooled_string(capacity);
                for (k, v) in attrs {
                    result.push(' ');
                    result.push_str(k);
                    result.push_str("=\"");
                    result.push_str(v);
                    result.push('"');
                }
                result
            },
            Self::Many(attrs) => {
                let capacity = attrs.iter()
                    .map(|(k, v)| k.len() + v.len() + 4)
                    .sum::<usize>() + 1;
                let mut result = get_pooled_string(capacity);
                for (k, v) in attrs {
                    result.push(' ');
                    result.push_str(k);
                    result.push_str("=\"");
                    result.push_str(v);
                    result.push('"');
                }
                result
            }
        }
    }
}

// =============================================================================
// ZERO-COPY CHILD PROCESSING WITH BRANCH PREDICTION
// =============================================================================

// Branch prediction hints (simplified without unstable intrinsics)
#[inline(always)]
fn likely(b: bool) -> bool {
    b
}

#[inline(always)]
fn unlikely(b: bool) -> bool {
    b
}

// Streaming HTML writer for zero-copy processing
struct HtmlWriter {
    buffer: String,
}

impl HtmlWriter {
    #[inline(always)]
    fn new(capacity: usize) -> Self {
        Self {
            buffer: get_pooled_string(capacity),
        }
    }
    
    #[inline(always)]
    fn write_tag_start(&mut self, tag: &str, attrs: &AttributeStorage) {
        self.buffer.push('<');
        self.buffer.push_str(tag);
        let attr_string = attrs.build_string();
        self.buffer.push_str(&attr_string);
        return_to_pool(attr_string);
        self.buffer.push('>');
    }
    
    #[inline(always)]
    fn write_tag_end(&mut self, tag: &str) {
        self.buffer.push_str("</");
        self.buffer.push_str(tag);
        self.buffer.push('>');
    }
    
    #[inline(always)]
    fn write_child(&mut self, child: &PyObject, py: Python) -> PyResult<()> {
        // Order by likelihood - strings are most common
        if likely(child.extract::<&str>(py).is_ok()) {
            self.buffer.push_str(child.extract::<&str>(py).unwrap());
            return Ok(());
        }
        
        if likely(child.extract::<PyRef<HtmlString>>(py).is_ok()) {
            let html_string = child.extract::<PyRef<HtmlString>>(py).unwrap();
            self.buffer.push_str(&html_string.content);
            return Ok(());
        }
        
        if unlikely(child.extract::<i64>(py).is_ok()) {
            let i = child.extract::<i64>(py).unwrap();
            let mut buffer = itoa::Buffer::new();
            self.buffer.push_str(buffer.format(i));
            return Ok(());
        }
        
        if unlikely(child.extract::<f64>(py).is_ok()) {
            let f = child.extract::<f64>(py).unwrap();
            let mut buffer = ryu::Buffer::new();
            self.buffer.push_str(buffer.format(f));
            return Ok(());
        }
        
        // Handle other types
        let child_type = child.bind(py).get_type().name()?;
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            format!("Unsupported child type: {}", child_type)
        ))
    }
    
    // Bulk child processing with type-specific optimizations
    #[inline(always)]
    fn write_children_bulk(&mut self, children: &[PyObject], py: Python) -> PyResult<()> {
        // Group children by type for batch processing
        let mut string_chunks = Vec::with_capacity(16);
        let mut html_chunks: Vec<&str> = Vec::with_capacity(16);
        
        for child in children {
            if likely(child.extract::<&str>(py).is_ok()) {
                let s = child.extract::<&str>(py).unwrap();
                string_chunks.push(s);
                
                // Batch write string chunks when we have enough
                if unlikely(string_chunks.len() >= 8) {
                    for s in string_chunks.drain(..) {
                        self.buffer.push_str(s);
                    }
                }
            } else if likely(child.extract::<PyRef<HtmlString>>(py).is_ok()) {
                // Flush pending strings first
                for s in string_chunks.drain(..) {
                    self.buffer.push_str(s);
                }
                
                let html_string = child.extract::<PyRef<HtmlString>>(py).unwrap();
                self.buffer.push_str(&html_string.content);
            } else {
                // Flush pending strings first
                for s in string_chunks.drain(..) {
                    self.buffer.push_str(s);
                }
                
                // Handle other types individually
                self.write_child(child, py)?;
            }
        }
        
        // Flush remaining string chunks
        for s in string_chunks {
            self.buffer.push_str(s);
        }
        
        Ok(())
    }
    
    #[inline(always)]
    fn into_html_string(self) -> HtmlString {
        HtmlString::new(self.buffer)
    }
}

// Optimized bulk child processing for complex scenarios
#[inline(always)]
fn process_children_with_prefetch(children: &[PyObject], py: Python) -> PyResult<String> {
    if children.is_empty() {
        return Ok(String::new());
    }
    
    // Enhanced capacity estimation based on child types
    let estimated_capacity = estimate_children_capacity(children, py);
    let mut writer = HtmlWriter::new(estimated_capacity);
    
    // Batch process children with type-specific optimizations
    writer.write_children_bulk(children, py)?;
    
    Ok(writer.buffer)
}

// Smart capacity estimation for better memory allocation
#[inline(always)]
fn estimate_children_capacity(children: &[PyObject], py: Python) -> usize {
    let mut capacity = 0;
    let base_per_child = 32; // Conservative base estimate
    
    for child in children.iter().take(std::cmp::min(children.len(), 10)) {
        // Sample first 10 children for estimation
        if child.extract::<&str>(py).is_ok() {
            let s = child.extract::<&str>(py).unwrap();
            capacity += s.len() + 10; // String + tag overhead
        } else if child.extract::<PyRef<HtmlString>>(py).is_ok() {
            let html_string = child.extract::<PyRef<HtmlString>>(py).unwrap();
            capacity += html_string.content.len() + 10;
        } else {
            capacity += base_per_child;
        }
    }
    
    // Scale estimation for remaining children
    if children.len() > 10 {
        let avg_per_sample = capacity / std::cmp::min(children.len(), 10);
        capacity = avg_per_sample * children.len();
    }
    
    // Add buffer for tag overhead
    capacity + children.len() * 20
}

// Specialized functions for high-performance list rendering
#[pyfunction]
fn render_list_optimized(
    py: Python,
    tag: &str,
    items: Vec<PyObject>,
    item_tag: &str,
    class_name: std::option::Option<String>,
    item_class_prefix: std::option::Option<String>
) -> PyResult<HtmlString> {
    if items.is_empty() {
        let empty_tag = format!("<{tag}></{tag}>");
        return Ok(HtmlString::new(empty_tag));
    }
    
    // Pre-calculate total capacity for optimal allocation
    let base_capacity = tag.len() * 2 + 5; // <tag></tag>
    let item_capacity = item_tag.len() * 2 + 5; // <item></item>
    let total_item_capacity = item_capacity * items.len();
    
    // Estimate content size
    let mut content_size = 0;
    for item in items.iter().take(5) { // Sample first 5 items
        if let Ok(s) = item.extract::<&str>(py) {
            content_size += s.len();
        } else {
            content_size += 20; // Conservative estimate
        }
    }
    let avg_content = if items.len() > 5 { content_size * items.len() / 5 } else { content_size };
    
    let class_capacity = class_name.as_ref().map_or(0, |c| c.len() + 10);
    let total_capacity = base_capacity + total_item_capacity + avg_content + class_capacity;
    
    let mut buffer = get_pooled_string(total_capacity);
    
    // Build opening tag
    buffer.push('<');
    buffer.push_str(tag);
    if let Some(ref class) = class_name {
        buffer.push_str(" class=\"");
        buffer.push_str(class);
        buffer.push('"');
    }
    buffer.push('>');
    
    // Bulk render items
    for (i, item) in items.iter().enumerate() {
        buffer.push('<');
        buffer.push_str(item_tag);
        
        if let Some(ref prefix) = item_class_prefix {
            buffer.push_str(" class=\"");
            buffer.push_str(prefix);
            buffer.push_str(&i.to_string());
            buffer.push('"');
        }
        
        buffer.push('>');
        
        // Optimized item content handling
        if let Ok(s) = item.extract::<&str>(py) {
            buffer.push_str(s);
        } else if let Ok(html) = item.extract::<PyRef<HtmlString>>(py) {
            buffer.push_str(&html.content);
        } else {
            // Fallback to string representation
            let item_bound = item.bind(py).str()?;
            let item_str = item_bound.to_cow()?;
            buffer.push_str(&item_str);
        }
        
        buffer.push_str("</");
        buffer.push_str(item_tag);
        buffer.push('>');
    }
    
    // Closing tag
    buffer.push_str("</");
    buffer.push_str(tag);
    buffer.push('>');
    
    Ok(HtmlString::new(buffer))
}

// Specialized function for table rendering
#[pyfunction]
fn render_table_optimized(
    py: Python,
    headers: Vec<String>,
    rows: Vec<Vec<PyObject>>,
    table_class: std::option::Option<String>,
    header_class: std::option::Option<String>,
    row_class_prefix: std::option::Option<String>
) -> PyResult<HtmlString> {
    if rows.is_empty() {
        return Ok(HtmlString::new("<table></table>".to_string()));
    }
    
    // Pre-calculate capacity
    let header_capacity = headers.iter().map(|h| h.len() + 8).sum::<usize>(); // <th>header</th>
    let row_capacity = rows.len() * rows.get(0).map_or(0, |r| r.len()) * 50; // Rough estimate
    let class_capacity = table_class.as_ref().map_or(0, |c| c.len() + 15);
    let total_capacity = header_capacity + row_capacity + class_capacity + 200; // Buffer
    
    let mut buffer = get_pooled_string(total_capacity);
    
    // Table opening
    buffer.push_str("<table");
    if let Some(ref class) = table_class {
        buffer.push_str(" class=\"");
        buffer.push_str(class);
        buffer.push('"');
    }
    buffer.push_str("><thead><tr");
    if let Some(ref hclass) = header_class {
        buffer.push_str(" class=\"");
        buffer.push_str(hclass);
        buffer.push('"');
    }
    buffer.push('>');
    
    // Headers
    for header in &headers {
        buffer.push_str("<th>");
        buffer.push_str(header);
        buffer.push_str("</th>");
    }
    buffer.push_str("</tr></thead><tbody>");
    
    // Rows
    for (row_idx, row) in rows.iter().enumerate() {
        buffer.push_str("<tr");
        if let Some(ref prefix) = row_class_prefix {
            buffer.push_str(" class=\"");
            buffer.push_str(prefix);
            if row_idx % 2 == 0 { buffer.push_str("even"); } else { buffer.push_str("odd"); }
            buffer.push('"');
        }
        buffer.push('>');
        
        for cell in row {
            buffer.push_str("<td>");
            if let Ok(s) = cell.extract::<&str>(py) {
                buffer.push_str(s);
            } else if let Ok(html) = cell.extract::<PyRef<HtmlString>>(py) {
                buffer.push_str(&html.content);
            } else {
                let cell_bound = cell.bind(py).str()?;
                let cell_str = cell_bound.to_cow()?;
                buffer.push_str(&cell_str);
            }
            buffer.push_str("</td>");
        }
        buffer.push_str("</tr>");
    }
    
    buffer.push_str("</tbody></table>");
    Ok(HtmlString::new(buffer))
}

// =============================================================================
// IMMEDIATE RENDERING WITH DICT EXPLOSION AND PARALLELISM  
// =============================================================================

// Process children and extract attribute dictionaries
fn separate_children_and_dicts(children: &[PyObject], py: Python) -> PyResult<(Vec<PyObject>, HashMap<String, String>)> {
    let mut actual_children = Vec::new();
    let mut extracted_attrs = HashMap::new();
    
    for child in children {
        // Check if child is a dictionary (should be exploded as attributes)
        if let Ok(dict) = child.downcast_bound::<PyDict>(py) {
            // Explode dictionary into attributes
            for (key, value) in dict.iter() {
                let key_str = key.extract::<String>()?;
                let value_str = value.extract::<String>()?;
                extracted_attrs.insert(key_str, value_str);
            }
        } else {
            // Regular child content
            actual_children.push(child.clone_ref(py));
        }
    }
    
    Ok((actual_children, extracted_attrs))
}

// Process children with potential optimizations for large lists
fn process_children_parallel(children: &[PyObject], py: Python) -> PyResult<String> {
    if children.is_empty() {
        return Ok(String::new());
    }
    
    // For now, use optimized sequential processing
    // Note: True parallelism is limited by Python's GIL
    // Future optimization could use Rayon with proper Python handling
    process_children_with_prefetch(children, py)
}

// Create tag with immediate rendering, dict explosion, and parallelism
fn create_tag_immediate(
    tag_name: &str,
    children: Vec<PyObject>, 
    kwargs: std::option::Option<&Bound<'_, PyDict>>,
    py: Python
) -> PyResult<String> {
    // Step 1: Separate actual children from attribute dictionaries
    let (actual_children, dict_attrs) = separate_children_and_dicts(&children, py)?;
    
    // Step 2: Merge kwargs and dict attributes
    let mut all_attrs = dict_attrs;
    if let Some(kwargs) = kwargs {
        for (key, value) in kwargs.iter() {
            let key_str = key.extract::<String>()?;
            let value_str = value.extract::<String>()?;
            // kwargs override dict attributes
            all_attrs.insert(key_str, value_str);
        }
    }
    
    // Step 3: Process children (with potential parallelism)
    let children_string = process_children_parallel(&actual_children, py)?;
    
    // Step 4: Build attributes string
    let attr_storage = AttributeStorage::from_hashmap(all_attrs);
    let attr_string = attr_storage.build_string();
    
    // Step 5: Assemble final HTML
    let tag_lower = tag_name.to_lowercase();
    let capacity = tag_lower.len() * 2 + attr_string.len() + children_string.len() + 5;
    
    let mut result = get_pooled_string(capacity);
    result.push('<');
    result.push_str(&tag_lower);
    result.push_str(&attr_string);
    result.push('>');
    result.push_str(&children_string);
    result.push_str("</");
    result.push_str(&tag_lower);
    result.push('>');
    
    // Return strings to pools
    return_to_pool(attr_string);
    return_to_pool(children_string);
    
    Ok(result)
}

// =============================================================================
// CORE HTML STRING AND TAG STRUCTURES
// =============================================================================

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

// Optimized tag builder with all improvements
#[inline(always)]
fn build_html_tag_optimized(
    tag_name: &str, 
    children: Vec<PyObject>, 
    attrs: HashMap<String, String>,
    py: Python
) -> PyResult<HtmlString> {
    let tag_lower = normalize_tag_name(tag_name);
    let attr_storage = AttributeStorage::from_hashmap(attrs);
    let children_string = process_children_with_prefetch(&children, py)?;
    
    // Calculate exact capacity
    let attr_string = attr_storage.build_string();
    let capacity = tag_lower.len() * 2 + attr_string.len() + children_string.len() + 5;
    
    let mut writer = HtmlWriter::new(capacity);
    writer.write_tag_start(&tag_lower, &attr_storage);
    writer.buffer.push_str(&children_string);
    writer.write_tag_end(&tag_lower);
    
    // Return strings to pools
    return_to_pool(attr_string);
    return_to_pool(children_string);
    
    Ok(writer.into_html_string())
}

// Ultra-optimized macro with all improvements
macro_rules! html_tag_optimized {
    ($name:ident, $doc:expr) => {
        #[pyfunction]
        #[doc = $doc]
        #[pyo3(signature = (*children, **kwargs))]
        #[inline(always)]
        fn $name(children: Vec<PyObject>, kwargs: std::option::Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<String> {
            let tag_name = normalize_tag_name(stringify!($name));
            create_tag_immediate(&tag_name, children, kwargs, py)
        }
    };
}

// Generate all HTML tag functions with optimizations
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
html_tag_optimized!(Footer, "Defines a page footer");
html_tag_optimized!(Thead, "Defines a table header group");
html_tag_optimized!(Tbody, "Defines a table body group");

// Additional HTML tags for full Air compatibility
html_tag_optimized!(Abbr, "Defines an abbreviation or an acronym");
html_tag_optimized!(Address, "Defines contact information for the author/owner of a document");
html_tag_optimized!(Area, "Defines an area inside an image map");
html_tag_optimized!(Article, "Defines an article");
html_tag_optimized!(Audio, "Defines embedded sound content");
html_tag_optimized!(Base, "Specifies the base URL/target for all relative URLs in a document");
html_tag_optimized!(Bdi, "Isolates a part of text that might be formatted in a different direction from other text outside it");
html_tag_optimized!(Bdo, "Overrides the current text direction");
html_tag_optimized!(Blockquote, "Defines a section that is quoted from another source");
html_tag_optimized!(Canvas, "Used to draw graphics, on the fly, via scripting (usually JavaScript)");
html_tag_optimized!(Caption, "Defines a table caption");
html_tag_optimized!(Cite, "Defines the title of a work");
html_tag_optimized!(Col, "Specifies column properties for each column within a <colgroup> element");
html_tag_optimized!(Colgroup, "Specifies a group of one or more columns in a table for formatting");
html_tag_optimized!(Data, "Adds a machine-readable translation of a given content");
html_tag_optimized!(Datalist, "Specifies a list of pre-defined options for input controls");
html_tag_optimized!(Dd, "Defines a description/value of a term in a description list");
html_tag_optimized!(Del, "Defines text that has been deleted from a document");
html_tag_optimized!(Details, "Defines additional details that the user can view or hide");
html_tag_optimized!(Dfn, "Specifies a term that is going to be defined within the content");
html_tag_optimized!(Dialog, "Defines a dialog box or window");
html_tag_optimized!(Dl, "Defines a description list");
html_tag_optimized!(Dt, "Defines a term/name in a description list");
html_tag_optimized!(Embed, "Defines a container for an external application");
html_tag_optimized!(Fieldset, "Groups related elements in a form");
html_tag_optimized!(Figcaption, "Defines a caption for a <figure> element");
html_tag_optimized!(Figure, "Specifies self-contained content");
html_tag_optimized!(Hgroup, "Defines a header and related content");
html_tag_optimized!(Hr, "Defines a thematic change in the content");
html_tag_optimized!(Iframe, "Defines an inline frame");
html_tag_optimized!(Ins, "Defines a text that has been inserted into a document");
html_tag_optimized!(Kbd, "Defines keyboard input");
html_tag_optimized!(Legend, "Defines a caption for a <fieldset> element");
html_tag_optimized!(Map, "Defines an image map");
html_tag_optimized!(Mark, "Defines marked/highlighted text");
html_tag_optimized!(Menu, "Defines an unordered list");
html_tag_optimized!(Meta, "Defines metadata about an HTML document");
html_tag_optimized!(Meter, "Defines a scalar measurement within a known range (a gauge)");
html_tag_optimized!(Noscript, "Defines an alternate content for users that do not support client-side scripts");
html_tag_optimized!(Object, "Defines a container for an external application");
html_tag_optimized!(Optgroup, "Defines a group of related options in a drop-down list");
// Create OptionElement with proper tag name
#[pyfunction]
#[doc = "Defines an option in a drop-down list"]
#[pyo3(signature = (*children, **kwargs))]
#[inline(always)]
fn OptionElement(children: Vec<PyObject>, kwargs: std::option::Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<String> {
    create_tag_immediate("option", children, kwargs, py)
}

// Alias for compatibility with Air
#[pyfunction(name = "Option")]
#[doc = "Defines an option in a drop-down list"]
#[pyo3(signature = (*children, **kwargs))]
#[inline(always)]
fn option_tag_alias(children: Vec<PyObject>, kwargs: std::option::Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<String> {
    create_tag_immediate("option", children, kwargs, py)
}
html_tag_optimized!(Output, "Defines the result of a calculation");
html_tag_optimized!(Param, "Defines a parameter for an object");
html_tag_optimized!(Picture, "Defines a container for multiple image resources");
html_tag_optimized!(Pre, "Defines preformatted text");
html_tag_optimized!(Progress, "Represents the progress of a task");
html_tag_optimized!(Q, "Defines a short quotation");
html_tag_optimized!(Rp, "Defines what to show in browsers that do not support ruby annotations");
html_tag_optimized!(Rt, "Defines an explanation/pronunciation of characters (for East Asian typography)");
html_tag_optimized!(Ruby, "Defines a ruby annotation (for East Asian typography)");
html_tag_optimized!(S, "Defines text that is no longer correct");
html_tag_optimized!(Samp, "Defines sample output from a computer program");
html_tag_optimized!(Script, "Defines a client-side script");
html_tag_optimized!(Search, "Defines a search section");
html_tag_optimized!(Select, "Defines a drop-down list");
html_tag_optimized!(Small, "Defines smaller text");
html_tag_optimized!(Source, "Defines multiple media resources for media elements (<video> and <audio>)");
html_tag_optimized!(Style, "Defines style information for a document");
html_tag_optimized!(Sub, "Defines subscripted text");
html_tag_optimized!(Summary, "Defines a visible heading for a <details> element");
html_tag_optimized!(Sup, "Defines superscripted text");
html_tag_optimized!(Template, "Defines a container for content that should be hidden when the page loads");
html_tag_optimized!(Textarea, "Defines a multiline input control (text area)");
html_tag_optimized!(Tfoot, "Groups the footer content in a table");
html_tag_optimized!(Time, "Defines a specific time (or datetime)");
html_tag_optimized!(Track, "Defines text tracks for media elements (<video> and <audio>)");
html_tag_optimized!(U, "Defines some text that is unarticulated and styled differently from normal text");
html_tag_optimized!(Var, "Defines a variable");
html_tag_optimized!(Video, "Defines embedded video content");
html_tag_optimized!(Wbr, "Defines a possible line-break");

// Special optimized Html tag with automatic head/body separation
#[pyfunction]
#[doc = "Defines the HTML document"]
#[pyo3(signature = (*children, **kwargs))]
#[inline(always)]
fn Html(children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<String> {
    let attr_storage = if let Some(kwargs) = kwargs {
        let mut attrs = HashMap::default();
        for (key, value) in kwargs.iter() {
            let key_str = key.extract::<String>()?;
            let value_str = value.extract::<String>()?;
            attrs.insert(key_str, value_str);
        }
        AttributeStorage::from_hashmap(attrs)
    } else {
        AttributeStorage::Empty
    };
    
    // Separate head and body content using SmallVec for stack allocation
    let mut head_content: SmallVec<[PyObject; 4]> = smallvec![];
    let mut body_content: SmallVec<[PyObject; 8]> = smallvec![];
    
    for child_obj in children {
        // Check if this is a head-specific tag
        if likely(child_obj.extract::<PyRef<HtmlString>>(py).is_ok()) {
            let html_string = child_obj.extract::<PyRef<HtmlString>>(py).unwrap();
            let content = &html_string.content;
            
            // Check for head-specific tags using SIMD-accelerated memchr
            if memchr::memmem::find(content.as_bytes(), b"<title").is_some() ||
               memchr::memmem::find(content.as_bytes(), b"<link").is_some() ||
               memchr::memmem::find(content.as_bytes(), b"<meta").is_some() ||
               memchr::memmem::find(content.as_bytes(), b"<style").is_some() ||
               memchr::memmem::find(content.as_bytes(), b"<script").is_some() ||
               memchr::memmem::find(content.as_bytes(), b"<base").is_some() {
                head_content.push(child_obj);
            } else {
                body_content.push(child_obj);
            }
        } else {
            body_content.push(child_obj);
        }
    }
    
    // Process content efficiently
    let head_string = process_children_with_prefetch(&head_content, py)?;
    let body_string = process_children_with_prefetch(&body_content, py)?;
    let attr_string = attr_storage.build_string();
    
    // Build complete HTML structure
    let capacity = 67 + attr_string.len() + head_string.len() + body_string.len();
    let mut writer = HtmlWriter::new(capacity);
    
    writer.buffer.push_str("<!doctype html><html");
    writer.buffer.push_str(&attr_string);
    writer.buffer.push_str("><head>");
    writer.buffer.push_str(&head_string);
    writer.buffer.push_str("</head><body>");
    writer.buffer.push_str(&body_string);
    writer.buffer.push_str("</body></html>");
    
    // Return strings to pools
    return_to_pool(attr_string);
    return_to_pool(head_string);
    return_to_pool(body_string);
    
    Ok(writer.buffer)
}

// Backward-compatible Tag class (optimized)
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
        if likely(child_obj.extract::<PyRef<HtmlString>>(py).is_ok()) {
            return Ok(child_obj.extract::<PyRef<HtmlString>>(py).unwrap().content.clone());
        }
        if likely(child_obj.extract::<PyRef<Tag>>(py).is_ok()) {
            return child_obj.extract::<PyRef<Tag>>(py).unwrap().render(py);
        }
        if likely(child_obj.extract::<String>(py).is_ok()) {
            return Ok(child_obj.extract::<String>(py).unwrap());
        }
        if unlikely(child_obj.extract::<i64>(py).is_ok()) {
            let mut buffer = itoa::Buffer::new();
            return Ok(buffer.format(child_obj.extract::<i64>(py).unwrap()).to_string());
        }
        if unlikely(child_obj.extract::<f64>(py).is_ok()) {
            let mut buffer = ryu::Buffer::new();
            return Ok(buffer.format(child_obj.extract::<f64>(py).unwrap()).to_string());
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
        let attr_storage = AttributeStorage::from_hashmap(self._attrs.clone());
        attr_storage.build_string()
    }
    
    #[getter]
    fn children(&self, py: Python) -> PyResult<String> {
        process_children_with_prefetch(&self._children, py)
    }
    
    fn render(&self, py: Python) -> PyResult<String> {
        let name = self.name();
        let attrs = self.attrs();
        let children = self.children(py)?;
        
        let capacity = name.len() * 2 + attrs.len() + children.len() + 5;
        let mut result = get_pooled_string(capacity);
        
        result.push('<');
        result.push_str(&name);
        result.push_str(&attrs);
        result.push('>');
        result.push_str(&children);
        result.push_str("</");
        result.push_str(&name);
        result.push('>');
        
        Ok(result)
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

// =============================================================================
// PYTHON MODULE DEFINITION
// =============================================================================

#[pymodule]
fn rusty_tags(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core classes
    m.add_class::<HtmlString>()?;
    m.add_class::<Tag>()?;
    
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
    m.add_function(wrap_pyfunction!(Footer, m)?)?;
    m.add_function(wrap_pyfunction!(Thead, m)?)?;
    m.add_function(wrap_pyfunction!(Tbody, m)?)?;
    
    // Additional HTML tags for full Air compatibility
    m.add_function(wrap_pyfunction!(Abbr, m)?)?;
    m.add_function(wrap_pyfunction!(Address, m)?)?;
    m.add_function(wrap_pyfunction!(Area, m)?)?;
    m.add_function(wrap_pyfunction!(Article, m)?)?;
    m.add_function(wrap_pyfunction!(Audio, m)?)?;
    m.add_function(wrap_pyfunction!(Base, m)?)?;
    m.add_function(wrap_pyfunction!(Bdi, m)?)?;
    m.add_function(wrap_pyfunction!(Bdo, m)?)?;
    m.add_function(wrap_pyfunction!(Blockquote, m)?)?;
    m.add_function(wrap_pyfunction!(Canvas, m)?)?;
    m.add_function(wrap_pyfunction!(Caption, m)?)?;
    m.add_function(wrap_pyfunction!(Cite, m)?)?;
    m.add_function(wrap_pyfunction!(Col, m)?)?;
    m.add_function(wrap_pyfunction!(Colgroup, m)?)?;
    m.add_function(wrap_pyfunction!(Data, m)?)?;
    m.add_function(wrap_pyfunction!(Datalist, m)?)?;
    m.add_function(wrap_pyfunction!(Dd, m)?)?;
    m.add_function(wrap_pyfunction!(Del, m)?)?;
    m.add_function(wrap_pyfunction!(Details, m)?)?;
    m.add_function(wrap_pyfunction!(Dfn, m)?)?;
    m.add_function(wrap_pyfunction!(Dialog, m)?)?;
    m.add_function(wrap_pyfunction!(Dl, m)?)?;
    m.add_function(wrap_pyfunction!(Dt, m)?)?;
    m.add_function(wrap_pyfunction!(Embed, m)?)?;
    m.add_function(wrap_pyfunction!(Fieldset, m)?)?;
    m.add_function(wrap_pyfunction!(Figcaption, m)?)?;
    m.add_function(wrap_pyfunction!(Figure, m)?)?;
    m.add_function(wrap_pyfunction!(Hgroup, m)?)?;
    m.add_function(wrap_pyfunction!(Hr, m)?)?;
    m.add_function(wrap_pyfunction!(Iframe, m)?)?;
    m.add_function(wrap_pyfunction!(Ins, m)?)?;
    m.add_function(wrap_pyfunction!(Kbd, m)?)?;
    m.add_function(wrap_pyfunction!(Legend, m)?)?;
    m.add_function(wrap_pyfunction!(Map, m)?)?;
    m.add_function(wrap_pyfunction!(Mark, m)?)?;
    m.add_function(wrap_pyfunction!(Menu, m)?)?;
    m.add_function(wrap_pyfunction!(Meta, m)?)?;
    m.add_function(wrap_pyfunction!(Meter, m)?)?;
    m.add_function(wrap_pyfunction!(Noscript, m)?)?;
    m.add_function(wrap_pyfunction!(Object, m)?)?;
    m.add_function(wrap_pyfunction!(Optgroup, m)?)?;
    m.add_function(wrap_pyfunction!(OptionElement, m)?)?;
    m.add_function(wrap_pyfunction!(option_tag_alias, m)?)?;
    m.add_function(wrap_pyfunction!(Output, m)?)?;
    m.add_function(wrap_pyfunction!(Param, m)?)?;
    m.add_function(wrap_pyfunction!(Picture, m)?)?;
    m.add_function(wrap_pyfunction!(Pre, m)?)?;
    m.add_function(wrap_pyfunction!(Progress, m)?)?;
    m.add_function(wrap_pyfunction!(Q, m)?)?;
    m.add_function(wrap_pyfunction!(Rp, m)?)?;
    m.add_function(wrap_pyfunction!(Rt, m)?)?;
    m.add_function(wrap_pyfunction!(Ruby, m)?)?;
    m.add_function(wrap_pyfunction!(S, m)?)?;
    m.add_function(wrap_pyfunction!(Samp, m)?)?;
    m.add_function(wrap_pyfunction!(Script, m)?)?;
    m.add_function(wrap_pyfunction!(Search, m)?)?;
    m.add_function(wrap_pyfunction!(Select, m)?)?;
    m.add_function(wrap_pyfunction!(Small, m)?)?;
    m.add_function(wrap_pyfunction!(Source, m)?)?;
    m.add_function(wrap_pyfunction!(Style, m)?)?;
    m.add_function(wrap_pyfunction!(Sub, m)?)?;
    m.add_function(wrap_pyfunction!(Summary, m)?)?;
    m.add_function(wrap_pyfunction!(Sup, m)?)?;
    m.add_function(wrap_pyfunction!(Template, m)?)?;
    m.add_function(wrap_pyfunction!(Textarea, m)?)?;
    m.add_function(wrap_pyfunction!(Tfoot, m)?)?;
    m.add_function(wrap_pyfunction!(Time, m)?)?;
    m.add_function(wrap_pyfunction!(Track, m)?)?;
    m.add_function(wrap_pyfunction!(U, m)?)?;
    m.add_function(wrap_pyfunction!(Var, m)?)?;
    m.add_function(wrap_pyfunction!(Video, m)?)?;
    m.add_function(wrap_pyfunction!(Wbr, m)?)?;
    
    // Specialized optimization functions
    m.add_function(wrap_pyfunction!(render_list_optimized, m)?)?;
    m.add_function(wrap_pyfunction!(render_table_optimized, m)?)?;
    
    Ok(())
}