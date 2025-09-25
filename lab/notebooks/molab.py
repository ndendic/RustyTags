import marimo

__generated_with = "0.16.0"
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
        # rt.Link(rel='stylesheet', href='https://unpkg.com/open-props/normalize.min.css'),
        rt.Style("""
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
            ::backdrop {
                  background-image: linear-gradient(
                    45deg,
                    magenta,
                    rebeccapurple,
                    dodgerblue,
                    green
                  );
                  opacity: 0.75;
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
            rt.Details(rt.Summary("Click me", style="list-style: none;"), "For real?", name="1"), 
            rt.Details(rt.Summary("Here!"), "For real?", name="1"), 
            rt.Details(rt.Summary("Really?"), "For real?", name="1"),
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


@app.cell(column=2)
def _():
    mo.md(r"""## Dialog testing""")
    return


@app.cell
def _():
    import uuid

    def Dialog(*children,id: str | None = None, **args):
        if id is not None:
            args['id'] = id
        elif 'id' not in args.keys():
            args['id'] = f"dialog_{uuid.uuid4()}"

        return rt.Dialog(*children,**args)

    def DialogToggle(*children,toggles=None,modal=False, **args):
        if toggles is None:
            raise ValueError("DialogToggle requires a 'toggles' argument")
        showAction = 'showModal' if modal else 'show'
        sigs = rt.Signals(**{toggles: 'false'})
        return rt.Button(
                    *children,
                    signals=sigs,           
                    on_click=f"${toggles} ? document.getElementById('{toggles}').{showAction}() : document.getElementById('{toggles}').close(); ${toggles} = !${toggles};",
                    **args
        )

    demo = rt.Div(
            DialogToggle("Dialog", toggles="MyDialog"),
            Dialog("Hello!", id="MyDialog"),
        )
    print(demo.render())
    show(demo)
    return


if __name__ == "__main__":
    app.run()
