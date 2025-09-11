import rusty_tags as rt
from typing import Literal

# input[type="date"],
#                 input[type="datetime-local"],
#                 input[type="email"],
#                 input[type="month"],
#                 input[type="number"],
#                 input[type="password"],
#                 input[type="search"],
#                 input[type="tel"],
#                 input[type="text"],
#                 input[type="time"],
#                 input[type="url"],
#                 input[type="week"]

def Input(
        label, 
        type:Literal['date', 'datetime-local', 'email', 'month', 'number', 'password', 'search', 'tel', 'text', 'time', 'url', 'week'] = 'text', 
        placeholder:str = '', 
        supporting_text:str = '', 
        *args, **kwargs
    ):
    """
    Open Props UI compatible text field component.
    
    Args:
        label: The floating label text (this becomes the floating label)
        type: Input type (default: 'text')
        placeholder: NOT USED - Open Props UI uses floating labels instead of placeholders
        supporting_text: Helper text below the input
    """
    # For Open Props UI floating labels, we need an empty placeholder for the CSS to work
    # The label parameter becomes the floating label, not the placeholder
    placeholder = ' '
    
    return rt.Label(
        rt.Span(label, cls='label'),
        rt.Input(type=type, placeholder=placeholder, *args, **kwargs),
        rt.Span(supporting_text, cls='supporting-text') if supporting_text else "",
        cls='field',
    )