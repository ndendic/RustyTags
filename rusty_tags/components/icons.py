import rusty_tags as rt

def Icon(icon: str, 
         lucide: bool = True, 
         cls: str = "", 
         width: str = "1em", 
         height: str = "1en", 
         **attrs
    ) -> rt.HtmlString:
    style_attrs = {
        "style": {
            "width": width,
            "height": height,
        }
    }
    attrs.update(style_attrs)
    if lucide:
        return rt.I(rt.Script("lucide.createIcons();"), data_lucide=icon, **attrs)
    else:
        return rt.I(icon,style=style_attrs, **attrs)