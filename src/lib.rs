use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};
use ahash::AHashMap as HashMap;
use smallvec::{SmallVec, smallvec};
use dashmap::DashMap;
use once_cell::sync::Lazy;
use std::borrow::Cow;
use std::cell::RefCell;
use std::sync::atomic::{AtomicUsize, Ordering};
use bumpalo::Bump;
use serde::{Deserialize, Serialize};
use serde_json;
use pythonize;
use scraper::{Html as HtmlParser, Node, ElementRef};

/// Escape HTML special characters to prevent XSS and allow displaying HTML as text
/// Converts: < > & " '
#[inline]
fn html_escape(text: &str) -> String {
    let mut result = String::with_capacity(text.len() + (text.len() / 8));
    for c in text.chars() {
        match c {
            '<' => result.push_str("&lt;"),
            '>' => result.push_str("&gt;"),
            '&' => result.push_str("&amp;"),
            '"' => result.push_str("&quot;"),
            '\'' => result.push_str("&#x27;"),
            _ => result.push(c),
        }
    }
    result
}

/// Convert JSON string from double quotes to single quotes for HTML attributes
#[inline]
fn json_to_html_attr(json_str: &str) -> String {
    // Replace double quotes with single quotes for JSON string values
    // This is safe because we're only converting valid JSON
    json_str.replace('"', "'")
}

// =============================================================================
// DATASTAR INTEGRATION - CORE TYPE SYSTEM
// =============================================================================

/// Represents different types of values for Datastar attributes
/// Optimized for performance with intelligent JavaScript type handling
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DatastarValue {
    /// JavaScript expression (no quotes, direct output) - $signal, @action
    Expression(String),
    
    /// JSON for objects/arrays - will be serialized as-is
    Json(String),
    
    /// JavaScript string literal - will be quoted: 'value'
    String(String),
    
    /// JavaScript number - direct output: 42, 3.14
    Number(f64),
    
    /// JavaScript boolean - direct output: true/false
    Boolean(bool),
    
    /// JavaScript null
    Null,
    
    /// Raw HTML (won't be escaped) - for advanced use cases
    Raw(String),
}

impl DatastarValue {
    /// Convert a Python value to a DatastarValue with intelligent type detection
    #[inline]
    pub fn from_python(py_value: &Bound<'_, pyo3::PyAny>) -> PyResult<Self> {
        // Handle None/null first
        if py_value.is_none() {
            return Ok(DatastarValue::Null);
        }
        
        // Fast path for booleans (check before numbers since bool can be extracted as int)
        if let Ok(b) = py_value.extract::<bool>() {
            return Ok(DatastarValue::Boolean(b));
        }
        
        // Fast path for numbers
        if let Ok(i) = py_value.extract::<i64>() {
            return Ok(DatastarValue::Number(i as f64));
        }
        if let Ok(f) = py_value.extract::<f64>() {
            return Ok(DatastarValue::Number(f));
        }
        
        // Handle strings with Datastar expression detection
        if let Ok(s) = py_value.extract::<String>() {
            // Detect Datastar expressions by common patterns
            if s.starts_with('$') ||           // $signal
               s.starts_with('@') ||           // @action
               s.contains("$") ||              // Contains signal references
               s.contains("@") ||              // Contains action references
               s.starts_with("new ") ||        // JavaScript constructors
               s.contains("()") ||             // Function calls (no params)
               s.contains("(") ||              // Function calls (with params)
               s.contains("===") ||            // Strict equality
               s.contains("!==") ||            // Strict inequality
               s.contains("&&") ||             // Logical AND
               s.contains("||") ||             // Logical OR
               s.contains("Date.") ||          // Date methods
               s.contains(".length") ||        // Array/string length
               s.contains(".push(") ||         // Array methods
               s.contains(".pop(") ||
               s.contains(".splice(") ||
               s.contains("window.") ||        // Browser globals
               s.contains("document.") {       // DOM access
                return Ok(DatastarValue::Expression(s));
            } else {
                return Ok(DatastarValue::String(s));
            }
        }
        
        // Handle dictionaries and lists as JSON
        if py_value.is_instance_of::<PyDict>() || py_value.is_instance_of::<PyList>() {
            // Convert Python object to serde_json::Value for serialization
            let json_value: serde_json::Value = pythonize::depythonize(py_value)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Failed to convert Python object to JSON: {}", e)
                ))?;
            let json_string = serde_json::to_string(&json_value)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Failed to serialize to JSON: {}", e)
                ))?;
            return Ok(DatastarValue::Json(json_to_html_attr(&json_string)));
        }
        
        // Final fallback - convert to string
        if let Ok(str_result) = py_value.str() {
            if let Ok(str_value) = str_result.extract::<String>() {
                return Ok(DatastarValue::String(str_value));
            }
        }
        
        // Error case
        let value_type = py_value.get_type().name()?;
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            format!("Cannot convert {} to DatastarValue", value_type)
        ))
    }
    
    /// Convert to HTML attribute value with proper JavaScript formatting
    #[inline]
    pub fn to_html_attr(&self) -> String {
        match self {
            DatastarValue::Expression(expr) => expr.clone(),
            DatastarValue::String(s) => {
                // Return string as-is, no escaping needed since HTML attributes use double quotes
                s.clone()
            },
            DatastarValue::Boolean(b) => b.to_string(),
            DatastarValue::Number(n) => {
                // Use optimized number formatting
                if n.fract() == 0.0 && *n >= i64::MIN as f64 && *n <= i64::MAX as f64 {
                    // Integer path using itoa for speed
                    let mut buffer = itoa::Buffer::new();
                    buffer.format(*n as i64).to_string()
                } else {
                    // Float path using ryu for speed
                    let mut buffer = ryu::Buffer::new();
                    buffer.format(*n).to_string()
                }
            },
            DatastarValue::Json(json) => json.clone(),
            DatastarValue::Null => "null".to_string(),
            DatastarValue::Raw(raw) => raw.clone(),
        }
    }
    
    /// Get memory footprint for capacity planning
    #[inline]
    pub fn memory_size(&self) -> usize {
        match self {
            DatastarValue::Expression(s) => s.len(),
            DatastarValue::String(s) => s.len() + 2, // +2 for quotes
            DatastarValue::Json(s) => s.len(),
            DatastarValue::Raw(s) => s.len(),
            DatastarValue::Boolean(_) => 5, // "false".len()
            DatastarValue::Number(_) => 16, // Conservative estimate
            DatastarValue::Null => 4, // "null".len()
        }
    }
}

