<div class="product-list">
    <h2>${title}</h2>
    <div class="products">
    % for product in products:
        <div class="product-card" data-id="${product['id']}">
            <h3>${product['name']}</h3>
            <p class="price">$${product['price']}</p>
            <p class="description">${product['description']}</p>
            <div class="tags">
            % for tag in product['tags']:
                <span class="tag">${tag}</span>
            % endfor
            </div>
        </div>
    % endfor
    </div>
</div>