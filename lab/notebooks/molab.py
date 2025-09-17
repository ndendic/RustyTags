import marimo

__generated_with = "0.15.5"
app = marimo.App(
    width="columns",
    layout_file="layouts/molab.slides.json",
    css_file="",
)

with app.setup(hide_code=True):
    import marimo as mo
    import rusty_tags as rt
    from rusty_tags.utils import create_template, page_template
    from rusty_tags.datastar import Signals

    hdrs = (
        rt.Link(rel='stylesheet', href='https://unpkg.com/open-props'),
        rt.Link(rel='stylesheet', href='https://unpkg.com/open-props/normalize.min.css'),
        rt.Style("""
            html {
                font-family: var(--font-geometric-humanist);
                backroung-color: #EFD49F
                font-size: var(--font-size-1);
            }
            main {
                width: min(100% - 2rem, 40rem);
                margin-inline: auto;
            }

        """),
    )
    htmlkws = dict(lang="en")
    bodykws = dict(signals=Signals(message="", conn=""))
    template = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, highlightjs=True)
    page = page_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, highlightjs=True)


@app.function
def show(comp:str, width="100%",height="400px"):
    return mo.iframe(str(page(comp)), width=width,height=height)


@app.cell
def _():
    sigs = rt.Signals(message="Hello ", name="Nikola")

    myComp = rt.Div(
            rt.H2("Demo APP!"),
            rt.Input(bind="message"),
            rt.Input(bind="name"),
            rt.P("Hello from Marimo!", text="$message + $name"),
            style="display: grid; gap: 1rem; width: min(100% - 2rem, 20rem); margin-inline: auto;",
            signals = sigs
        )
    return (myComp,)


@app.cell
def _(myComp):
    show(myComp)
    return


@app.cell(column=1)
def _():
    show(
        rt.Div(
            rt.Details(rt.Summary("Click me"), "For real?", name="1"), 
            rt.Details(rt.Summary("Here!"), "For real?", name="1"), 
            rt.Details(rt.Summary("Really?"), "For real?", name="1")
        )
    )
    return


@app.cell
def _():
    import inspect

    def printer(
        txt="Default" # Some default text, description="A description of the text parameter"
    ):
        print(txt)

    # print the code of the printer def
    source_lines = inspect.getsource(printer).split('\n')
    print('\n'.join(source_lines))

    return


if __name__ == "__main__":
    app.run()
