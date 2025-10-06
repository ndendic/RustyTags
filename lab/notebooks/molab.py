import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    import marimo as mo
    import rusty_tags as rt
    from rusty_tags.utils import create_template, page_template

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
        """),
    )
    htmlkws = dict(lang="en")
    template = create_template(hdrs=hdrs, htmlkw=htmlkws)
    page = page_template(hdrs=hdrs, htmlkw=htmlkws)


@app.function
def show(comp:str, width="100%",height="100%"):
    return mo.iframe(str(page(comp)), width=width,height=height)


@app.cell
def _():
    myComp = rt.Div(
            # rt.H2("D* Playground"),
            rt.Button("-",on_click="$counter--"),
            rt.P("Hello from Marimo!", text="$counter"),
            rt.Button("+",on_click="$counter++"),

            style="display: flex; gap: 1rem; width: min(100% - 2rem, 20rem); margin-inline: auto; align-items: center;",
            signals = {"message": "Hello ", "name": "Nikola", "counter":"0"}
        )
    show(myComp)
    return


if __name__ == "__main__":
    app.run()
