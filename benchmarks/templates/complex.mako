<!doctype html>
<html lang="${lang}">
<head><title>${title}</title></head>
<body>
<div class="page-container">
    <header class="site-header">
        <h1>${heading}</h1>
        <nav class="main-nav">
            <ul>
            % for link in nav_links:
                <li><a href="${link['url']}">${link['text']}</a></li>
            % endfor
            </ul>
        </nav>
    </header>
    <main class="main-content">
        <section class="content">
            <h2>${section_title}</h2>
            <p>${description}</p>
            <ul class="features">
            % for feature in features:
                <li>${feature}</li>
            % endfor
            </ul>
        </section>
    </main>
    <footer class="site-footer">
        <p>${footer_text}</p>
    </footer>
</div>
</body>
</html>