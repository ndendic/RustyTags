from typing import Literal

from rusty_tags import H2 as HTMLH2
from rusty_tags import Div, HtmlString, P, Span, Button
from rusty_tags.datastar import Signals
from rusty_tags.datastar import attribute_generator as data

# Using direct class strings instead of cn utility for Open Props compatibility

SheetSide = Literal["top", "right", "bottom", "left"]
SheetSize = Literal["sm", "md", "lg", "xl", "full"]


def Sheet(
    *children,
    signal: str,
    modal: bool = True,
    default_open: bool = False,
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> HtmlString:
    signal_open = f"{signal}_open"

    scroll_lock = (
        Div(effect=f"document.body.style.overflow = ${signal_open} ? 'hidden' : ''")
        if modal
        else None
    )

    return Div(  # pyright: ignore[reportCallIssue]
        *children,
        scroll_lock,
        **data.on('keydown', f"evt.key === 'Escape' && (${signal_open} = false)").window() if modal else {},
        signals=Signals(**{signal_open: default_open}),
        data_sheet_root=signal,
        data_class=f"{{open: ${signal_open}, closed: !${signal_open}}}",
        cls=f"sheet-root {class_name} {cls}".strip(),
        **attrs,
    )


def SheetTrigger(
    *children,
    signal: str,
    variant: str = "outline",
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> HtmlString:
    # from .button import Button

    signal_open = f"{signal}_open"
    content_id = f"{signal}-content"

    return Button(
        *children,
        on_click=f"${signal_open} = true",
        id=f"{signal}-trigger",
        **{
            "aria-expanded": f"${{{signal_open}}}",
            "aria-haspopup": "dialog",
            "aria-controls": content_id,
            "data-sheet-role": "trigger",
        },
        variant=variant,
        cls=f"{class_name} {cls}".strip(),
        **attrs,
    )


def SheetContent(
        *children,
        signal: str,
        side: SheetSide = "right",
        size: SheetSize = "sm",
        modal: bool = True,
        show_close: bool = True,
        class_name: str = "",
        cls: str = "",
        **attrs,
    ) -> HtmlString:
    signal_open = f"{signal}_open"
    content_id = f"{signal}-content"

    # Positioning and sizing are now handled by CSS using data attributes

    close_button = (
        (
            SheetClose(
                Span(
                    "×",
                    aria_hidden="true",
                    cls="sheet-close-icon",
                ),
                signal=signal,
                size="icon",
                cls="sheet-close-button",
            )
        )
        if show_close
        else None
    )

    overlay = (
        Div(
            on_click=f"${signal_open} = false",
            cls="sheet-overlay",
            data_class=f"{{open: ${signal_open}, closed: !${signal_open}}}",
            data_sheet_role="overlay",
        )
        if modal
        else None
    )

    content_panel = Div(
        close_button or None,
        *children,
        id=content_id,
        role="dialog",
        aria_modal="true" if modal else None, # pyright: ignore[reportArgumentType]
        aria_labelledby=f"{content_id}-title",
        aria_describedby=f"{content_id}-description",
        data_class=f"{{open: ${signal_open}, closed: !${signal_open}}}",
        data_sheet_role="content",
        data_sheet_side=side,
        data_sheet_size=size,
        cls=f"sheet-content {class_name} {cls}".strip(),
        **attrs,
    )

    return Div(
        overlay,
        content_panel,
        # show=f"${signal_open}",
        data_sheet_role="content-wrapper"
    )


def SheetClose(
    *children,
    signal: str,
    variant: str = "ghost",
    size: str = "sm",
    class_name: str = "",
    cls: str = "",
    **attrs,
) -> HtmlString:
    # from .button import Button

    signal_open = f"{signal}_open"

    return Button(
        *children,
        on_click=f"${signal_open} = false",
        data_sheet_role="close",
        variant=variant,
        size=size,
        cls=f"{class_name} {cls}".strip(),
        **attrs,
    )


def SheetHeader(*children, class_name: str = "", cls: str = "", **attrs) -> HtmlString:
    return Div(
        *children,
        data_sheet_role="header",
        cls=f"sheet-header {class_name} {cls}".strip(),
        **attrs,
    )


def SheetFooter(*children, class_name: str = "", cls: str = "", **attrs) -> HtmlString:
    return Div(
        *children,
        data_sheet_role="footer",
        cls=f"sheet-footer {class_name} {cls}".strip(),
        **attrs,
    )


def SheetTitle(
    *children, signal: str, class_name: str = "", cls: str = "", **attrs
) -> HtmlString:
    content_id = f"{signal}-content"

    return HTMLH2(
        *children,
        id=f"{content_id}-title",
        data_sheet_role="title",
        cls=f"sheet-title {class_name} {cls}".strip(),
        **attrs,
    )


def SheetDescription(
    *children, signal: str, class_name: str = "", cls: str = "", **attrs
) -> HtmlString:
    content_id = f"{signal}-content"

    return P(
        *children,
        id=f"{content_id}-description",
        data_sheet_role="description",
        cls=f"sheet-description {class_name} {cls}".strip(),
        **attrs,
    )