// Thread-local cache for Datastar transformations
thread_local! {
    static DATASTAR_ATTR_CACHE: RefCell<HashMap<String, (String, DatastarValue)>> = 
        RefCell::new(HashMap::with_capacity(128));
}

// =============================================================================
// DATASTAR ATTRIBUTE HANDLER SYSTEM
// =============================================================================

/// Trait for handling different types of Datastar attributes
pub trait DatastarHandler {
    /// Check if this handler can process the given attribute key
    fn can_handle(&self, key: &str) -> bool;
    
    /// Process the attribute key and Python value into a data-* attribute
    fn process(&self, key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)>;
    
    /// Priority for handler ordering (higher = more specific, checked first)
    fn priority(&self) -> u8;
}

/// Handler for ds_signals attribute - converts to data-signals JSON
pub struct SignalsHandler;

impl DatastarHandler for SignalsHandler {
    #[inline]
    fn can_handle(&self, key: &str) -> bool {
        key == "ds_signals"
    }
    
    #[inline]
    fn process(&self, _key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        let datastar_value = DatastarValue::from_python(value)?;
        
        // For signals, we always want JSON format regardless of input type
        let json_value = match datastar_value {
            DatastarValue::Json(json) => json,
            DatastarValue::String(s) => {
                // Parse string as JSON if possible, otherwise create simple object
                json_to_html_attr(&serde_json::to_string(&serde_json::json!({ "value": s }))
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Failed to create signals JSON: {}", e)
                    ))?)
            },
            other => {
                // Convert other types to JSON
                let json_str = other.to_html_attr();
                json_to_html_attr(&serde_json::to_string(&serde_json::json!({ "value": json_str }))
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Failed to create signals JSON: {}", e)
                    ))?)
            }
        };
        
        Ok(("data-signals".to_string(), DatastarValue::Json(json_value)))
    }
    
    #[inline]
    fn priority(&self) -> u8 { 100 }
}

/// Handler for general ds_on_* event attributes
pub struct EventHandler;

impl DatastarHandler for EventHandler {
    #[inline]
    fn can_handle(&self, key: &str) -> bool {
        key.starts_with("ds_on_")
    }
    
    #[inline]
    fn process(&self, key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        let event_part = &key[6..]; // Remove "ds_on_"
        let data_key = transform_event_key(event_part);
        let datastar_value = DatastarValue::from_python(value)?;
        
        // Events should typically be expressions, but we'll preserve the detected type
        Ok((data_key, datastar_value))
    }
    
    #[inline]
    fn priority(&self) -> u8 { 80 }
}

/// Handler for reactive class binding (ds_cls)
pub struct ClassHandler;

impl DatastarHandler for ClassHandler {
    #[inline]
    fn can_handle(&self, key: &str) -> bool {
        key == "ds_cls"
    }
    
    #[inline]
    fn process(&self, _key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        let datastar_value = DatastarValue::from_python(value)?;
        
        // Class bindings should be JSON objects
        let json_value = match datastar_value {
            DatastarValue::Json(json) => json,
            other => {
                // Convert to JSON format
                json_to_html_attr(&serde_json::to_string(&serde_json::json!({ "default": other.to_html_attr() }))
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Failed to create class binding JSON: {}", e)
                    ))?)
            }
        };
        
        Ok(("data-class".to_string(), DatastarValue::Json(json_value)))
    }
    
    #[inline]
    fn priority(&self) -> u8 { 95 }
}

/// Handler for data-bind attribute - strips leading $ from signal references
/// data-bind requires signal names without the $ prefix
pub struct BindHandler;

impl DatastarHandler for BindHandler {
    #[inline]
    fn can_handle(&self, key: &str) -> bool {
        key == "ds_bind"
    }
    
    #[inline]
    fn process(&self, _key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        let mut datastar_value = DatastarValue::from_python(value)?;
        
        // Strip leading $ from bind values since data-bind uses signal names without $
        datastar_value = match datastar_value {
            DatastarValue::Expression(s) if s.starts_with('$') => {
                // Remove the $ prefix for bind attributes
                DatastarValue::Expression(s[1..].to_string())
            },
            DatastarValue::String(s) if s.starts_with('$') => {
                // Also handle string values that look like signal references
                DatastarValue::Expression(s[1..].to_string())
            },
            other => other,
        };
        
        Ok(("data-bind".to_string(), datastar_value))
    }
    
    #[inline]
    fn priority(&self) -> u8 { 90 }
}

/// Handler for data-on-keys plugin (keyboard shortcuts)
///
/// Transforms on_keys_* attributes to data-on-keys:* format.
/// This plugin uses a different format than standard events:
/// - on_keys_ctrl_k -> data-on-keys:ctrl-k (NOT data-on:keys-ctrl-k)
/// - on_keys_enter__el -> data-on-keys:enter__el
/// - on_keys -> data-on-keys (captures all keys)
pub struct KeysEventHandler;

impl DatastarHandler for KeysEventHandler {
    #[inline]
    fn can_handle(&self, key: &str) -> bool {
        key == "ds_on_keys" || key.starts_with("ds_on_keys_")
    }

    #[inline]
    fn process(&self, key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        let datastar_value = DatastarValue::from_python(value)?;

        // Handle bare "on_keys" (no key spec - captures all keys)
        if key == "ds_on_keys" {
            return Ok(("data-on-keys".to_string(), datastar_value));
        }

        // Extract part after "ds_on_keys_"
        let key_part = &key[11..]; // e.g., "ctrl_k" or "enter__el__throttle_1s"

        let data_key = transform_keys_event(key_part);
        Ok((data_key, datastar_value))
    }

    #[inline]
    fn priority(&self) -> u8 { 85 } // Higher than EventHandler (80)
}

