import marimo

__generated_with = "0.16.5"
app = marimo.App(
    width="columns",
    app_title="Datastar Attributes",
    auto_download=["html"],
)

with app.setup(hide_code=True):
    import marimo as mo
    import rusty_tags as rt
    from rusty_tags.utils import create_template, page_template

    hdrs = (
        rt.Link(rel="stylesheet", href="https://unpkg.com/open-props"),
        rt.Style(
            """
            html {
                background: light-dark(var(--gradient-5), var(--gradient-16));
                min-height: 100vh;
                color: light-dark(var(--gray-9), var(--gray-1));
                font-family: var(--font-geometric-humanist);
                font-size: var(--font-size-1);
            }
            main {
                width: min(100% - 2rem, 45rem);
                margin-inline: auto;
            }
            .demo-section {
                background: light-dark(var(--gray-0), var(--gray-9));
                padding: var(--size-4);
                margin-block: var(--size-3);
                border-radius: var(--radius-3);
                border: 1px solid light-dark(var(--gray-3), var(--gray-7));
            }
            .demo-controls {
                display: flex;
                gap: var(--size-2);
                flex-wrap: wrap;
                align-items: center;
            }
            .demo-output {
                margin-top: var(--size-3);
                padding: var(--size-3);
                background: light-dark(var(--gray-1), var(--gray-8));
                border-radius: var(--radius-2);
                font-family: var(--font-mono);
            }
        """
        ),
    )

    htmlkws = dict(lang="en")
    template = rt.create_template(hdrs=hdrs, htmlkw=htmlkws)
    page = rt.page_template(hdrs=hdrs, htmlkw=htmlkws)


@app.function
def show(comp: str, width="100%", height="100%"):
    return mo.iframe(str(page(comp)), width=width, height=height)


@app.cell(hide_code=True)
def _():
    mo.md("""# RustyTags Datastar SDK - Complete Demo""")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 1. Basic Signal Usage

    Signals are the foundation of reactive state in Datastar. They provide type-safe, validated reactive variables.
    """
    )
    return


@app.cell
def _():
    from rusty_tags.datastar import Signal, Signals

    sigs = Signals(counter=0, user_name="John", is_active=True)

    basic_demo = rt.Div(
        rt.H3("Counter Demo"),
        rt.Div(
            rt.Button("-", on_click=sigs.counter.sub(1)),
            rt.P(text=sigs.counter),
            rt.Button("+", on_click=sigs.counter.add(1)),
            rt.Button("Reset", on_click=sigs.counter.set(0)),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals=sigs,
    )

    show(basic_demo, height="200px")
    return Signal, Signals


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 2. Arithmetic Operators

    All standard Python arithmetic operators work on Signals and generate JavaScript expressions.
    """
    )
    return


