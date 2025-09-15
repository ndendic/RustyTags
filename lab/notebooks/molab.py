import marimo

__generated_with = "0.15.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import rusty_tags as rt
    return mo, rt


@app.cell
def _(rt):
    rt.Div("Hello from Marimo!", rt.Button("click me!", cls="border rounded rounded-xl hover:cursor-pointer") , cls="grid text-2xl")
    return


app._unparsable_cell(
    r"""
    from rusty_tags.utils import create_template, page_template
    from rusty_tags.datastar import Signals

    hdrs = (
        rt.Link(rel='stylesheet', href='https://unpkg.com/open-props'),
        # Link(rel='stylesheet', href='https://unpkg.com/open-props/normalize.min.css'),
        rt.Style(f\"\"\"
            html {{
                background: light-dark(var(--gradient-5), var(--gradient-16));
                min-height: 100vh;
                color: light-dark(var(--gray-9), var(--gray-1));
                font-family: var(--font-geometric-humanist);
                font-size: var(--font-size-1);
            }}
            main {{
                width: min(100% - 2rem, 40rem);
                margin-inline: auto;
            }}
        
            /* RustyTags Xtras CSS */
        \"\"\"),
    )
    htmlkws = dict(lang=\"en\")
    bodykws = dict(signals=Signals(message=\"\", conn=\"\"))
    template = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, highlightjs=True)
    page = page_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, highlightjs=True)

    # mo.iframe(page(rt.H1(\"Nikola was here\")).render(),height=100, width=300)
    mo.Html(rt.H1(\"Nikola was here\").render())
    mo.iframe(\"www.google.com\",with=\"100%\", hight=\"500px\")

    """,
    name="_"
)


@app.cell
def _(mo):
    mo.iframe("<h1>This is an iframe with pure HTML content!</h1><p>It's rendered directly from a string.</p>")
    return


if __name__ == "__main__":
    app.run()