/// Default fallback handler for any ds_* attribute
/// 
/// Handles keyed plugins with colon syntax (data-plugin:key) and
/// non-keyed plugins with hyphen syntax (data-plugin)
pub struct DefaultDatastarHandler;

/// Plugins that use keyed syntax with colon separator
/// e.g., ds_attr_title -> data-attr:title
const KEYED_PLUGINS: &[&str] = &["attr", "class", "bind", "signals", "computed", "style"];

impl DatastarHandler for DefaultDatastarHandler {
    #[inline]
    fn can_handle(&self, key: &str) -> bool {
        key.starts_with("ds_")
    }
    
    #[inline]
    fn process(&self, key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        let without_ds = &key[3..]; // Remove "ds_"
        let data_key = transform_ds_key(without_ds);
        let datastar_value = DatastarValue::from_python(value)?;
        Ok((data_key, datastar_value))
    }
    
    #[inline]
    fn priority(&self) -> u8 { 1 }
}

/// Transform a ds_ key to the appropriate data-* attribute
/// 
/// For keyed plugins (attr, class, bind, signals, computed, style):
///   ds_attr_title -> data-attr:title
///   ds_computed_my_signal -> data-computed:my-signal
/// 
/// For non-keyed plugins:
///   ds_text -> data-text
///   ds_show -> data-show
#[inline]
fn transform_ds_key(key_without_ds: &str) -> String {
    // Check if this starts with a keyed plugin prefix
    for plugin in KEYED_PLUGINS {
        let prefix = format!("{}_", plugin);
        if key_without_ds.starts_with(&prefix) {
            // Extract the key part after the plugin name
            let key_part = &key_without_ds[prefix.len()..];
            // Convert underscores to hyphens in the key part
            let transformed_key = key_part.replace('_', "-");
            return format!("data-{}:{}", plugin, transformed_key);
        }
    }
    
    // Non-keyed plugin - just convert underscores to hyphens
    format!("data-{}", key_without_ds.replace('_', "-"))
}

/// Event key transformation with intelligent pattern detection
/// 
/// Transforms event keys according to Datastar specification:
/// - Colon separates the plugin name from the event name
/// - First __ separates base event from modifiers
/// - In modifier section: __ stays as __ (separates modifiers), _ becomes . (within modifier)
/// 
/// Examples:
/// - on_click__debounce_500ms -> data-on:click__debounce.500ms
/// - on_click__window__throttle_1s -> data-on:click__window__throttle.1s
/// - on_resize__throttle_500ms__noleading -> data-on:resize__throttle.500ms__noleading
#[inline]
fn transform_event_key(event_part: &str) -> String {
    // Handle modifiers (after first __)
    if let Some(double_pos) = event_part.find("__") {
        let base_event = &event_part[..double_pos];
        let modifier_part = &event_part[double_pos + 2..]; // Skip the first __
        
        // In modifier section:
        // - Keep __ as __ (separator between modifiers)
        // - Convert single _ to . (separator within modifier values)
        
        // Use placeholder to preserve __
        let modifier = modifier_part
            .replace("__", "§§")       // Protect __ temporarily
            .replace('_', ".")          // Convert single _ to .
            .replace("§§", "__");       // Restore __
        
        return format!("data-on:{}__{}",
            base_event.replace('_', "-"),  // Event name: _ becomes -
            modifier
        );
    }
    
    // No modifiers - just convert underscores to hyphens
    format!("data-on:{}", event_part.replace('_', "-"))
}

/// Transform key event key for the data-on-keys plugin
///
/// This handles the special syntax for the on-keys plugin where:
/// - on_keys_ctrl_k -> data-on-keys:ctrl-k
/// - on_keys_enter__el -> data-on-keys:enter__el
/// - on_keys_space__throttle_1s -> data-on-keys:space__throttle.1s
#[inline]
fn transform_keys_event(key_part: &str) -> String {
    // Handle modifiers (after first __)
    if let Some(double_pos) = key_part.find("__") {
        let key_spec = &key_part[..double_pos];
        let modifier_part = &key_part[double_pos + 2..]; // Skip the first __

        // Key spec: _ becomes -
        let transformed_key = key_spec.replace('_', "-");

        // Modifier part: same rules as other events
        // - Keep __ as __ (separator between modifiers)
        // - Convert single _ to . (separator within modifier values)
        let modifier = modifier_part
            .replace("__", "\x00\x00")  // Protect __ temporarily
            .replace('_', ".")          // Convert single _ to .
            .replace("\x00\x00", "__"); // Restore __

        format!("data-on-keys:{}__{}", transformed_key, modifier)
    } else {
        // No modifiers - just convert underscores to hyphens in key spec
        format!("data-on-keys:{}", key_part.replace('_', "-"))
    }
}

/// Map shorthand attribute names to their ds_ equivalents
/// Returns Some(mapped_name) if it's a shorthand attribute, None otherwise
#[inline]
fn map_shorthand_attribute(key: &str) -> Option<String> {
    match key {
        // Core Datastar attributes (most commonly used)
        "signals" => Some("ds_signals".to_string()),
        "bind" => Some("ds_bind".to_string()),
        "data_bind" => Some("ds_bind".to_string()),  // Also map data_bind for consistency
        "show" => Some("ds_show".to_string()),
        "text" => Some("ds_text".to_string()),
        "attrs" => Some("ds_attr".to_string()),
        "data_style" => Some("ds_style".to_string()),
        
        // Common attributes
        "effect" => Some("ds_effect".to_string()),
        "computed" => Some("ds_computed".to_string()),
        "ref" => Some("ds_ref".to_string()),
        "indicator" => Some("ds_indicator".to_string()),
        
        // Event attributes - generic support for any on_* event
        key if key.starts_with("on_") => {
            Some(format!("ds_{}", key))
        },
        
        // Pro/Advanced attributes (lower priority but included for completeness)
        "persist" => Some("ds_persist".to_string()),
        "query_string" => Some("ds_query_string".to_string()),
        "replace_url" => Some("ds_replace_url".to_string()),
        "scroll_into_view" => Some("ds_scroll_into_view".to_string()),
        "view_transition" => Some("ds_view_transition".to_string()),
        "animate" => Some("ds_animate".to_string()),
        "custom_validity" => Some("ds_custom_validity".to_string()),
        "on_raf" => Some("ds_on_raf".to_string()),
        "on_resize" => Some("ds_on_resize".to_string()),
        "on_load" => Some("ds_on_load".to_string()),
        "on_intersect" => Some("ds_on_intersect".to_string()),
        "on_interval" => Some("ds_on_interval".to_string()),
        "on_signal_patch" => Some("ds_on_signal_patch".to_string()),
        "on_signal_patch_filter" => Some("ds_on_signal_patch_filter".to_string()),
        "ignore" => Some("ds_ignore".to_string()),
        "ignore_morph" => Some("ds_ignore_morph".to_string()),
        "preserve_attr" => Some("ds_preserve_attr".to_string()),
        "json_signals" => Some("ds_json_signals".to_string()),
        
        // Not a shorthand attribute
        _ => None,
    }
}

