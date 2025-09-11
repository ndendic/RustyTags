from typing import Literal

from rusty_tags import H2 as HTMLH2
from rusty_tags import Div, HtmlString, P, Span, Button
from rusty_tags.datastar import Signals
from rusty_tags.datastar import attribute_generator as data

from rusty_tags.utils import cn

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

    return Div(
        *children,
        scroll_lock,
        **data.on('keydown', f"evt.key === 'Escape' && (${signal_open} = false)").window() if modal else None,
        signals=Signals(**{signal_open: default_open}),
        data_sheet_root=signal,
        data_attr_data_state=f"${signal_open} ? 'open' : 'closed'",
        cls=cn("relative", class_name, cls),
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
        aria_expanded=f"${{{signal_open}}}",
        aria_haspopup="dialog",
        aria_controls=content_id,
        data_sheet_role="trigger",
        variant=variant,
        cls=cn(class_name, cls),
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

    side_classes = {
        "right": "inset-y-0 right-0 h-full border-l translate-x-full opacity-0 data-[state=open]:translate-x-0 data-[state=open]:opacity-100 data-[state=closed]:translate-x-full data-[state=closed]:opacity-0",
        "left": "inset-y-0 left-0 h-full border-r -translate-x-full opacity-0 data-[state=open]:translate-x-0 data-[state=open]:opacity-100 data-[state=closed]:-translate-x-full data-[state=closed]:opacity-0",
        "top": "inset-x-0 top-0 w-full border-b -translate-y-full opacity-0 data-[state=open]:translate-y-0 data-[state=open]:opacity-100 data-[state=closed]:-translate-y-full data-[state=closed]:opacity-0",
        "bottom": "inset-x-0 bottom-0 w-full border-t translate-y-full opacity-0 data-[state=open]:translate-y-0 data-[state=open]:opacity-100 data-[state=closed]:translate-y-full data-[state=closed]:opacity-0",
    }

    size_classes = (
        {
            "sm": "max-w-sm",
            "md": "max-w-md",
            "lg": "max-w-lg",
            "xl": "max-w-xl",
            "full": "max-w-none w-full",
        }
        if side in ["left", "right"]
        else {}
    )

    close_button = (
        (
            SheetClose(
                Span(
                    "×",
                    aria_hidden="true",
                    cls="text-2xl font-light leading-none -mt-0.5",
                ),
                signal=signal,
                size="icon",
                cls="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-secondary",
            )
        )
        if show_close
        else None
    )

    overlay = (
        Div(
            on_click=f"${signal_open} = false",
            cls="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm transition-opacity duration-300 ease-in-out [transition-behavior:allow-discrete] opacity-0 data-[state=open]:opacity-100 data-[state=closed]:opacity-0 data-[state=closed]:pointer-events-none",
            data_attr_data_state=f"${signal_open} ? 'open' : 'closed'",
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
        aria_modal="true" if modal else None,
        aria_labelledby=f"{content_id}-title",
        aria_describedby=f"{content_id}-description",
        data_attr_data_state=f"${signal_open} ? 'open' : 'closed'",
        data_sheet_role="content",
        cls=cn(
            "fixed z-[110] bg-background shadow-lg flex flex-col",
            "transition-all duration-300 ease-in-out",
            "[transition-behavior:allow-discrete]",
            # Start hidden for proper animation
            "data-[state=closed]:pointer-events-none",
            side_classes.get(side, ""),
            size_classes.get(size, ""),
            "overflow-y-auto",
            class_name,
            cls,
        ),
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
        cls=cn(class_name, cls),
        **attrs,
    )


def SheetHeader(*children, class_name: str = "", cls: str = "", **attrs) -> HtmlString:
    return Div(
        *children,
        data_sheet_role="header",
        cls=cn("flex flex-col space-y-1.5 p-6", class_name, cls),
        **attrs,
    )


def SheetFooter(*children, class_name: str = "", cls: str = "", **attrs) -> HtmlString:
    return Div(
        *children,
        data_sheet_role="footer",
        cls=cn(
            "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 p-6",
            class_name,
            cls,
        ),
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
        cls=cn("text-lg font-semibold text-foreground", class_name, cls),
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
        cls=cn("text-sm text-muted-foreground", class_name, cls),
        **attrs,
    )
