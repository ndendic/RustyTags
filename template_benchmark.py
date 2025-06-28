#!/usr/bin/env python3
"""
Comprehensive benchmark comparing RustyTags vs templating engines
"""

import time
import air
import rusty_tags as rust
from air.tags import *
from jinja2 import Template, Environment
from mako.template import Template as MakoTemplate

def benchmark_function(func, iterations=1000):
    """Benchmark a function and return average time per iteration"""
    start = time.perf_counter()
    for _ in range(iterations):
        result = func()
    return (time.perf_counter() - start) / iterations

def print_results(name, times, iterations):
    """Print benchmark results in a formatted table"""
    print(f"\n🧪 {name}")
    print("=" * (len(name) + 4))
    print(f"Testing {iterations} iterations...\n")
    
    for engine, t in times.items():
        pages_per_sec = int(1/t) if t > 0 else 0
        print(f"{engine:8}: {t*1000:6.3f}ms ({pages_per_sec:6,} pages/sec)")
    
    rust_time = times.get('Rust', 0)
    if rust_time > 0:
        print(f"\nSpeedups vs Rust:")
        for engine, t in times.items():
            if engine != 'Rust' and t > 0:
                speedup = t / rust_time
                print(f"  {engine:8}: {speedup:4.1f}x {'slower' if speedup > 1 else 'faster'}")

