import rusty_tags as rt


def LucideIcon(icon: str, 
         cls: str = "", 
         width: str = "16", 
         height: str = "16", 
         **attrs
    ) -> rt.HtmlString:    
    return rt.I(rt.Script("lucide.createIcons();"), data_lucide=icon,width=width,height=height, cls=cls, **attrs)
        