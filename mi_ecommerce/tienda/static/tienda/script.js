document.addEventListener('DOMContentLoaded', () => {
    // Selectores del DOM
    const productItems = document.querySelectorAll('.product-item');
    const summaryList = document.getElementById('summary-list');
    const summaryTotal = document.getElementById('summary-total');
    const checkoutButton = document.getElementById('checkoutButton');
    const searchInput = document.getElementById('searchInput');

    // Objeto para almacenar el estado del carrito (productos y cantidades)
    const cart = {};

    /**
     * Parsea una cadena de precio a un número de punto flotante.
     * Maneja formatos con comas o puntos.
     * @param {string} priceString - La cadena de texto del precio.
     * @returns {number} El precio como un número.
     */
    const parsePrice = (priceString) => {
        if (!priceString) {
            return 0;
        }
        // Elimina todos los caracteres que no sean dígitos o comas
        const cleanedPrice = priceString.replace(/[^\d,]/g, '');
        // Reemplaza la coma por un punto para un parseo correcto
        const finalPrice = cleanedPrice.replace(',', '.');
        const parsedPrice = parseFloat(finalPrice);
        // Devuelve 0 si el resultado no es un número válido
        return isNaN(parsedPrice) ? 0 : parsedPrice;
    };

    /**
     * Actualiza la interfaz del resumen de compra.
     * Muestra los productos, calcula el total y habilita/deshabilita el botón de compra.
     */
    const updateSummary = () => {
        summaryList.innerHTML = '';
        let total = 0;

        // Formato para moneda local (pesos argentinos)
        const formatter = new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS',
            minimumFractionDigits: 2,
        });

        const cartKeys = Object.keys(cart);
        // Si el carrito está vacío, muestra un mensaje y deshabilita el botón
        if (cartKeys.length === 0) {
            summaryList.innerHTML = '<p class="empty-message">Tu carrito está vacío. ¡Agrega productos para comenzar! 🛒</p>';
            summaryTotal.textContent = 'Total: $0.00';
            checkoutButton.disabled = true;
        } else {
            // Itera sobre los productos en el carrito para construir el resumen
            for (const key in cart) {
                const item = cart[key];
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                const presentationText = item.presentation ? ` (${item.presentation})` : '';
                const contentText = item.content ? ` - ${item.content}` : '';

                const summaryItem = document.createElement('div');
                summaryItem.className = 'summary-item';
                summaryItem.innerHTML = `
                    <span>${item.name}${presentationText}${contentText} (${item.quantity})</span>
                    <span>${formatter.format(itemTotal)}</span>
                `;
                summaryList.appendChild(summaryItem);
            }
            summaryTotal.textContent = `Total: ${formatter.format(total)}`;
            checkoutButton.disabled = false;
        }

        // Agrega o quita la clase 'empty' para cambiar el estilo del total
        summaryTotal.classList.toggle('empty', total === 0);
    };

    // Evento para el botón de finalizar compra
    checkoutButton.addEventListener('click', () => {
        // Alerta de confirmación, se podría reemplazar por una lógica de procesamiento real
        alert('¡Compra finalizada! Total: ' + summaryTotal.textContent);
        // Limpia el carrito y actualiza la UI
        Object.keys(cart).forEach(key => delete cart[key]);
        updateSummary();
        // Restablece los displays de cantidad a 0 en el catálogo
        productItems.forEach(item => {
            item.querySelector('.quantity-display').textContent = '0';
        });
    });

    // Asigna los eventos de click a todos los botones de añadir y quitar productos
    productItems.forEach(item => {
        const id = item.dataset.id;
        const name = item.dataset.nombre;
        const presentation = item.dataset.presentacion ?? '';
        const content = item.dataset.contenido ?? '';
        const price = parsePrice(item.dataset.precio);

        // Se usa una clave única para productos con la misma ID pero diferente presentación
        const uniqueKey = `${id}-${presentation}`;

        const quantityDisplay = item.querySelector('.quantity-display');
        const addButton = item.querySelector('.btn-add');
        const removeButton = item.querySelector('.btn-remove');

        addButton.addEventListener('click', () => {
            // Inicializa el producto en el carrito si no existe
            if (!cart[uniqueKey]) {
                cart[uniqueKey] = { name, price, presentation, content, quantity: 0 };
            }
            cart[uniqueKey].quantity += 1;
            quantityDisplay.textContent = cart[uniqueKey].quantity;
            updateSummary();
        });

        removeButton.addEventListener('click', () => {
            // Decrementa la cantidad si es mayor que cero
            if (cart[uniqueKey] && cart[uniqueKey].quantity > 0) {
                cart[uniqueKey].quantity -= 1;
                // Si la cantidad llega a cero, elimina el producto del carrito
                if (cart[uniqueKey].quantity === 0) {
                    delete cart[uniqueKey];
                }
                quantityDisplay.textContent = cart[uniqueKey] ? cart[uniqueKey].quantity : 0;
                updateSummary();
            }
        });
    });

    // Evento de búsqueda en tiempo real
    searchInput.addEventListener('input', (event) => {
        const searchTerm = event.target.value.toLowerCase();
        productItems.forEach(item => {
            const productName = item.dataset.nombre.toLowerCase();
            // Muestra u oculta el elemento según el término de búsqueda
            if (productName.includes(searchTerm)) {
                item.classList.remove('hidden');
            } else {
                item.classList.add('hidden');
            }
        });
    });
});