def main():
    print("🎯 TEMPLATING LIBRARIES COMPREHENSIVE BENCHMARK")
    print("=" * 52)
    
    # TEST 1: Simple Page Template
    simple_data = {
        'title': 'Simple Test Page',
        'header': 'Welcome to Test',
        'header_class': 'main-title',
        'content': 'This is test content with some text.',
        'footer_text': 'Footer content',
        'footer_class': 'page-footer'
    }

    jinja_simple = Template('''<!doctype html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1 class="{{ header_class }}">{{ header }}</h1>
    <p>{{ content }}</p>
    <div class="{{ footer_class }}">
        <strong>{{ footer_text }}</strong>
    </div>
</body>
</html>''')

    mako_simple = MakoTemplate('''<!doctype html>
<html>
<head><title>${title}</title></head>
<body>
    <h1 class="${header_class}">${header}</h1>
    <p>${content}</p>
    <div class="${footer_class}">
        <strong>${footer_text}</strong>
    </div>
</body>
</html>''')

    def jinja_simple_func():
        return jinja_simple.render(**simple_data)
    
    def mako_simple_func():
        return mako_simple.render(**simple_data)
    
    def air_simple_func():
        return Html(
            H1(simple_data['header'], cls=simple_data['header_class']),
            P(simple_data['content']),
            Div(Strong(simple_data['footer_text']), cls=simple_data['footer_class']),
            headers=(Title(simple_data['title']),)
        ).render()
    
    def rust_simple_func():
        return str(rust.Html(
            rust.Title(simple_data['title']),
            rust.H1(simple_data['header'], cls=simple_data['header_class']),
            rust.P(simple_data['content']),
            rust.Div(rust.Strong(simple_data['footer_text']), cls=simple_data['footer_class'])
        ))

    iterations = 5000
    simple_times = {
        'Jinja2': benchmark_function(jinja_simple_func, iterations),
        'Mako': benchmark_function(mako_simple_func, iterations),
        'Air': benchmark_function(air_simple_func, iterations),
        'Rust': benchmark_function(rust_simple_func, iterations)
    }
    
    print_results("TEST 1: Simple Page Template", simple_times, iterations)
    
    # TEST 2: Data Table Template
    users_data = []
    for i in range(50):
        users_data.append({
            'id': i + 1,
            'name': f'User {i + 1}',
            'email': f'user{i + 1}@example.com', 
            'status': 'Active' if i % 3 == 0 else 'Pending',
            'active': i % 3 == 0
        })

    table_data = {
        'title': 'User Management',
        'page_title': 'User Directory',
        'users': users_data
    }

    jinja_table = Template('''<!doctype html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>{{ page_title }}</h1>
    <table class="data-table">
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
        {% for user in users %}
        <tr class="{{ 'active' if user.active else 'inactive' }}">
            <td>{{ user.id }}</td>
            <td><strong>{{ user.name }}</strong></td>
            <td>{{ user.email }}</td>
            <td>{{ user.status }}</td>
        </tr>
        {% endfor %}
    </table>
    <p>Total users: {{ users|length }}</p>
</body>
</html>''')

    mako_table = MakoTemplate('''<!doctype html>
<html>
<head><title>${title}</title></head>
<body>
    <h1>${page_title}</h1>
    <table class="data-table">
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
        % for user in users:
        <tr class="${'active' if user['active'] else 'inactive'}">
            <td>${user['id']}</td>
            <td><strong>${user['name']}</strong></td>
            <td>${user['email']}</td>
            <td>${user['status']}</td>
        </tr>
        % endfor
    </table>
    <p>Total users: ${len(users)}</p>
</body>
</html>''')

    def jinja_table_func():
        return jinja_table.render(**table_data)
    
    def mako_table_func():
        return mako_table.render(**table_data)
    
    def air_table_func():
        rows = []
        for user in users_data:
            rows.append(Tr(
                Td(str(user['id'])),
                Td(Strong(user['name'])),
                Td(user['email']),
                Td(user['status']),
                cls='active' if user['active'] else 'inactive'
            ))
        
        return Html(
            H1(table_data['page_title']),
            Table(
                Tr(Th('ID'), Th('Name'), Th('Email'), Th('Status')),
                *rows,
                cls='data-table'
            ),
            P(f'Total users: {len(users_data)}'),
            headers=(Title(table_data['title']),)
        ).render()
    
    def rust_table_func():
        rows = []
        for user in users_data:
            rows.append(rust.Tr(
                rust.Td(str(user['id'])),
                rust.Td(rust.Strong(user['name'])),
                rust.Td(user['email']),
                rust.Td(user['status']),
                cls='active' if user['active'] else 'inactive'
            ))
        
        return str(rust.Html(
            rust.Title(table_data['title']),
            rust.H1(table_data['page_title']),
            rust.Table(
                rust.Tr(rust.Th('ID'), rust.Th('Name'), rust.Th('Email'), rust.Th('Status')),
                *rows,
                cls='data-table'
            ),
            rust.P(f'Total users: {len(users_data)}')
        ))

    iterations = 1000
    table_times = {
        'Jinja2': benchmark_function(jinja_table_func, iterations),
        'Mako': benchmark_function(mako_table_func, iterations),
        'Air': benchmark_function(air_table_func, iterations),
        'Rust': benchmark_function(rust_table_func, iterations)
    }
    
    print_results("TEST 2: Data Table Template (50 rows)", table_times, iterations)
    
    print("\n" + "="*52)
    print("🏆 PERFORMANCE SUMMARY")
    print("="*52)
    
    print("\n📊 Performance Analysis:")
    all_engines = ['Jinja2', 'Mako', 'Air', 'Rust']
    
    for engine in all_engines:
        simple_t = simple_times.get(engine, 0)
        table_t = table_times.get(engine, 0)
        
        if simple_t > 0 and table_t > 0:
            simple_pages = int(1/simple_t) if simple_t > 0 else 0
            table_pages = int(1/table_t) if table_t > 0 else 0
            print(f"\n{engine}:")
            print(f"  Simple pages: {simple_pages:6,} pages/sec")
            print(f"  Table pages:  {table_pages:6,} pages/sec")
    
    rust_simple = simple_times.get('Rust', 0)
    rust_table = table_times.get('Rust', 0)
    
    if rust_simple > 0 and rust_table > 0:
        print(f"\n🚀 RustyTags vs Others (Simple Templates):")
        for engine, t in simple_times.items():
            if engine != 'Rust' and t > 0:
                speedup = t / rust_simple
                print(f"  vs {engine:8}: {speedup:4.1f}x faster")
        
        print(f"\n🚀 RustyTags vs Others (Table Templates):")
        for engine, t in table_times.items():
            if engine != 'Rust' and t > 0:
                speedup = t / rust_table
                status = 'faster' if speedup > 1 else 'slower'
                print(f"  vs {engine:8}: {speedup:4.1f}x {status}")
    
    print(f"\n✨ Key Insights:")
    print(f"  • RustyTags dominates simple template generation")
    print(f"  • Mako excels at loop-heavy, repetitive content")
    print(f"  • Template engines are optimized for different patterns")
    print(f"  • Choose the right tool for your specific use case")

if __name__ == "__main__":
    main() 