"""
RustyTags Datastar Integration - Python API Layer

This module provides action generators and utilities for working with Datastar
in a pythonic way, similar to the official Datastar Python SDK.
"""

import json
from typing import Any, Dict, Union
from urllib.parse import urlencode
from datastar_py.attributes import attribute_generator
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode, EventType
from .utils import AttrDict


class DS:
    """
    Datastar action generators for common patterns.
    
    This class provides static methods that generate JavaScript expressions
    for common Datastar actions, making it easier to work with Datastar
    from Python without writing raw JavaScript.
    """
    
    @staticmethod
    def get(url: str, **params) -> str:
        """
        Generate a @get() action for fetching data.
        
        Args:
            url: The URL to fetch from
            target: Optional target selector for where to place the response
            **params: Query parameters to append to the URL
            
        Returns:
            JavaScript expression string for the @get action
            
        Example:
            DS.get("/api/data", target="#content", page=1, limit=10)
            # Returns: "@get('/api/data?page=1&limit=10') @target('#content')"
        """
        if params:
            url = f"{url}?{urlencode(params)}"
        
        action = f"@get('{url}')"
        
        return action
    
    @staticmethod
    def post(url: str, target: str|None = None, data: Union[str, Dict]|None = None, **extra_data) -> str:
        """
        Generate a @post() action for sending data.
        
        Args:
            url: The URL to post to
            target: Optional target selector for where to place the response
            data: Data to send (can be a dict, signal reference, or raw string)
            **extra_data: Additional data fields to merge
            
        Returns:
            JavaScript expression string for the @post action
        """
        action = f"@post('{url}')"
        
        # Handle data parameter
        if data is not None or extra_data:
            combined_data = {}
            
            if isinstance(data, dict):
                combined_data.update(data)
            elif isinstance(data, str):
                # If data is a string, assume it's a signal reference or expression
                if data.startswith('$'):
                    action += f" @data({data})"
                else:
                    action += f" @data('{data}')"
            
            if extra_data:
                combined_data.update(extra_data)
            
            if combined_data and not isinstance(data, str):
                action += f" @data({json.dumps(combined_data)})"
        
        if target:
            action += f" @target('{target}')"
        
        return action
    
    @staticmethod
    def put(url: str, target: str|None = None, data: Union[str, Dict]|None = None, **extra_data) -> str:
        """
        Generate a @put() action for updating data.
        
        Args:
            url: The URL to put to
            target: Optional target selector for where to place the response
            data: Data to send (can be a dict, signal reference, or raw string)
            **extra_data: Additional data fields to merge
            
        Returns:
            JavaScript expression string for the @put action
        """
        action = f"@put('{url}')"
        
        if data is not None or extra_data:
            combined_data = {}
            
            if isinstance(data, dict):
                combined_data.update(data)
            elif isinstance(data, str):
                if data.startswith('$'):
                    action += f" @data({data})"
                else:
                    action += f" @data('{data}')"
            
            if extra_data:
                combined_data.update(extra_data)
            
            if combined_data and not isinstance(data, str):
                action += f" @data({json.dumps(combined_data)})"
        
        if target:
            action += f" @target('{target}')"
        
        return action
    
    @staticmethod
    def delete(url: str, target: str|None = None) -> str:
        """
        Generate a @delete() action.
        
        Args:
            url: The URL to delete
            target: Optional target selector for where to place the response
            
        Returns:
            JavaScript expression string for the @delete action
        """
        action = f"@delete('{url}')"
        if target:
            action += f" @target('{target}')"
        return action
    
    @staticmethod
    def patch(url: str, target: str|None = None, data: Union[str, Dict]|None = None, **extra_data) -> str:
        """
        Generate a @patch() action for partial updates.
        
        Args:
            url: The URL to patch
            target: Optional target selector for where to place the response
            data: Data to send (can be a dict, signal reference, or raw string)
            **extra_data: Additional data fields to merge
            
        Returns:
            JavaScript expression string for the @patch action
        """
        action = f"@patch('{url}')"
        
        if data is not None or extra_data:
            combined_data = {}
            
            if isinstance(data, dict):
                combined_data.update(data)
            elif isinstance(data, str):
                if data.startswith('$'):
                    action += f" @data({data})"
                else:
                    action += f" @data('{data}')"
            
            if extra_data:
                combined_data.update(extra_data)
            
            if combined_data and not isinstance(data, str):
                action += f" @data({json.dumps(combined_data)})"
        
        if target:
            action += f" @target('{target}')"
        
        return action
    
    # Signal manipulation helpers
    @staticmethod
    def set(signal: str, value: Any) -> str:
        """
        Set a signal value.
        
        Args:
            signal: Signal name (without $)
            value: Value to set
            
        Returns:
            JavaScript expression to set the signal
        """
        if isinstance(value, str):
            # Check if it's already an expression or needs quoting
            if value.startswith('$') or value.startswith('@') or any(op in value for op in ['===', '!==', '&&', '||', '()']):
                return f"${signal} = {value}"
            else:
                return f"${signal} = '{value}'"
        elif isinstance(value, bool):
            return f"${signal} = {'true' if value else 'false'}"
        elif isinstance(value, (int, float)):
            return f"${signal} = {value}"
        elif value is None:
            return f"${signal} = null"
        else:
            return f"${signal} = {json.dumps(value)}"
    
    @staticmethod
    def toggle(signal: str) -> str:
        """
        Toggle a boolean signal.
        
        Args:
            signal: Signal name (without $)
            
        Returns:
            JavaScript expression to toggle the signal
        """
        return f"${signal} = !${signal}"
    
    @staticmethod
    def increment(signal: str, amount: Union[int, float] = 1) -> str:
        """
        Increment a numeric signal.
        
        Args:
            signal: Signal name (without $)
            amount: Amount to increment by (default: 1)
            
        Returns:
            JavaScript expression to increment the signal
        """
        return f"${signal} += {amount}"
    
    @staticmethod
    def decrement(signal: str, amount: Union[int, float] = 1) -> str:
        """
        Decrement a numeric signal.
        
        Args:
            signal: Signal name (without $)
            amount: Amount to decrement by (default: 1)
            
        Returns:
            JavaScript expression to decrement the signal
        """
        return f"${signal} -= {amount}"
    
    @staticmethod
    def append(signal: str, value: Any) -> str:
        """
        Append to an array signal.
        
        Args:
            signal: Signal name (without $)
            value: Value to append
            
        Returns:
            JavaScript expression to append to the signal array
        """
        if isinstance(value, str) and not (value.startswith('$') or value.startswith('@')):
            return f"${signal}.push('{value}')"
        else:
            return f"${signal}.push({json.dumps(value) if not isinstance(value, str) else value})"
    
    @staticmethod
    def remove(signal: str, index: Union[int, str, None] = None, value: Any = None) -> str:
        """
        Remove from an array signal.
        
        Args:
            signal: Signal name (without $)
            index: Index to remove (if specified)
            value: Value to find and remove (if specified, used instead of index)
            
        Returns:
            JavaScript expression to remove from the signal array
        """
        if index is not None:
            return f"${signal}.splice({index}, 1)"
        elif value is not None:
            value_expr = json.dumps(value) if not isinstance(value, str) or not value.startswith('$') else value
            return f"${signal}.splice(${signal}.indexOf({value_expr}), 1)"
        else:
            return f"${signal}.pop()"
    
    # Utility methods for complex actions
    @staticmethod
    def chain(*actions) -> str:
        """
        Chain multiple actions together.
        
        Args:
            *actions: Actions to chain
            
        Returns:
            JavaScript expression with chained actions
        """
        return '; '.join(str(action) for action in actions if action)
    
    @staticmethod
    def conditional(condition: str, true_action: str, false_action: str|None = None) -> str:
        """
        Create a conditional action.
        
        Args:
            condition: JavaScript condition
            true_action: Action to execute if condition is true
            false_action: Action to execute if condition is false (optional)
            
        Returns:
            JavaScript ternary expression
        """
        if false_action:
            return f"{condition} ? ({true_action}) : ({false_action})"
        else:
            return f"{condition} && ({true_action})"


# Convenience functions for common patterns
def signals(**kwargs) -> Dict[str, Any]:
    """
    Create a signals dictionary for ds_signals attribute.
    
    Args:
        **kwargs: Signal name/value pairs
        
    Returns:
        Dictionary suitable for ds_signals
        
    Example:
        signals(count=0, user={"name": "", "email": ""})
    """
    return kwargs

class Signals(AttrDict):
    """
    A dictionary of signals with reactive capabilities.
    """
    ...

def reactive_class(**conditions) -> Dict[str, str]:
    """
    Create a reactive class dictionary for cls attribute.
    
    Args:
        **conditions: CSS class name -> condition pairs
        
    Returns:
        Dictionary suitable for reactive cls attribute
        
    Example:
        reactive_class(active="$isActive", disabled="$count === 0")
    """
    return conditions


# Export all public items
__all__ = [
    'DS',
    'signals', 
    'Signals',
    'reactive_class',
    'attribute_generator',
    'SSE',
    'ElementPatchMode',
    'EventType'
]