/// Context for processing attribute key-value pairs
#[derive(Debug, Clone, Copy, PartialEq)]
enum AttributeContext {
    /// Processing keyword arguments (kwargs) - should not expand mappings for datastar attrs
    Kwargs,
    /// Processing positional dict children - should expand mappings as individual attributes
    PositionalDict,
}

/// Process a single attribute key-value pair, handling shorthand attributes and Mapping expansion
#[inline]
fn process_attribute_key_value(
    key_str: &str,
    value: &Bound<'_, pyo3::PyAny>,
    processor: &DatastarProcessor,
    attrs: &mut HashMap<String, String>,
    datastar_attrs: &mut HashMap<String, DatastarValue>,
    context: AttributeContext,
    py: Python,
) -> PyResult<()> {
    // First check if the value is a Mapping and should be expanded
    // Only expand mappings when processing positional dict children, not kwargs
    if context == AttributeContext::PositionalDict {
        // Check if it's a PyDict specifically, as that's the most common case
        if value.is_instance_of::<PyDict>() && !key_str.starts_with("ds_") && key_str != "cls" {
            let dict = value.downcast::<PyDict>()?;
            // Expand the mapping as individual attributes
            for (map_key, map_value) in dict.iter() {
                let map_key_str = map_key.extract::<String>()?;
                // Recursively process each key-value pair from the mapping
                process_attribute_key_value(&map_key_str, &map_value, processor, attrs, datastar_attrs, context, py)?;
            }
            return Ok(());
        }
        // For other mapping-like objects, try to check for items() method
        else if !key_str.starts_with("ds_") && key_str != "cls" {
            if let Ok(items) = value.call_method0("items") {
                if let Ok(items_list) = items.downcast::<PyList>() {
                    for item in items_list.iter() {
                        // Extract key-value pair from tuple
                        if let Ok(tuple) = item.extract::<(String, PyObject)>() {
                            let (map_key_str, map_value) = tuple;
                            let map_value_bound = map_value.bind(py);
                            process_attribute_key_value(&map_key_str, map_value_bound, processor, attrs, datastar_attrs, context, py)?;
                        }
                    }
                    return Ok(());
                }
            }
        }
    }
    
    // Original attribute processing logic
    // Check if it's a shorthand attribute first
    if let Some(mapped_key) = map_shorthand_attribute(key_str) {
        // It's a shorthand attribute - process as Datastar
        let (data_key, data_value) = processor.process(&mapped_key, value)?;
        datastar_attrs.insert(data_key, data_value);
    } else if key_str.starts_with("ds_") {
        // Direct Datastar attribute
        let (data_key, data_value) = processor.process(key_str, value)?;
        datastar_attrs.insert(data_key, data_value);
    } else if key_str == "cls" {
        // Handle special case of reactive vs static class
        if value.is_instance_of::<PyDict>() {
            // Reactive class binding -> ds_cls
            let (data_key, data_value) = processor.process("ds_cls", value)?;
            datastar_attrs.insert(data_key, data_value);
        } else {
            // Regular HTML class
            if let Some(value_str) = convert_attribute_value(value, py)? {
                attrs.insert("class".to_string(), value_str);
            }
        }
    } else {
        // Regular HTML attribute
        if let Some(value_str) = convert_attribute_value(value, py)? {
            attrs.insert(key_str.to_string(), value_str);
        }
    }
    
    Ok(())
}

/// Datastar processor with handler registry and caching
pub struct DatastarProcessor {
    handlers: Vec<Box<dyn DatastarHandler>>,
}

impl DatastarProcessor {
    /// Create a new processor with all default handlers
    pub fn new() -> Self {
        let mut handlers: Vec<Box<dyn DatastarHandler>> = vec![
            Box::new(SignalsHandler),
            Box::new(ClassHandler),
            Box::new(BindHandler), // Handle data-bind attribute (strips $)
            Box::new(KeysEventHandler), // Handle data-on-keys plugin (priority 85)
            Box::new(EventHandler), // Generic event handler with modifier support
            Box::new(DefaultDatastarHandler), // Fallback handler (lowest priority)
        ];
        
        // Sort by priority (highest first)
        handlers.sort_by(|a, b| b.priority().cmp(&a.priority()));
        
        Self { handlers }
    }
    
