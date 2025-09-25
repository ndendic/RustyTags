"""
Shared utilities and configuration for component documentation pages.
All component documentation pages should import from this module.
"""
import inspect
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags import Section as HTMLSection
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from rusty_tags.xtras import LucideIcon, CodeBlock, Tabs, TabsList, TabsTrigger, TabsContent, Accordion, AccordionItem, Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogBody, DialogFooter, DialogClose, ConfirmDialog
from rusty_tags.xtras.utils import cn
from datastar_py.fastapi import ReadSignals
from datastar_py.consts import ElementPatchMode
from uuid import uuid4
from typing import Any, Callable
from enum import Enum

# Shared header URLs for external dependencies
HEADER_URLS = {
    'franken_css': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/css/core.min.css",
    'franken_js_core': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/core.iife.js",
    'franken_icons': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/icon.iife.js",
    'tailwind': "https://cdn.tailwindcss.com/3.4.16",
    'daisyui': "https://cdn.jsdelivr.net/npm/daisyui@4.12.24/dist/full.min.css",
    'apex_charts': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/chart.iife.js"
}

# Read the xtras CSS content
import os
xtras_css_path = os.path.join(os.path.dirname(__file__), '../../../rusty_tags/xtras/xtras.css')
with open(xtras_css_path, 'r') as f:
    xtras_css = f.read()

# Shared headers for all documentation pages
inspector = Script(src="/static/js/datastar-inspector.js", type="module")
hdrs = (
    Link(rel='stylesheet', href='https://unpkg.com/open-props'),
    Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css", type="text/css"),
    Script("import { load, apply } from 'https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js';\r\n        import AnchorPlugin from 'https://cdn.jsdelivr.net/gh/ndendic/data-satelites@master/dist/min/anchor.min.js';\r\n        load(AnchorPlugin);\r\n        apply();", type='module'),
    # Link(rel='stylesheet', href='https://unpkg.com/open-props/normalize.min.css'),
    Style(f"""
        html {{
            min-height: 100vh;
            color: light-dark(var(--gray-9), var(--gray-1));
            font-family: var(--font-neo-grotesque);
            font-size: var(--font-size-fluid-0);
            letter-spacing: var(--font-letterspacing-1);
        }}
        main {{
            width: min(100% - 2rem, 45rem);
            margin-inline: auto;
        }}
        
        .anchor-container {{
            position: relative;
            height: 300px;
            border: 2px dashed #ccc;
            margin: 20px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
        }}
        
        /* RustyTags Xtras CSS */
        {xtras_css}
    """),
    inspector
)

# Shared HTML and body configuration
htmlkws = dict(lang="en")
bodykws = dict(signals=Signals(message="", conn=""))
ftrs = (
    CustomTag("datastar-inspector"),
    Script("lucide.createIcons();")
)
# Shared page template
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, ftrs=ftrs, highlightjs=True, datastar=False)

def Section(title, *content):
    """Utility function for creating documentation sections"""
    return HTMLSection(
        H2(title),
        *content,
        cls="fluid-flex"
    )

def BackLink(href="/", text="← Back to Home"):
    """Standard back navigation link"""
    return Div(
        A(text, href=href, cls="color-blue-6 text-decoration-underline"),
        cls="mt-8"
    )

def get_code(component: Callable):
    code = ""
    for line in inspect.getsource(component).split("\n"):
        if not line.strip().startswith("def"):
            code += line[4:] + "\n"
    code = code.replace("return ", "")
    return code

def ComponentShowcase(component: Callable):
    return Tabs(
            TabsList(
                TabsTrigger("Preview", id="tab1"),
                TabsTrigger("Code", id="tab2"),
                style="margin-bottom: 1rem;"
            ),
            TabsContent(component(), id="tab1", style="padding: 1rem; border: 1px solid; border-radius: 0.5rem;"),
            TabsContent(CodeBlock(get_code(component), cls="language-python", style="border: 1px solid; border-radius: 0.5rem;"), id="tab2"),
            default_tab="tab1",
        )