"""Dialog component documentation page"""

from .base import *

from rusty_tags.xtras import (
    Dialog,
    DialogTrigger,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogBody,
    DialogFooter,
    DialogClose,
    ConfirmDialog,
)


def example_basic_dialog():
    return Dialog(
        DialogTrigger(
            "Open basic dialog",
            toggles="basicDialog",
            style="padding:0.5rem 1rem; border:1px solid currentColor; border-radius:0.5rem; background:transparent; cursor:pointer;",
        ),
        DialogContent(
            DialogHeader(
                DialogTitle("Basic dialog"),
                DialogClose(
                    "Close",
                    style="border:none; background:none; cursor:pointer; text-decoration:underline;",
                ),
                style="display:flex; align-items:center; justify-content:space-between;",
            ),
            DialogBody(
                P("Dialogs keep their own Datastar-backed open state."),
                P("When you pass `id='basicDialog'`, the signal becomes `$basicDialog_open` automatically."),
                style="display:grid; gap:0.75rem;",
            ),
            DialogFooter(
                DialogClose(
                    "Cancel",
                    style="border:1px solid currentColor; background:transparent; padding:0.4rem 0.9rem; border-radius:0.5rem; cursor:pointer;",
                ),
                DialogClose(
                    "Confirm",
                    on_click="console.log('Confirmed')",
                    style="border:1px solid currentColor; background:currentColor; color:Canvas; padding:0.4rem 0.9rem; border-radius:0.5rem; cursor:pointer;",
                ),
                style="display:flex; justify-content:flex-end; gap:0.75rem;",
            ),
            content_attrs=dict(
                style="display:grid; gap:1.5rem; padding:1.5rem; border:1px solid currentColor; border-radius:0.75rem; background:Canvas; color:CanvasText; min-width:18rem;",
            ),
            style="padding:0; border:none; background:transparent;",
        ),
        id="basicDialog",
        data_style="{backdropFilter: $basicDialog_open ? 'blur(6px)' : 'none'}",
    )


def example_confirm_dialog():
    return ConfirmDialog(
        title="Delete file",
        message="Are you sure you want to delete this file? This action cannot be undone.",
        trigger_text="Delete file",
        confirm_text="Delete",
        cancel_text="Cancel",
        on_confirm="console.log('File deleted')",
        id="deleteFile",
        trigger_attrs={
            "style": "padding:0.45rem 1rem; border:1px solid currentColor; border-radius:0.5rem; background:var(--red-3, #fee); cursor:pointer;",
        },
        confirm_attrs={
            "style": "padding:0.45rem 1rem; border:1px solid currentColor; border-radius:0.5rem; background:var(--red-6, #c00); color:Canvas; cursor:pointer;",
        },
        cancel_attrs={
            "style": "padding:0.45rem 1rem; border:1px solid currentColor; border-radius:0.5rem; background:transparent; cursor:pointer;",
        },
        close_icon_attrs={
            "style": "border:none; background:none; cursor:pointer; font-size:1rem;",
        },
        data_style="{maxWidth: '26rem', borderColor: $deleteFile_open ? 'currentColor' : 'transparent'}",
    )


def example_custom_dialog():
    return Dialog(
        DialogTrigger(
            "Compose message",
            style="padding:0.5rem 1rem; border:1px solid currentColor; border-radius:999px; background:transparent; cursor:pointer;",
        ),
        DialogContent(
            DialogHeader(
                DialogTitle("Compose message"),
                DialogClose(
                    "×",
                    style="border:none; background:none; font-size:1.25rem; cursor:pointer; line-height:1;",
                ),
                style="display:flex; align-items:center; justify-content:space-between;",
            ),
            DialogBody(
                P("Use `content_attrs` to style the inner surface without predefined classes."),
                Div(
                    Label("Subject", _for="subject"),
                    Input(id="subject", placeholder="Quarterly report", style="padding:0.4rem 0.6rem; border:1px solid currentColor; border-radius:0.4rem;"),
                    Label("Message", _for="message"),
                    Textarea(id="message", rows=4, style="padding:0.4rem 0.6rem; border:1px solid currentColor; border-radius:0.4rem;"),
                    style="display:grid; gap:0.75rem;",
                ),
                style="display:grid; gap:1rem;",
            ),
            DialogFooter(
                DialogClose(
                    "Discard",
                    style="border:1px solid currentColor; background:transparent; padding:0.45rem 1rem; border-radius:0.5rem; cursor:pointer;",
                ),
                DialogClose(
                    "Send",
                    on_click="console.log('Message sent')",
                    style="border:1px solid currentColor; background:currentColor; color:Canvas; padding:0.45rem 1rem; border-radius:0.5rem; cursor:pointer;",
                ),
                style="display:flex; justify-content:flex-end; gap:0.75rem;",
            ),
            content_attrs=dict(
                style="display:grid; gap:1.5rem; padding:1.75rem; border:1px solid currentColor; border-radius:1rem; background:Canvas; color:CanvasText; min-width:22rem;",
                data_style="{boxShadow: $composer_open ? '0 24px 48px -24px oklch(0 0 0 / 0.45)' : 'none'}",
            ),
        ),
        id="composer",
        data_style="{opacity: $composer_open ? 1 : 0.92}",
    )