    /// Process a ds_* attribute through the handler system with caching
    #[inline]
    pub fn process(&self, key: &str, value: &Bound<'_, pyo3::PyAny>) -> PyResult<(String, DatastarValue)> {
        // Create a more comprehensive cache key that includes actual content
        let value_str = if let Ok(s) = value.extract::<String>() {
            // For strings, include the actual string content
            format!("{}:str:{}", key, s)
        } else if value.is_instance_of::<pyo3::types::PyDict>() || value.is_instance_of::<pyo3::types::PyList>() {
            // For complex objects, use their string representation to ensure uniqueness
            if let Ok(repr) = value.repr() {
                if let Ok(repr_str) = repr.extract::<String>() {
                    format!("{}:complex:{}", key, repr_str)
                } else {
                    // Fallback: use hash of the object
                    format!("{}:complex:hash:{}", key, value.as_ptr() as usize)
                }
            } else {
                // Fallback: use hash of the object
                format!("{}:complex:hash:{}", key, value.as_ptr() as usize)
            }
        } else {
            // For other types, try to get a string representation
            if let Ok(str_result) = value.str() {
                if let Ok(str_value) = str_result.extract::<String>() {
                    format!("{}:{}:{}", key, value.get_type().name()?, str_value)
                } else {
                    format!("{}:{}:hash:{}", key, value.get_type().name()?, value.as_ptr() as usize)
                }
            } else {
                format!("{}:{}:hash:{}", key, value.get_type().name()?, value.as_ptr() as usize)
            }
        };
        
        // For complex objects, disable caching to ensure fresh processing
        // This prevents the issue where different complex objects get the same cached result
        let should_cache = !value.is_instance_of::<pyo3::types::PyDict>() && 
                          !value.is_instance_of::<pyo3::types::PyList>();
        
        if should_cache {
            if let Some(cached) = DATASTAR_ATTR_CACHE.with(|cache| {
                cache.borrow().get(&value_str).cloned()
            }) {
                return Ok(cached);
            }
        }
        
        // Find appropriate handler
        for handler in &self.handlers {
            if handler.can_handle(key) {
                let result = handler.process(key, value)?;
                
                // Cache the result only for simple types
                if should_cache {
                    DATASTAR_ATTR_CACHE.with(|cache| {
                        let mut cache_ref = cache.borrow_mut();
                        if cache_ref.len() < 256 { // Prevent unbounded growth
                            cache_ref.insert(value_str, result.clone());
                        }
                    });
                }
                
                return Ok(result);
            }
        }
        
        // Should never reach here due to DefaultDatastarHandler
        Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("No handler found for Datastar attribute: {}", key)
        ))
    }
}

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
// Returns None for false booleans (omit attribute), Some(String) otherwise
#[inline(always)]
fn convert_attribute_value(value_obj: &Bound<'_, pyo3::PyAny>, _py: Python) -> PyResult<Option<String>> {
    // Fast path for strings
    if let Ok(s) = value_obj.extract::<String>() {
        return Ok(Some(s));
    }
    
    // Fast path for booleans - check first since bool can be extracted as int
    // HTML5 boolean attributes: true = present, false = omitted
    if let Ok(b) = value_obj.extract::<bool>() {
        return Ok(if b { Some(String::new()) } else { None });
    }
    
    // Fast path for integers
    if let Ok(i) = value_obj.extract::<i64>() {
        let mut buffer = itoa::Buffer::new();
        return Ok(Some(buffer.format(i).to_string()));
    }
    
    // Fast path for floats
    if let Ok(f) = value_obj.extract::<f64>() {
        let mut buffer = ryu::Buffer::new();
        return Ok(Some(buffer.format(f).to_string()));
    }
    
    // Try to convert to string using __str__
    if let Ok(str_result) = value_obj.str() {
        if let Ok(str_value) = str_result.extract::<String>() {
            return Ok(Some(str_value));
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
    // Fast path for None - return empty string to ignore it
    if child_obj.bind(py).is_none() {
        return Ok(String::new());
    }
    
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
                // First try HtmlString
                if let Ok(html_string) = html_result.extract::<PyRef<HtmlString>>() {
                    return Ok(html_string.content.clone());
                }
                // Then try String
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
                // First try HtmlString
                if let Ok(html_string) = html_result.extract::<PyRef<HtmlString>>() {
                    return Ok(html_string.content.clone());
                }
                // Then try String
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
                // First try HtmlString
                if let Ok(html_string) = render_result.extract::<PyRef<HtmlString>>() {
                    return Ok(html_string.content.clone());
                }
                // Then try String
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
    // Special case for OptionEl -> option
    if tag_name == "OptionEl" {
        return "option".to_string();
    }
    
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
        
        // For boolean attributes (empty value), don't add ="value"
        if v.is_empty() {
            result.push(' ');
        } else {
            result.push_str("=\"");
            result.push_str(v);
            result.push_str("\" ");
        }
    }
    
    // Remove trailing space
    result.pop();
    result
}

// Enhanced attribute building with Datastar support
#[inline(always)]
fn build_attributes_with_datastar(
    attrs: &HashMap<String, String>,
    datastar_attrs: &HashMap<String, DatastarValue>
) -> String {
    if attrs.is_empty() && datastar_attrs.is_empty() {
        return String::new();
    }
    
    // Pre-calculate exact capacity needed
    let regular_capacity: usize = attrs.iter()
        .map(|(k, v)| {
            let mapped_key_len = attrmap_optimized(k).len();
            mapped_key_len + v.len() + 4 // +4 for =" " and quote
        })
        .sum::<usize>();
    
    let datastar_capacity: usize = datastar_attrs.iter()
        .map(|(k, v)| k.len() + v.memory_size() + 4) // +4 for =" " and quote
        .sum::<usize>();
    
    let total_capacity = regular_capacity + datastar_capacity + 1; // +1 for leading space
    let mut result = get_pooled_string(total_capacity);
    result.push(' ');
    
    // Process regular attributes first
    for (k, v) in attrs {
        let mapped_key = attrmap_optimized(k);
        result.push_str(&mapped_key);
        
        // For boolean attributes (empty value), don't add ="value"
        if v.is_empty() {
            result.push(' ');
        } else {
            result.push_str("=\"");
            result.push_str(v);
            result.push_str("\" ");
        }
    }
    
    // Process Datastar attributes
    for (k, v) in datastar_attrs {
        result.push_str(k);
        result.push_str("=\"");
        result.push_str(&v.to_html_attr());
        result.push_str("\" ");
    }
    
    // Remove trailing space
    result.pop();
    result
}

// =============================================================================
// HTML PARSING SYSTEM - HtmlElement for DOM manipulation
// =============================================================================

/// Represents a parsed HTML element with mutable attributes and children
/// This enables post-creation inspection and modification of HTML structures
#[pyclass(module = "rusty_tags.core")]
pub struct HtmlElement {
    /// Element tag name (e.g., "div", "input")
    #[pyo3(get, set)]
    pub tag: String,

    /// Mutable attribute dictionary
    #[pyo3(get, set)]
    pub attributes: Py<PyDict>,

    /// Mixed list of children - can contain HtmlElement objects or text strings
    #[pyo3(get, set)]
    pub children: Vec<PyObject>,

    /// Flag to distinguish text nodes from element nodes
    #[pyo3(get, set)]
    pub is_text: bool,
}

#[pymethods]
impl HtmlElement {
    #[new]
    #[pyo3(signature = (tag = String::new(), attributes = None, children = None, is_text = false))]
    fn new(
        tag: String,
        attributes: Option<Py<PyDict>>,
        children: Option<Vec<PyObject>>,
        is_text: bool,
        py: Python,
    ) -> PyResult<Self> {
        let attributes = attributes.unwrap_or_else(|| PyDict::new(py).unbind());
        let children = children.unwrap_or_default();

        Ok(HtmlElement {
            tag,
            attributes,
            children,
            is_text,
        })
    }

    /// Recursively serialize the element tree back to HTML string
    fn to_html(&self, py: Python) -> PyResult<Py<HtmlString>> {
        let html_content = self.serialize_to_html(py)?;
        let html_string = HtmlString::new(html_content);
        Py::new(py, html_string)
    }

    /// Implement __html__ protocol so HtmlElement can be used directly as a child
    /// This allows: Div(parsed_element) to work seamlessly
    fn __html__(&self, py: Python) -> PyResult<Py<HtmlString>> {
        self.to_html(py)
    }

    fn __repr__(&self, py: Python) -> PyResult<String> {
        if self.is_text {
            Ok(format!("HtmlElement(text={})", &self.tag))
        } else {
            let attrs_repr = self.attributes.bind(py).repr()?.to_string();
            Ok(format!(
                "HtmlElement(tag='{}', attributes={}, children={})",
                self.tag,
                attrs_repr,
                self.children.len()
            ))
        }
    }

    /// Custom __getattr__ to allow dot notation for attribute access
    /// This is called only when the attribute is not found through normal means
    /// Example: element.data_class instead of element.attributes["data_class"]
    fn __getattr__(&self, py: Python, name: &str) -> PyResult<PyObject> {
        // Try to get from attributes dict
        let attrs_dict = self.attributes.bind(py);
        if let Ok(value) = attrs_dict.get_item(name) {
            if let Some(val) = value {
                return Ok(val.unbind());
            }
        }

        // Attribute not found
        Err(PyErr::new::<pyo3::exceptions::PyAttributeError, _>(
            format!("'HtmlElement' object has no attribute '{}'", name)
        ))
    }

    /// Custom __setattr__ to allow dot notation for attribute assignment
    /// Example: element.data_class = "foo" instead of element.attributes["data_class"] = "foo"
    fn __setattr__(&mut self, py: Python, name: &str, value: PyObject) -> PyResult<()> {
        // Protect standard attributes from being overwritten
        match name {
            "tag" => {
                if let Ok(s) = value.extract::<String>(py) {
                    self.tag = s;
                    return Ok(());
                }
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "tag must be a string"
                ));
            }
            "attributes" => {
                if let Ok(dict) = value.extract::<Py<PyDict>>(py) {
                    self.attributes = dict;
                    return Ok(());
                }
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "attributes must be a dict"
                ));
            }
            "children" => {
                if let Ok(children) = value.extract::<Vec<PyObject>>(py) {
                    self.children = children;
                    return Ok(());
                }
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "children must be a list"
                ));
            }
            "is_text" => {
                if let Ok(b) = value.extract::<bool>(py) {
                    self.is_text = b;
                    return Ok(());
                }
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "is_text must be a bool"
                ));
            }
            _ => {}
        }

        // For other names, treat as HTML attribute assignment
        // This allows: element.data_class = "foo", element.cls = "bar", etc.
        let attrs_dict = self.attributes.bind(py);
        attrs_dict.set_item(name, value)?;
        Ok(())
    }
}