@app.cell
def _(Signals):
    numbers = Signals(x=10, y=3)
    arithmetic_demo = rt.Div(
        rt.H3("Arithmetic Operations"),
        rt.Div(
            rt.P(text="X: "+numbers.x),
            rt.P(text="Y: "+numbers.y),
            rt.Hr(),
            rt.P(text="Addition: " + (numbers.x + numbers.y)),
            rt.P(text="Subtraction: " + (numbers.x - numbers.y)),
            rt.P(text="Multiplication: " + (numbers.x * numbers.y)),
            rt.P(text="Division: " + (numbers.x / numbers.y)),
            rt.P(text="Modulo: " + (numbers.x % numbers.y)),
            cls="demo-output",
        ),
        rt.Div(
            rt.Button("X +5", on_click=numbers.x.add(5)),
            rt.Button("Y +1", on_click=numbers.y.add(1)),
            rt.Button("Reset", on_click=numbers.x.set(10).to_js() + "; " + numbers.y.set(3).to_js()),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals=numbers,
    )

    show(arithmetic_demo, height="400px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 3. Comparison & Logical Operators

    Compare signals and combine conditions with logical operators.
    """
    )
    return


@app.cell
def _(Signal):
    age = Signal("age", 25)
    has_license = Signal("has_license", True)

    comparison_demo = rt.Div(
        rt.H3("Comparison & Logic"),
        rt.Div(
            rt.P(text="Age: "+age),
            rt.P(text="Has License: "+has_license),
            rt.Hr(),
            rt.P(text=("Is Adult (≥18): ")+(age >= 18)),
            rt.P(text="Can Drive: "+((age >= 18) & has_license)),
            rt.P("Is Minor: ", rt.Span(text=age < 18)),
            rt.P("No License: ", rt.Span(text=~has_license)),
            cls="demo-output",
        ),
        rt.Div(
            rt.Button("Age +1", on_click=age.add(1)),
            rt.Button("Age -1", on_click=age.sub(1)),
            rt.Button("Toggle License", on_click=has_license.toggle()),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals={"age": 25, "has_license": True},
    )

    show(comparison_demo, height="400px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 4. String Methods

    Work with text using string manipulation methods.
    """
    )
    return


@app.cell
def _(Signal):
    text = Signal("text", "Hello World")

    string_demo = rt.Div(
        rt.H3("String Manipulation"),
        rt.Div(rt.Input(type="text", bind=text, placeholder="Enter text"), cls="demo-controls"),
        rt.Div(
            rt.P(text="Original: "+text),
            rt.P(text="Uppercase: "+text.upper()),
            rt.P(text="Lowercase: "+text.lower()),
            rt.P(text="Length: "+text.length),
            rt.P(text="Contains 'Hello': "+text.contains("Hello")),
            cls="demo-output",
        ),
        cls="demo-section",
        signals={"text": "Hello World"},
    )

    show(string_demo, height="350px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 5. Array Methods

    Manipulate lists with push, pop, append, and more.
    """
    )
    return


@app.cell
def _(Signal):
    from rusty_tags.datastar import js

    items = Signal("items", ["Apple", "Banana"])
    new_item = Signal("new_item", "Orange")

    array_demo = rt.Div(
        rt.H3("Array Operations"),
        rt.Div(
            rt.Input(type="text", bind=new_item, placeholder="New item"),
            rt.Button("Add Item", data_on_click=items.append(new_item).to_js() + "; " + new_item.set("").to_js()),
            rt.Button("Remove Last", data_on_click=items.pop()),
            rt.Button("Clear All", data_on_click=items.set([])),
            cls="demo-controls",
        ),
        rt.Div(
            rt.P("Count: ", rt.Span(text=items.length)),
            rt.P("Items: ", rt.Span(text=items.join(", "))),
            rt.P("Empty: ", rt.Span(text=items.length == 0)),
            cls="demo-output",
        ),
        cls="demo-section",
        signals={"items": ["Apple", "Banana"], "new_item": ""},
    )

    show(array_demo, height="350px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 6. Math Methods

    Mathematical operations like round, abs, min, max, and clamp.
    """
    )
    return


@app.cell
def _(Signal):
    value = Signal("value", 7.825)

    math_demo = rt.Div(
        rt.H3("Math Operations"),
        rt.Div(
            rt.P("Value: ", rt.Span(text=value)),
            rt.Hr(),
            rt.P("Rounded: ", rt.Span(text=value.round())),
            rt.P("Rounded (2 decimals): ", rt.Span(text=value.round(2))),
            rt.P("Absolute: ", rt.Span(text=value.abs())),
            rt.P("Min with 5: ", rt.Span(text=value.min(5))),
            rt.P("Max with 10: ", rt.Span(text=value.max(10))),
            rt.P("Clamped (0-10): ", rt.Span(text=value.clamp(0, 10))),
            cls="demo-output",
        ),
        rt.Div(
            rt.Button("+0.5", data_on_click=value.add(0.521)),
            rt.Button("-0.5", data_on_click=value.sub(0.5)),
            rt.Button("Set to -3.14", data_on_click=value.set(-3.14)),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals={"value": 7.8},
    )

    show(math_demo, height="450px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 7. Property & Index Access

    Access nested object properties and array indices.
    """
    )
    return


@app.cell
def _(Signal):
    user = Signal("user", {"name": "Alice", "age": 16, "email": "alice@example.com"})

    property_demo = rt.Div(
        rt.H3("Property Access"),
        rt.Div(
            rt.P("User Name: ", rt.Span(text=user.name)),
            rt.P("User Age: ", rt.Span(text=user.age)),
            rt.P("User Email: ", rt.Span(text=user.email)),
            rt.Hr(),
            rt.P("Adult: ", rt.Span(text=(user.age >= 18))),
            cls="demo-output",
        ),
        rt.Div(rt.Button("Birthday", on_click=user.age.add(1)), rt.Button("Change Name", on_click=user.name.set("Bob")), cls="demo-controls"),
        cls="demo-section",
        signals={"user": {"name": "Alice", "age": 30, "email": "alice@example.com"}},
    )

    show(property_demo, height="350px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 8. Conditional (Ternary) Expressions

    Use `if_()` method for conditional rendering.
    """
    )
    return


@app.cell
def _(Signal):
    from rusty_tags.datastar import if_
    score = Signal("score", 75)

    conditional_demo = rt.Div(
        rt.H3("Conditional Expressions"),
        rt.Div(
            rt.P("Score: ", rt.Span(text=score)),
            rt.Hr(),
            rt.P("Grade: ", rt.Span(text="($score >= 90) ? 'A' : 'B'")),
            rt.P("Grade: ", rt.Span(text=if_(score >= 90, "A", "B"))),
            rt.P("Grade: ", rt.Span(text=if_(score >= 90, "A", if_(score >= 80, "B", if_(score >= 70, "C", "F"))))),
            rt.P("Status: ", text=if_(score >= 60, "Pass", "Fail")),
            rt.Div(
                text=if_(score >= 90, "🎉 Excellent!", if_(score >= 70, "👍 Good", "📚 Keep trying")),
                style="font-size: 2rem; text-align: center; padding: 1rem;",
            ),
            cls="demo-output",
        ),
        rt.Div(
            rt.Button("+10", data_on_click=score.add(10)),
            rt.Button("-10", data_on_click=score.sub(10)),
            rt.Button("Reset", data_on_click=score.set(75)),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals={"score": 75},
    )

    show(conditional_demo, height="400px")
    return if_, score


@app.cell
def _(score):
    print((score >= 90).if_("A", "B"))
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 9. Pattern Matching with match()

    Switch between multiple values like Python's match/case.
    """
    )
    return


@app.cell
def _(Signals):
    from rusty_tags.datastar import match

    state = Signals(status="idle")

    match_demo = rt.Div(
        rt.H3("Pattern Matching"),
        rt.Div(
            rt.P("Current Status: ", rt.Span(text=state.status)),
            rt.Div(
                text=match(
                    state.status, 
                    idle="⏸️ Ready to start", 
                    loading="⏳ Processing...", 
                    success="✅ Completed!", 
                    error="❌ Failed!", 
                    default="❓ Unknown"
                ),
                style="font-size: 1.5rem; text-align: center; padding: 1rem;",
            ),
            cls="demo-output",
        ),
        rt.Div(
            rt.Button("Idle", on_click=state.status.set("idle")),
            rt.Button("Loading", on_click=state.status.set("loading")),
            rt.Button("Success", on_click=state.status.set("success")),
            rt.Button("Error", on_click=state.status.set("error")),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals=state,
    )

    show(match_demo, height="350px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 10. Template Literals with f()

    Create dynamic strings with embedded expressions.
    """
    )
    return


@app.cell
def _(Signals):
    from rusty_tags.datastar import f

    usr = Signals(first_name="John", last_name="Doe", age_val=25)

    template_demo = rt.Div(
        rt.H3("Template Literals"),
        rt.Div(
            rt.Input(type="text", bind=usr.first_name, placeholder="First name"),
            rt.Input(type="text", bind=usr.last_name, placeholder="Last name"),
            rt.Input(type="number", bind=usr.age_val, placeholder="Age"),
            cls="demo-controls",
        ),
        rt.Div(
            rt.P(text=f("Hello, {fn} {ln}!", fn=usr.first_name, ln=usr.last_name)),
            rt.P(text=f("You are {age} years old.", age=usr.age_val)),
            rt.P(text=f("In 10 years, you'll be {future}.", future=usr.age_val + 10)),
            cls="demo-output",
        ),
        cls="demo-section",
        signals=usr,
    )

    show(template_demo, height="350px")
    return (f,)


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 11. Collect - Dynamic Classes

    Gather multiple conditional values, perfect for CSS classes.
    """
    )
    return


@app.cell
def _(Signal):
    from rusty_tags.datastar import collect

    is_large = Signal("is_large", False)
    is_bold = Signal("is_bold", False)
    is_italic = Signal("is_italic", False)

    collect_demo = rt.Div(
        rt.H3("Dynamic Styling with collect()"),
        rt.Div(
            rt.Label(rt.Input(type="checkbox", bind=is_large), " Large"),
            rt.Label(rt.Input(type="checkbox", bind=is_bold), " Bold"),
            rt.Label(rt.Input(type="checkbox", bind=is_italic), " Italic"),
            cls="demo-controls",
        ),
        rt.Div(
            rt.P(
                "Styled Text",
                data_class=collect([(is_large, "large"), (is_bold, "bold"), (is_italic, "italic")], join_with=" "),
                style="transition: all 0.3s;",
            ),
            cls="demo-output",
        ),
        rt.Style(
            """
            .large { font-size: 2rem; }
            .bold { font-weight: bold; }
            .italic { font-style: italic; }
        """
        ),
        cls="demo-section",
        signals={"is_large": False, "is_bold": False, "is_italic": False},
    )

    show(collect_demo, height="300px")
    return collect, is_bold, is_italic, is_large


@app.cell
def _(collect, is_bold, is_italic, is_large):
    print(collect([(is_large, "large"), (is_bold, "bold"), (is_italic, "italic")], join_with=" "))
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 11b. Datastar data-class with classes()

    For Datastar's `data-class` attribute specifically, use `classes()` which generates 
    the proper object literal format: `{class: condition}`.
    """
    )
    return


@app.cell
def _(Signal):
    from rusty_tags.datastar import classes

    cls_large = Signal("cls_large", False)
    cls_bold = Signal("cls_bold", False)
    cls_italic = Signal("cls_italic", False)
    cls_blue = Signal("cls_blue", False)

    classes_demo = rt.Div(
        rt.H3("Datastar data-class with classes()"),
        rt.Div(
            rt.Label(rt.Input(type="checkbox", bind=cls_large), " Large"),
            rt.Label(rt.Input(type="checkbox", bind=cls_bold), " Bold"),
            rt.Label(rt.Input(type="checkbox", bind=cls_italic), " Italic"),
            rt.Label(rt.Input(type="checkbox", bind=cls_blue), " Blue"),
            cls="demo-controls",
        ),
        rt.Div(
            rt.P(
                "Styled Text with data-class",
                data_class=classes(large=cls_large, bold=cls_bold, italic=cls_italic, blue=cls_blue),
                style="transition: all 0.3s;",
            ),
            cls="demo-output",
        ),
        rt.Style(
            """
            .large { font-size: 2rem; }
            .bold { font-weight: bold; }
            .italic { font-style: italic; }
            .blue { color: var(--blue-9); animation: var(--animation-fade-in)}
        """
        ),
        cls="demo-section",
        signals={"cls_large": False, "cls_bold": False, "cls_italic": False, "cls_blue": False},
    )

    show(classes_demo, height="350px")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 12. Logical Aggregation (all/any)

    Check if all or any conditions are truthy.
    """
    )
    return


@app.cell
def _(Signal, if_):
    from rusty_tags.datastar import all as all_cond, any as any_cond

    check1 = Signal("check1", False)
    check2 = Signal("check2", False)
    check3 = Signal("check3", False)

    logic_demo = rt.Div(
        rt.H3("Logical Aggregation"),
        rt.Div(
            rt.Label(rt.Input(type="checkbox", bind=check1), " Check 1"),
            rt.Label(rt.Input(type="checkbox", bind=check2), " Check 2"),
            rt.Label(rt.Input(type="checkbox", bind=check3), " Check 3"),
            cls="demo-controls",
        ),
        rt.Div(
            rt.P("All checked: ", rt.Span(text=all_cond(check1, check2, check3))),
            rt.P("Any checked: ", rt.Span(text=any_cond(check1, check2, check3))),
            rt.P(
                "Submit button: ",
                rt.Button(
                    "Submit",
                    data_disabled=~all_cond(check1, check2, check3),
                    style="opacity: 0.5;",
                    data_attr_style=if_(all_cond(check1, check2, check3), "opacity: 1;", "opacity: 0.5;"),
                ),
            ),
            cls="demo-output",
        ),
        cls="demo-section",
        signals={"check1": False, "check2": False, "check3": False},
    )


    show(logic_demo, height="350px")
    return all_cond, check1


@app.cell
def _(check1, if_):

    print(if_(check1, "True", "False"))
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        """
    ## 13. Complete Form Example

    Putting it all together: a reactive form with validation.
    """
    )
    return


@app.cell
def _(Signal, all_cond, f, if_):
    form_name = Signal("form_name", "")
    form_email = Signal("form_email", "")
    form_age = Signal("form_age", 0)
    form_agree = Signal("form_agree", False)

    name_valid = form_name.length >= 3
    email_valid = form_email.contains("@")
    age_valid = form_age >= 18
    can_submit = all_cond(name_valid, email_valid, age_valid, form_agree)

    form_demo = rt.Div(
        rt.H3("Complete Registration Form"),
        rt.Div(
            rt.Div(
                rt.Label("Name:"),
                rt.Input(type="text", bind=form_name, placeholder="Enter name (min 3 chars)"),
                rt.P("✓ Valid", data_show=name_valid, style="color: green;"),
                rt.P("✗ Too short", data_show=~name_valid, style="color: red;"),
            ),
            rt.Div(
                rt.Label("Email:"),
                rt.Input(type="email", bind=form_email, placeholder="Enter email"),
                rt.P("✓ Valid", data_show=email_valid, style="color: green;"),
                rt.P("✗ Invalid", data_show=~email_valid, style="color: red;"),
            ),
            rt.Div(
                rt.Label("Age:"),
                rt.Input(type="number", bind=form_age, placeholder="Enter age"),
                rt.P("✓ Valid", data_show=age_valid, style="color: green;"),
                rt.P("✗ Must be 18+", data_show=~age_valid, style="color: red;"),
            ),
            rt.Div(
                rt.Label(rt.Input(type="checkbox", bind=form_agree), " I agree to terms"),
            ),
        ),
        rt.Div(
            rt.Button(
                "Submit", data_disabled=~can_submit, data_attr_style=if_(can_submit, "opacity: 1; cursor: pointer;", "opacity: 0.5; cursor: not-allowed;")
            ),
            rt.P(text=f("Hello, {name}!", name=form_name), data_show=can_submit),
            cls="demo-controls",
        ),
        cls="demo-section",
        signals={"form_name": "", "form_email": "", "form_age": 0, "form_agree": False},
    )

    show(form_demo, height="600px")
    return


@app.cell
def _():
    mo.md(
        """
    ## Summary

    This demo showcases the RustyTags Datastar SDK's complete feature set:

    - ✅ Type-safe Signals with validation
    - ✅ Arithmetic, comparison, and logical operators
    - ✅ String, array, and math methods
    - ✅ Property and index access
    - ✅ Conditional expressions and pattern matching
    - ✅ Template literals
    - ✅ Dynamic class collection
    - ✅ Logical aggregation
    - ✅ Complete reactive forms

    All features generate optimized JavaScript and work seamlessly with Datastar's reactive system!
    """
    )
    return


if __name__ == "__main__":
    app.run()
