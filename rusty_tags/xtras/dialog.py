from typing import Any, Callable, Dict, Optional

import rusty_tags as rt
from rusty_tags.datastar import Signals

from .utils import generate_component_id

DialogContext = Dict[str, Any]


def _resolve_component_id(raw_id: Optional[str]) -> str:
    """Return a stable component identifier."""
    return raw_id or generate_component_id("dialog")


def _call_with_context(child: Any, context: DialogContext) -> Any:
    """Invoke closure-based children with the dialog context."""
    return child(context) if callable(child) else child


def _merge_classes(*parts: Optional[str]) -> Optional[str]:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(segment for segment in str(part).split() if segment)
    return " ".join(tokens) or None


def Dialog(
    *children: Any,
    id: Optional[str] = None,
    default_open: bool = False,
    modal: bool = True,
    close_on_escape: bool = True,
    close_on_backdrop: bool = True,
    element_id: Optional[str] = None,
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString:
    """Headless dialog wrapper built on the native ``<dialog>`` element.

    ``id`` becomes the basis for internal state (``$<id>_open``) and can also
    seed the dialog element's ``id`` via ``element_id``. Consumers no longer
    need to decide on signal names manually.
    """

    component_id = _resolve_component_id(id)
    signal_name = f"{component_id}_open"
    dialog_element_id = element_id or component_id

    context: DialogContext = {
        "component_id": component_id,
        "signal": signal_name,
        "modal": modal,
        "close_on_escape": close_on_escape,
        "close_on_backdrop": close_on_backdrop,
        "default_open": default_open,
        "dialog_id": dialog_element_id,
    }

    processed_children = [_call_with_context(child, context) for child in children]

    container_attrs = dict(attrs)
    container_cls = _merge_classes(cls, container_attrs.pop("cls", ""))
    if container_cls:
        container_attrs["cls"] = container_cls
    container_attrs.setdefault("data-attr-data-open", f"${signal_name} ? 'true' : 'false'")

    return rt.Div(
        *processed_children,
        signals=Signals(**{signal_name: default_open}),
        **container_attrs,
    )


def DialogTrigger(
    *children: Any,
    toggles: str|None = None,
    as_modal: bool = False,
    cls: str = "",
    **attrs: Any,
) -> Callable[[DialogContext], rt.HtmlString]:
    """Interactive control that opens the dialog."""
    if toggles is None:
        raise ValueError("DialogTrigger requires a 'toggles' argument")
    showAction = 'showModal' if as_modal else 'show'
    toggle_action = f"${toggles} ? document.getElementById('{toggles}').{showAction}() : document.getElementById('{toggles}').close(); ${toggles} = !${toggles};"
    sigs = Signals(**{toggles: 'false'})

    def create_trigger(context: DialogContext) -> rt.HtmlString:
        signal = context["signal"]
        dialog_id = context["dialog_id"]

        button_attrs = dict(attrs)
        existing_cls = button_attrs.pop("cls", "")
        user_handler = button_attrs.pop("on_click", "").strip()
        button_type = button_attrs.pop("type", None)
        handler_parts = [user_handler, toggle_action] if user_handler else [toggle_action]

        button_attrs["on_click"] = "; ".join(part for part in handler_parts if part)
        button_attrs.setdefault("type", button_type or "button")
        button_attrs.setdefault("aria-haspopup", "dialog")
        button_attrs.setdefault("aria-controls", dialog_id)
        button_attrs.setdefault("data-attr-aria-expanded", f"${signal} ? 'true' : 'false'")

        merged_cls = _merge_classes(cls, existing_cls)
        if merged_cls:
            button_attrs["cls"] = merged_cls

        return rt.Button(
            *children,
            signals=sigs,
            **button_attrs,
        )

    return create_trigger


def DialogContent(
    *children: Any,
    cls: str = "",
    content_attrs: Optional[Dict[str, Any]] = None,
    dialog_cls: str = "",
    **attrs: Any,
) -> Callable[[DialogContext], rt.HtmlString]:
    """Native ``<dialog>`` surface controlled by the shared signal."""

    def create_content(context: DialogContext) -> rt.HtmlString:
        signal = context["signal"]
        modal = context["modal"]
        close_on_escape = context["close_on_escape"]
        close_on_backdrop = context["close_on_backdrop"]
        dialog_id = context["dialog_id"]
        default_open = context["default_open"]

        show_call = "this.showModal()" if modal else "this.show()"
        hide_call = "this.close()"

        dialog_attrs = {
            "id": dialog_id,
            "aria-modal": "true" if modal else "false",
            # "data_attr_open": f"${signal} ? '' : null",
            # "data_effect": (
            #     f"if (${signal}) {{ if (!this.open) {show_call}; }} "
            #     f"else if (this.open) {{ {hide_call}; }}"
            # ),
            # "data_on_close": f"${signal} = false",
        }

        if default_open:
            dialog_attrs["open"] = ""

        if close_on_escape:
            dialog_attrs["data_on_cancel"] = f"${signal} = false"
        else:
            dialog_attrs["data_on_keydown"] = (
                "if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); }"
            )
            dialog_attrs["data_on_cancel"] = "event.preventDefault()"

        if close_on_backdrop:
            dialog_attrs["data_on_click"] = (
                f"if (event.target === event.currentTarget) ${signal} = false"
            )
        else:
            dialog_attrs["data_on_click"] = (
                "if (event.target === event.currentTarget) event.preventDefault()"
            )

        dialog_attributes = {**dialog_attrs, **attrs}
        dialog_existing_cls = dialog_attributes.pop("cls", "")
        merged_dialog_cls = _merge_classes(dialog_cls, dialog_existing_cls)
        if merged_dialog_cls:
            dialog_attributes["cls"] = merged_dialog_cls

        inner_attrs = dict(content_attrs or {})
        inner_existing_cls = inner_attrs.pop("cls", "")
        merged_inner_cls = _merge_classes(cls, inner_existing_cls)
        if merged_inner_cls:
            inner_attrs["cls"] = merged_inner_cls
        inner_attrs.setdefault("role", "document")

        processed_children = [_call_with_context(child, context) for child in children]
        inner_content = rt.Div(
            *processed_children,
            **inner_attrs,
        )

        return rt.Dialog(
            inner_content,
            **dialog_attributes,
        )

    return create_content


def DialogHeader(
    *children: Any,
    cls: str = "",
    **attrs: Any,
) -> Callable[[DialogContext], rt.HtmlString]:
    """Header container for titles and dismiss actions."""

    def create_header(context: DialogContext) -> rt.HtmlString:
        header_attrs = dict(attrs)
        header_cls = _merge_classes(cls, header_attrs.pop("cls", ""))
        if header_cls:
            header_attrs["cls"] = header_cls

        processed_children = [_call_with_context(child, context) for child in children]
        return rt.Header(
            *processed_children,
            **header_attrs,
        )

    return create_header


def DialogTitle(
    *children: Any,
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString:
    """Semantic title element for dialogs."""

    title_attrs = dict(attrs)
    title_cls = _merge_classes(cls, title_attrs.pop("cls", ""))
    if title_cls:
        title_attrs["cls"] = title_cls

    return rt.H2(
        *children,
        **title_attrs,
    )


def DialogBody(
    *children: Any,
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString:
    """Scrollable body content for dialogs."""

    body_attrs = dict(attrs)
    body_cls = _merge_classes(cls, body_attrs.pop("cls", ""))
    if body_cls:
        body_attrs["cls"] = body_cls

    return rt.Div(
        *children,
        **body_attrs,
    )


def DialogFooter(
    *children: Any,
    cls: str = "",
    **attrs: Any,
) -> Callable[[DialogContext], rt.HtmlString]:
    """Footer container suited for action buttons."""

    def create_footer(context: DialogContext) -> rt.HtmlString:
        footer_attrs = dict(attrs)
        footer_cls = _merge_classes(cls, footer_attrs.pop("cls", ""))
        if footer_cls:
            footer_attrs["cls"] = footer_cls

        processed_children = [_call_with_context(child, context) for child in children]
        return rt.Footer(
            *processed_children,
            **footer_attrs,
        )

    return create_footer


def DialogClose(
    *children: Any,
    cls: str = "",
    **attrs: Any,
) -> Callable[[DialogContext], rt.HtmlString]:
    """Button helper that closes the dialog by toggling the shared signal."""

    def create_close(context: DialogContext) -> rt.HtmlString:
        signal = context["signal"]
        button_attrs = dict(attrs)
        existing_cls = button_attrs.pop("cls", "")
        user_handler = button_attrs.pop("on_click", "").strip()
        button_type = button_attrs.pop("type", None)
        handler_parts = [user_handler, f"${signal} = false"] if user_handler else [f"${signal} = false"]

        button_attrs["on_click"] = "; ".join(part for part in handler_parts if part)
        button_attrs.setdefault("type", button_type or "button")

        merged_cls = _merge_classes(cls, existing_cls)
        if merged_cls:
            button_attrs["cls"] = merged_cls

        return rt.Button(
            *children,
            **button_attrs,
        )

    return create_close


def ConfirmDialog(
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
) -> rt.HtmlString:
    """Convenience wrapper that assembles a basic confirmation dialog."""

    trigger_kwargs = dict(trigger_attrs or {})
    confirm_base = dict(confirm_attrs or {})
    cancel_base = dict(cancel_attrs or {})
    icon_base = dict(close_icon_attrs or {})

    def confirm_button(context: DialogContext) -> rt.HtmlString:
        signal = context["signal"]
        button_attrs = dict(confirm_base)
        existing_cls = button_attrs.pop("cls", "")
        user_handler = button_attrs.pop("on_click", "").strip()
        button_type = button_attrs.pop("type", None)

        handler_parts: list[str] = []
        if user_handler:
            handler_parts.append(user_handler)
        if on_confirm:
            handler_parts.append(on_confirm)
        handler_parts.append(f"${signal} = false")

        button_attrs["on_click"] = "; ".join(part for part in handler_parts if part)
        button_attrs.setdefault("type", button_type or "button")

        merged_cls = _merge_classes(existing_cls)
        if merged_cls:
            button_attrs["cls"] = merged_cls

        return rt.Button(
            confirm_text,
            **button_attrs,
        )

    cancel_button = DialogClose(cancel_text, **cancel_base)

    return Dialog(
        DialogTrigger(trigger_text, **trigger_kwargs),
        DialogContent(
            DialogHeader(
                DialogTitle(title),
                DialogClose(close_icon, **icon_base),
            ),
            DialogBody(rt.P(message)),
            DialogFooter(
                cancel_button,
                confirm_button,
            ),
        ),
        id=id,
        element_id=element_id,
        **attrs,
    )