impl HtmlElement {
    /// Internal method to recursively serialize element to HTML string
    /// Applies attribute transformations (cls -> class, data_signals -> data-signals, etc.)
    fn serialize_to_html(&self, py: Python) -> PyResult<String> {
        // Handle text nodes
        if self.is_text {
            return Ok(self.tag.clone());
        }

        // Build opening tag with attributes
        let mut result = format!("<{}", self.tag);

        // Process attributes with transformations
        let attrs_dict = self.attributes.bind(py);
        let mut regular_attrs = HashMap::default();
        let mut datastar_attrs = HashMap::default();
        let processor = DatastarProcessor::new();

        for (key, value) in attrs_dict.iter() {
            let key_str = key.extract::<String>()?;

            // Check if it's a shorthand attribute first
            if let Some(mapped_key) = map_shorthand_attribute(&key_str) {
                // It's a shorthand attribute - process as Datastar
                let (data_key, data_value) = processor.process(&mapped_key, &value)?;
                datastar_attrs.insert(data_key, data_value);
            } else if key_str.starts_with("ds_") {
                // Direct Datastar attribute
                let (data_key, data_value) = processor.process(&key_str, &value)?;
                datastar_attrs.insert(data_key, data_value);
            } else {
                // Regular HTML attribute - apply attrmap transformation
                let mapped_key = attrmap_optimized(&key_str);
                let value_str = if let Ok(s) = value.extract::<String>() {
                    s
                } else {
                    value.str()?.extract::<String>()?
                };
                regular_attrs.insert(mapped_key, value_str);
            }
        }

        // Build attributes string using the same logic as normal rendering
        let attr_string = build_attributes_with_datastar(&regular_attrs, &datastar_attrs);
        result.push_str(&attr_string);
        result.push('>');

        // Process children
        for child_obj in &self.children {
            let child_bound = child_obj.bind(py);

            // Check if child is an HtmlElement
            if let Ok(child_element) = child_bound.extract::<PyRef<HtmlElement>>() {
                result.push_str(&child_element.serialize_to_html(py)?);
            } else if let Ok(child_str) = child_bound.extract::<String>() {
                result.push_str(&child_str);
            } else {
                // Try to convert to string
                result.push_str(&child_bound.str()?.extract::<String>()?);
            }
        }

        // Closing tag
        result.push_str(&format!("</{}>", self.tag));

        Ok(result)
    }

