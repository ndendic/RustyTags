#!/usr/bin/env python3
"""
Compare tags between Air and RustyTags to find missing ones
"""

import inspect
import air.tags as air_tags
import rusty_tags as rt

def get_air_tags():
    """Get all HTML tag classes from Air."""
    tags = []
    for name, obj in inspect.getmembers(air_tags):
        if (inspect.isclass(obj) and 
            issubclass(obj, air_tags.Tag) and 
            obj != air_tags.Tag and 
            obj != air_tags.CaseTag and
            obj != air_tags.Html and
            obj != air_tags.RawHTML):
            tags.append(name)
    return sorted(tags)

def get_rusty_tags():
    """Get all HTML tag functions from RustyTags."""
    tags = []
    for name in dir(rt):
        if (not name.startswith('_') and 
            callable(getattr(rt, name)) and
            name != 'Html' and  # Special case
            name not in ['render_list_optimized', 'render_table_optimized']):  # Utility functions
            tags.append(name)
    return sorted(tags)

def compare_tags():
    """Compare tags between Air and RustyTags."""
    air_tags_list = get_air_tags()
    rusty_tags_list = get_rusty_tags()
    
    print("🔍 COMPARING TAGS: Air vs RustyTags")
    print("=" * 60)
    
    print(f"📊 Air has {len(air_tags_list)} tags")
    print(f"📊 RustyTags has {len(rusty_tags_list)} tags")
    
    # Find missing tags in RustyTags
    missing_in_rusty = set(air_tags_list) - set(rusty_tags_list)
    
    # Find extra tags in RustyTags (that Air doesn't have)
    extra_in_rusty = set(rusty_tags_list) - set(air_tags_list)
    
    print(f"\n❌ Missing in RustyTags ({len(missing_in_rusty)} tags):")
    if missing_in_rusty:
        for tag in sorted(missing_in_rusty):
            print(f"  - {tag}")
    else:
        print("  None! 🎉")
    
    print(f"\n➕ Extra in RustyTags ({len(extra_in_rusty)} tags):")
    if extra_in_rusty:
        for tag in sorted(extra_in_rusty):
            print(f"  + {tag}")
    else:
        print("  None!")
    
    # Show common tags
    common_tags = set(air_tags_list) & set(rusty_tags_list)
    print(f"\n✅ Common tags ({len(common_tags)} tags):")
    for tag in sorted(list(common_tags)[:10]):  # Show first 10
        print(f"  ✓ {tag}")
    if len(common_tags) > 10:
        print(f"  ... and {len(common_tags) - 10} more")
    
    return missing_in_rusty, extra_in_rusty

def generate_missing_tags_code(missing_tags):
    """Generate Rust code for missing tags."""
    if not missing_tags:
        print("\n🎉 No missing tags to generate!")
        return
    
    print(f"\n🔧 RUST CODE TO ADD ({len(missing_tags)} missing tags):")
    print("=" * 60)
    
    # Get docstrings from Air
    air_docs = {}
    for name, obj in inspect.getmembers(air_tags):
        if inspect.isclass(obj) and hasattr(obj, '__doc__'):
            air_docs[name] = obj.__doc__ or f"Defines {name.lower()} element"
    
    for tag in sorted(missing_tags):
        doc = air_docs.get(tag, f"Defines {tag.lower()} element")
        print(f'html_tag_optimized!({tag}, "{doc}");')

if __name__ == "__main__":
    missing, extra = compare_tags()
    generate_missing_tags_code(missing)
    
    print(f"\n📋 SUMMARY:")
    print(f"• Missing tags to add: {len(missing)}")
    print(f"• Extra tags (RustyTags only): {len(extra)}")
    print(f"• Implementation coverage: {(len(get_rusty_tags()) / len(get_air_tags())) * 100:.1f}%")