def get_routes(app: FastAPI):
    """Register routes for Dialog documentation"""

    @app.get("/xtras/dialog")
    @page(title="Dialog Component Documentation", wrap_in=HTMLResponse)
    def dialog_docs():
        return Main(
            H1("Dialog Component"),
            P("The Dialog primitive exposes native dialog behaviour without imposing styling or global JavaScript."),

            Section(
                "Component Purpose",
                P("Dialog solves native modal orchestration without extra scripts:"),
                Ul(
                    Li("🏗️ Datastar-driven open state shared across triggers and content"),
                    Li("♿️ Accessibility handled by the browser via `<dialog>` APIs"),
                    Li("⌨️ Keyboard support including ESC, focus trap, and restoration"),
                    Li("🪟 Backdrop interaction control through inline expressions"),
                    Li("🎛️ Headless composition ready for user-defined styling"),
                ),
            ),

            Section(
                "Basic Dialog Demo",
                P("A straightforward dialog using inline styling and Datastar bindings."),
                ComponentShowcase(example_basic_dialog),
            ),

            Section(
                "Confirm Dialog Demo",
                P("A convenience wrapper for confirmation workflows."),
                # ComponentShowcase(example_confirm_dialog),
            ),

            Section(
                "Custom Dialog Demo",
                P("Demonstrates id-derived signals, styling hooks, and inline side effects."),
                # ComponentShowcase(example_custom_dialog),
            ),

            Section(
                "API Reference",
                CodeBlock(
                    """
from typing import Any, Optional, Dict

# Root dialog wrapper
Dialog(
    *children: Any,
    id: Optional[str] = None,
    default_open: bool = False,
    modal: bool = True,
    close_on_escape: bool = True,
    close_on_backdrop: bool = True,
    element_id: Optional[str] = None,
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString

# Trigger button
DialogTrigger(*children: Any, cls: str = "", **attrs: Any)

# Dialog surface+content
DialogContent(
    *children: Any,
    cls: str = "",
    *,
    content_attrs: Optional[Dict[str, Any]] = None,
    dialog_cls: str = "",
    **attrs: Any,
)

# Sections and helpers
DialogHeader(*children: Any, cls: str = "", **attrs: Any)
DialogTitle(*children: Any, cls: str = "", **attrs: Any)
DialogBody(*children: Any, cls: str = "", **attrs: Any)
DialogFooter(*children: Any, cls: str = "", **attrs: Any)
DialogClose(*children: Any, cls: str = "", **attrs: Any)

# Convenience pattern
ConfirmDialog(
    title: str,
    message: str,
    *,
    id: Optional[str] = None,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    trigger_text: str = "Open Dialog",
    on_confirm: str = "",
    trigger_attrs: Optional[Dict[str, Any]] = None,
    confirm_attrs: Optional[Dict[str, Any]] = None,
    cancel_attrs: Optional[Dict[str, Any]] = None,
    close_icon: str = "×",
    close_icon_attrs: Optional[Dict[str, Any]] = None,
    element_id: Optional[str] = None,
    **attrs: Any,
) -> rt.HtmlString
""",
                    code_cls="language-python",
                ),
            ),

            Section(
                "Implementation Notes",
                Ul(
                    Li("🆔 Pass `id` once; the `$<id>_open` signal is generated automatically."),
                    Li("🦀 Native-first: the component calls `showModal()`/`show()` through `data-effect`"),
                    Li("📊 Signals: triggers and closers mutate the same Datastar signal"),
                    Li("🎛️ Hooks: use `content_attrs` for inner surface styling and `data_style` to react to `$<id>_open`"),
                    Li("🚫 No globals: all interactivity lives in inline expressions"),
                ),
            ),

            Section(
                "Accessibility",
                Ul(
                    Li("🎯 Focus returns to the trigger once the dialog closes"),
                    Li("⌨️ ESC and backdrop clicks can be toggled via parameters"),
                    Li("🔖 `aria-*` wiring keeps triggers and dialog content associated"),
                ),
            ),

            BackLink(),
            signals=Signals(message=""),
        )