    /// Convert a scraper Node to an HtmlElement tree
    fn from_node(node_ref: ElementRef, py: Python) -> PyResult<Self> {
        let element = node_ref.value();
        let tag = element.name().to_string();

        // Extract attributes
        let attributes = PyDict::new(py);
        for (attr_name, attr_value) in element.attrs() {
            attributes.set_item(attr_name, attr_value)?;
        }

        // Process children recursively
        let mut children = Vec::new();
        for child_node in node_ref.children() {
            match child_node.value() {
                Node::Element(_) => {
                    // Element node - recurse
                    if let Some(child_ref) = ElementRef::wrap(child_node) {
                        let child_element = Self::from_node(child_ref, py)?;
                        children.push(Py::new(py, child_element)?.into());
                    }
                },
                Node::Text(text) => {
                    // Text node - add as string
                    let text_str = text.text.to_string();
                    if !text_str.trim().is_empty() {
                        let py_str: PyObject = text_str.into_pyobject(py).unwrap().unbind().into();
                        children.push(py_str);
                    }
                },
                _ => {
                    // Ignore comments, doctypes, etc.
                }
            }
        }

        Ok(HtmlElement {
            tag,
            attributes: attributes.unbind(),
            children,
            is_text: false,
        })
    }
}

// Core HtmlString with optimized memory layout
#[pyclass(module = "rusty_tags.core")]
pub struct HtmlString {
    #[pyo3(get)]
    content: String,
}

// TagBuilder for callable functionality - preserves tag structure
#[pyclass]
pub struct TagBuilder {
    tag_name: String,
    pub attrs: HashMap<String, String>,
    pub datastar_attrs: HashMap<String, DatastarValue>,
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

    #[pyo3(signature = (encoding = "utf-8", errors = None))]
    #[inline(always)]
    fn encode(&self, encoding: &str, errors: Option<&str>, py: Python) -> PyResult<Py<PyBytes>> {
        // Fast path for UTF-8 which is the default for Starlette/HTMLResponse
        let enc_lower = encoding.to_ascii_lowercase();
        if enc_lower == "utf-8" || enc_lower == "utf8" {
            return Ok(PyBytes::new(py, self.content.as_bytes()).unbind());
        }

        // Fallback: use Python's codecs.encode to respect requested encoding and error handling
        let codecs = py.import("codecs")?;
        let args = (self.content.as_str(), encoding, errors.unwrap_or("strict"));
        let res = codecs.call_method1("encode", args)?;
        // codecs.encode returns a 'bytes' object; return it directly
        Ok(res.extract::<Py<PyBytes>>()?)
    }

    #[inline(always)]
    fn __bytes__(&self, py: Python) -> Py<PyBytes> {
        PyBytes::new(py, self.content.as_bytes()).unbind()
    }
    
    // Pickle support using __getnewargs_ex__
    #[inline(always)]
    fn __getnewargs_ex__(&self, py: Python) -> PyResult<((String,), PyObject)> {
        let args = (self.content.clone(),);
        let kwargs = pyo3::types::PyDict::new(py);
        Ok((args, kwargs.into()))
    }

