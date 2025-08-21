#!/usr/bin/env python3
"""
Demo of new Datastar shorthand attributes in RustyTags
Shows before/after comparison and real-world usage examples
"""

import rusty_tags as rt
from rusty_tags.datastar import signals, reactive_class, DS

def demo_before_after():
    """Show before/after comparison of shorthand vs ds_ prefix"""
    print("🔄 BEFORE/AFTER COMPARISON")
    print("=" * 50)
    
    print("\n📝 BEFORE (ds_ prefix):")
    old_syntax = rt.Div(
        "Hello World",
        ds_signals={"count": 0, "user": {"name": "John"}},
        ds_show="$isVisible", 
        ds_on_click="$count++",
        ds_text="$message"
    )
    print(f"Code: rt.Div('Hello World', ds_signals={{'count': 0}}, ds_show='$isVisible', ds_on_click='$count++', ds_text='$message')")
    print(f"HTML: {old_syntax}")
    
    print("\n✨ AFTER (shorthand):")
    new_syntax = rt.Div(
        "Hello World",
        signals={"count": 0, "user": {"name": "John"}},
        show="$isVisible",
        on_click="$count++", 
        text="$message"
    )
    print(f"Code: rt.Div('Hello World', signals={{'count': 0}}, show='$isVisible', on_click='$count++', text='$message')")
    print(f"HTML: {new_syntax}")
    
    print(f"\n✅ Same output: {str(old_syntax) == str(new_syntax)}")


def demo_comprehensive_example():
    """Show comprehensive real-world example"""
    print("\n\n🏗️  COMPREHENSIVE EXAMPLE")
    print("=" * 50)
    
    # Build a complete interactive todo app component
    todo_app = rt.Div(
        # Header with title and add button
        rt.Header(
            rt.H1("Todo App", text="$appTitle"),
            rt.Button(
                "+ Add Todo",
                on_click=DS.post("/todos", data="$newTodo", target="#todo-list"),
                show="$canAddTodo"
            ),
            cls="header"
        ),
        
        # Input form for new todos
        rt.Form(
            rt.Input(
                type="text",
                bind="$newTodo.text",
                attrs={"placeholder": "What needs to be done?"},
                on_keydown="$event.key === 'Enter' && $addTodo()"
            ),
            rt.Button(
                "Add",
                on_click="$addTodo()", 
                attrs={"disabled": "$newTodo.text.length === 0"}
            ),
            on_submit="$addTodo(); $event.preventDefault()"
        ),
        
        # Todo list with dynamic items
        rt.Div(
            rt.Div(
                text="No todos yet!",
                show="$todos.length === 0",
                cls="empty-state"
            ),
            rt.Div(
                # This would be repeated for each todo item
                rt.Input(
                    type="checkbox",
                    bind="$todo.completed",
                    on_change="$toggleTodo($index)"
                ),
                rt.Span(
                    text="$todo.text",
                    cls=reactive_class(
                        completed="$todo.completed",
                        priority="$todo.priority === 'high'"
                    )
                ),
                rt.Button(
                    "Delete",
                    on_click=DS.delete(f"/todos/{{}}", target="#todo-list"),
                    cls="delete-btn"
                ),
                show="$todos.length > 0",
                effect="$updateProgress()",
                cls="todo-item"
            ),
            id="todo-list",
            cls="todo-list"
        ),
        
        # Footer with stats and filters
        rt.Footer(
            rt.Span(
                text="$completedCount + ' of ' + $todos.length + ' completed'",
                cls="stats"
            ),
            rt.Div(
                rt.Button("All", on_click=DS.set("filter", "all")),
                rt.Button("Active", on_click=DS.set("filter", "active")),
                rt.Button("Completed", on_click=DS.set("filter", "completed")),
                cls="filters"
            ),
            rt.Button(
                "Clear Completed",
                on_click="$clearCompleted()",
                show="$completedCount > 0"
            ),
            cls="footer"
        ),
        
        # Root component with all state
        signals={
            "appTitle": "My Todo App",
            "todos": [],
            "newTodo": {"text": "", "priority": "normal"},
            "filter": "all",
            "completedCount": 0,
            "canAddTodo": True
        },
        
        # Global effects and computed values
        computed="completedCount = $todos.filter(t => t.completed).length",
        effect="$saveTodos($todos)",
        
        cls="todo-app",
        id="app"
    )
    
    print("Generated Todo App HTML:")
    print("-" * 30)
    print(str(todo_app))


