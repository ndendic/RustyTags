import rusty_tags as rt


def Icon(icon: str, 
         lucide: bool = True, 
         cls: str = "", 
         width: str = "16", 
         height: str = "16", 
         **attrs
    ) -> rt.HtmlString:
    style_attrs = f"width: {width}; height: {height};"        
    if lucide:
        return rt.I(rt.Script("lucide.createIcons();"), data_lucide=icon,width=width,height=height, cls=cls, **attrs)
    else:
        attrs.update({"style": style_attrs})    
        return rt.I(icon, cls=cls, **attrs)
        