    /// Parse HTML string into an HtmlElement tree for inspection/modification
    /// This is opt-in - only use when you need to inspect or modify the HTML structure
    ///
    /// # Example
    /// ```python
    /// html = Div(Input(name="email"), Button("Submit"))
    /// doc = html.parse()  # Returns HtmlElement tree
    ///
    /// # Traverse and modify
    /// for child in doc.children:
    ///     if isinstance(child, HtmlElement) and child.tag == "input":
    ///         child.attributes["required"] = "true"
    ///
    /// # Serialize back
    /// modified_html = doc.to_html()
    /// ```
    fn parse(&self, py: Python) -> PyResult<Py<HtmlElement>> {
        // Parse HTML fragment using scraper
        let fragment = HtmlParser::parse_fragment(&self.content);

        // Get the root node(s) - for fragments, we may have multiple roots
        let root_nodes: Vec<_> = fragment.root_element().children().collect();

        // If we have a single root element, return it directly
        if root_nodes.len() == 1 {
            if let Some(root_ref) = ElementRef::wrap(root_nodes[0]) {
                let html_element = HtmlElement::from_node(root_ref, py)?;
                return Py::new(py, html_element);
            }
        }

        // Multiple roots or text nodes - create a wrapper element
        let mut children = Vec::new();
        for node in root_nodes {
            match node.value() {
                Node::Element(_) => {
                    if let Some(node_ref) = ElementRef::wrap(node) {
                        let child_element = HtmlElement::from_node(node_ref, py)?;
                        children.push(Py::new(py, child_element)?.into());
                    }
                },
                Node::Text(text) => {
                    // Text node - add as string
                    let text_str = text.text.to_string();
                    if !text_str.trim().is_empty() {
                        let py_str: PyObject = text_str.into_pyobject(py).unwrap().unbind().into();
                        children.push(py_str);
                    }
                },
                _ => {}
            }
        }

        // Create a fragment wrapper with all children
        let wrapper = HtmlElement {
            tag: "fragment".to_string(),
            attributes: PyDict::new(py).unbind(),
            children,
            is_text: false,
        };

        Py::new(py, wrapper)
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
            datastar_attrs: HashMap::default(),
        }
    }
    
    #[inline(always)]
    #[pyo3(signature = (*children, **kwargs))]
    fn __call__(&mut self, children: Vec<PyObject>, kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<HtmlString> {
        // Separate dict children from regular children and merge them into kwargs
        let mut filtered_children = Vec::new();
        let processor = DatastarProcessor::new();
        
        // Process existing kwargs first
        if let Some(kwargs) = kwargs {
            for (key, value) in kwargs.iter() {
                let key_str = key.extract::<String>()?;
                process_attribute_key_value(&key_str, &value, &processor, &mut self.attrs, &mut self.datastar_attrs, AttributeContext::Kwargs, py)?;
            }
        }
        
        // Process children, extracting dicts as attributes
        for child in children {
            let child_bound = child.bind(py);
            if child_bound.is_instance_of::<PyDict>() {
                // This child is a dict - expand it as positional dict
                let dict = child_bound.downcast::<PyDict>()?;
                for (key, value) in dict.iter() {
                    let key_str = key.extract::<String>()?;
                    process_attribute_key_value(&key_str, &value, &processor, &mut self.attrs, &mut self.datastar_attrs, AttributeContext::PositionalDict, py)?;
                }
            } else {
                // Regular child content
                filtered_children.push(child);
            }
        }
        
        // Build the final HTML using enhanced function
        build_html_tag_with_datastar(&self.tag_name, filtered_children, &self.attrs, &self.datastar_attrs, py)
    }
    
    #[inline(always)]
    fn __str__(&self) -> PyResult<String> {
        // Return empty tag without children for inspection
        let tag_lower = normalize_tag_name(&self.tag_name);
        let attr_string = build_attributes_with_datastar(&self.attrs, &self.datastar_attrs);
        
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

// Enhanced HTML tag builder with Datastar support
#[inline(always)]
fn build_html_tag_with_datastar(
    tag_name: &str,
    children: Vec<PyObject>,
    attrs: &HashMap<String, String>,
    datastar_attrs: &HashMap<String, DatastarValue>,
    py: Python
) -> PyResult<HtmlString> {
    let tag_lower = normalize_tag_name(tag_name);
    let attr_string = build_attributes_with_datastar(attrs, datastar_attrs);
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
            // Separate dict children from regular children and process all attributes properly
            let mut filtered_children = Vec::new();
            let mut attrs = HashMap::default();
            let mut datastar_attrs = HashMap::default();
            let processor = DatastarProcessor::new();
            
            // Process existing kwargs first
            if let Some(kwargs) = kwargs {
                for (key, value) in kwargs.iter() {
                    let key_str = key.extract::<String>()?;
                    process_attribute_key_value(&key_str, &value, &processor, &mut attrs, &mut datastar_attrs, AttributeContext::Kwargs, py)?;
                }
            }
            
            // Process children, extracting dicts as attributes
            for child in children {
                let child_bound = child.bind(py);
                if child_bound.is_instance_of::<PyDict>() {
                    // This child is a dict - expand it as positional dict
                    let dict = child_bound.downcast::<PyDict>()?;
                    for (key, value) in dict.iter() {
                        let key_str = key.extract::<String>()?;
                        process_attribute_key_value(&key_str, &value, &processor, &mut attrs, &mut datastar_attrs, AttributeContext::PositionalDict, py)?;
                    }
                } else {
                    // Regular child content
                    filtered_children.push(child);
                }
            }
            
            // If no children AND no attributes, return TagBuilder for chaining
            if filtered_children.is_empty() && attrs.is_empty() && datastar_attrs.is_empty() {
                let tag_builder = TagBuilder::new(stringify!($name).to_string());
                return Ok(Py::new(py, tag_builder)?.into());
            }
            
            // If no children but has attributes, create self-closing tag immediately
            if filtered_children.is_empty() {
                let html_string = build_html_tag_with_datastar(stringify!($name), filtered_children, &attrs, &datastar_attrs, py)?;
                return Ok(Py::new(py, html_string)?.into());
            }
            
            // Fast path for no attributes but with children
            if attrs.is_empty() && datastar_attrs.is_empty() {
                let children_string = process_children_optimized(&filtered_children, py)?;
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
            
            // Full path with attributes
            let html_string = build_html_tag_with_datastar(stringify!($name), filtered_children, &attrs, &datastar_attrs, py)?;
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
            if let Some(value_str) = convert_attribute_value(&value, py)? {
                attrs.insert(key_str, value_str);
            }
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

// Fragment processing function
#[inline]
fn build_fragment_optimized(children: Vec<PyObject>, py: Python) -> PyResult<HtmlString> {
    if children.is_empty() {
        return Ok(HtmlString::new(String::new()));
    }

    // Calculate capacity for better performance
    let estimated_capacity = children.len() * 50;
    let mut content = String::with_capacity(estimated_capacity);

    for child in children {
        let child_html = process_child_object(&child, py)?;
        content.push_str(&child_html);
    }

    Ok(HtmlString::new(content))
}

// Fragment tag - renders children without wrapper
#[pyfunction]
#[doc = "Fragment renders its children without creating a wrapper element"]
#[pyo3(signature = (*children, **_kwargs))]
#[inline(always)]
fn Fragment(children: Vec<PyObject>, _kwargs: Option<&Bound<'_, PyDict>>, py: Python) -> PyResult<HtmlString> {
    // Fragment ignores kwargs (no attributes on fragments)
    build_fragment_optimized(children, py)
}

/// Safe - Renders text with HTML escaping to prevent XSS and display HTML as text
/// Use this when you want to display user input or HTML code as plain text
///
/// Example:
///   Safe("<script>alert('xss')</script>")
///   Output: &lt;script&gt;alert('xss')&lt;/script&gt;
///
///   Div(Safe("<div>nikola</div>"))
///   Output: <div>&lt;div&gt;nikola&lt;/div&gt;</div>
#[pyfunction]
fn Safe(text: String) -> PyResult<HtmlString> {
    let escaped = html_escape(&text);
    Ok(HtmlString::new(escaped))
}

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
            if let Some(value_str) = convert_attribute_value(&value, py)? {
                attrs.insert(key_str, value_str);
            }
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
fn core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core classes
    m.add_class::<HtmlString>()?;
    m.add_class::<HtmlElement>()?;
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
    
    // Fragment tag
    m.add_function(wrap_pyfunction!(Fragment, m)?)?;
    m.add_function(wrap_pyfunction!(Safe, m)?)?;

    // Custom tag function
    m.add_function(wrap_pyfunction!(CustomTag, m)?)?;
    
    // Factory function for pickle support
    m.add_function(wrap_pyfunction!(create_html_string, m)?)?;
    
    Ok(())
}