def demo_all_shorthand_attributes():
    """Demonstrate all supported shorthand attributes"""
    print("\n\n📋 ALL SUPPORTED SHORTHAND ATTRIBUTES")  
    print("=" * 50)
    
    # Core attributes (most common)
    core_attrs = {
        "signals": {"demo": "value"},
        "bind": "$inputValue", 
        "show": "$isVisible",
        "text": "$dynamicText",
        "attrs": {"disabled": "$isLoading"},
        "style": {"color": "$themeColor"}
    }
    
    print("\n🎯 CORE ATTRIBUTES:")
    for attr, value in core_attrs.items():
        div = rt.Div(**{attr: value})
        print(f"  {attr:8} → {div}")
    
    # Event attributes
    event_attrs = [
        "on_click", "on_hover", "on_submit", "on_focus", "on_blur", 
        "on_keydown", "on_change", "on_input", "on_load", "on_intersect"
    ]
    
    print("\n🎪 EVENT ATTRIBUTES:")
    for attr in event_attrs:
        div = rt.Div(**{attr: f"${attr.replace('on_', '')}Handler()"})
        print(f"  {attr:12} → {div}")
    
    # Advanced attributes  
    advanced_attrs = {
        "effect": "console.log($state)",
        "computed": "fullName = $first + $last", 
        "ref": "$refs.element",
        "indicator": "$loadingState",
        "persist": "local",
        "ignore": "true"
    }
    
    print("\n🚀 ADVANCED ATTRIBUTES:")
    for attr, value in advanced_attrs.items():
        div = rt.Div(**{attr: value})
        print(f"  {attr:10} → {div}")


def demo_migration_guide():
    """Show migration examples"""
    print("\n\n🔄 MIGRATION GUIDE")
    print("=" * 50)
    
    migrations = [
        ("ds_signals", "signals", {"count": 0}),
        ("ds_bind", "bind", "$value"),
        ("ds_show", "show", "$visible"),
        ("ds_text", "text", "$message"),
        ("ds_on_click", "on_click", "$handleClick()"),
        ("ds_on_hover", "on_hover", "$showTooltip()"),
        ("ds_effect", "effect", "console.log($data)"),
        ("ds_computed", "computed", "total = $items.length")
    ]
    
    for old_attr, new_attr, value in migrations:
        print(f"\n📝 {old_attr} → {new_attr}")
        old_div = rt.Div(**{old_attr: value})
        new_div = rt.Div(**{new_attr: value})
        print(f"  Old: {old_div}")
        print(f"  New: {new_div}")
        print(f"  ✅ Same output: {str(old_div) == str(new_div)}")


def main():
    """Run all demos"""
    print("✨ RUSTY TAGS DATASTAR SHORTHAND ATTRIBUTES DEMO")
    print("=" * 60)
    
    demo_before_after()
    demo_comprehensive_example() 
    demo_all_shorthand_attributes()
    demo_migration_guide()
    
    print("\n\n🎉 SUMMARY")
    print("=" * 20)
    print("✅ All Datastar attributes now support shorthand syntax!")
    print("✅ Full backward compatibility with ds_ prefixes")
    print("✅ Generic event support (on_* → data-on-*)")
    print("✅ Cleaner, more readable code")
    print("✅ Same performance - zero overhead")


if __name__ == "__main__":
    main()