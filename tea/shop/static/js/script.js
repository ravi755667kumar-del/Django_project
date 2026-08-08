// ---------- AUTHENTICATION ----------
// Load cart from localStorage
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// Update cart count when page loads
updateCartCount();
function openLogin(){
    document.getElementById("auth-wrapper").classList.add("active");
}
function closeLogin(){
    document.getElementById("auth-wrapper").classList.remove("active");
}


function switchAuthForm(targetId) {
    document.querySelectorAll('#auth-wrapper .form-section').forEach(section => {
        section.classList.remove('active');
        section.classList.add('hidden'); // Ensure it hides properly
    });

    const targetSection = document.getElementById(targetId);
    targetSection.classList.add('active');
    targetSection.classList.remove('hidden');
}

function enterTeaWorld() {
    document.getElementById('auth-wrapper').classList.add('hidden');
    
    document.body.classList.remove('auth-mode');
    document.body.classList.add('tea-mode');

    const teaWorld = document.getElementById('tea-world-wrapper');
    teaWorld.classList.remove('hidden');
    teaWorld.style.display = 'block'; // Ensure it becomes visible
    teaWorld.classList.add('fade-in');
}

function logOut() {
    document.getElementById('tea-world-wrapper').classList.add('hidden');
    document.getElementById('tea-world-wrapper').style.display = 'none';
    
    document.getElementById('order-form-wrapper').classList.add('hidden');
    document.getElementById('order-form-wrapper').style.display = 'none';

    document.body.classList.remove('tea-mode');
    document.body.classList.add('auth-mode');

    const authWrapper = document.getElementById('auth-wrapper');
    authWrapper.classList.remove('hidden');
    authWrapper.style.display = 'block';

    switchAuthForm('login-section');
}

const searchBox = document.getElementById("searchBox");
const priceFilter = document.getElementById("priceFilter");

if (searchBox && priceFilter) {
    function searchMenu() {
        const search = searchBox.value;
        const filter = priceFilter.value;

        fetch(`/search_menu/?search=${encodeURIComponent(search)}&price_filter=${filter}`)
            .then(response => response.text())
            .then(data => {
                document.getElementById("menu-container").innerHTML = data;
            });
    }
    searchBox.addEventListener("input", searchMenu);
    priceFilter.addEventListener("change", searchMenu);
}

// ---------- MENU & CATEGORIES ----------

function showCategory(category) {
    // Hide all categories
    document.getElementById("hot-category").style.display = "none";
    document.getElementById("cold-category").style.display = "none";
    document.getElementById("snack-category").style.display = "none";

    // Remove active class from all buttons
    document.getElementById("hot-btn").classList.remove("active-tab");
    document.getElementById("cold-btn").classList.remove("active-tab");
    document.getElementById("snack-btn").classList.remove("active-tab");

    // Hide the order only if it exists
    const orderform = document.getElementById("order-form-wrapper");
    if (orderform){
        orderform.style.display ="none";
    }

    // Show selected category (Using 'grid' instead of 'block' to maintain layout)
    document.getElementById(category + "-category").style.display = "grid";
    document.getElementById(category + "-btn").classList.add("active-tab");
}


// ---------- ORDERING SYSTEM ----------

function openOrderForm(teaName) {
    // Hide all tea grids
    document.getElementById("hot-category").style.display = "none";
    document.getElementById("cold-category").style.display = "none";
    document.getElementById("snack-category").style.display = "none";

    // Populate the form with the selected item
    document.getElementById('orderedTeaName').value = teaName;
    document.getElementById('selected-tea-display').innerText = "Currently Ordering: " + teaName;
    
    // Show the order form
    document.getElementById('order-form-wrapper').classList.remove('hidden');
    document.getElementById('order-form-wrapper').style.display = 'block';
}

function closeOrderForm() {
    // Hide the order form
    document.getElementById('order-form-wrapper').classList.add('hidden');
    document.getElementById('order-form-wrapper').style.display = 'none';
    
    // Find out which tab is currently active and show that category again
    const activeBtn = document.querySelector('.menu-left .active-tab');
    if (activeBtn) {
        activeBtn.click(); // Re-trigger the click to show the grid
    } else {
        showCategory('hot'); // Default fallback
    }
}


// ---------- CART SYSTEM ----------

function addToCart(name, price, btn) {

    // Check if item already exists
    let existingItem = cart.find(function(item) {
        return item.name === name;
    });

    if (existingItem) {

        // Increase quantity
        existingItem.quantity++;

    } else {

        // Add new item
        cart.push({
            name: name,
            price: price,
            quantity: 1
        });

    }

    // Save cart
    localStorage.setItem("cart", JSON.stringify(cart));

    // Update cart count
    updateCartCount();

    // Trigger Flying Animation
    if (btn) {
        flyToCart(btn);
    } else {
        if (!sessionStorage.getItem("cartAlertShown")) {
            alert(name + " added to cart.");
            sessionStorage.setItem("cartAlertShown", "true");
        }
    }
}

// Flying Animation Logic
function flyToCart(btnElement) {
    const cartBtn = document.querySelector('.cart-btn');
    if (!cartBtn) return;

    const btnRect = btnElement.getBoundingClientRect();
    const cartRect = cartBtn.getBoundingClientRect();

    const flyer = document.createElement('div');
    flyer.innerHTML = '🍵'; 
    flyer.style.position = 'fixed';
    flyer.style.left = (btnRect.left + btnRect.width / 2 - 10) + 'px';
    flyer.style.top = (btnRect.top + btnRect.height / 2 - 10) + 'px';
    flyer.style.fontSize = '20px';
    flyer.style.zIndex = '9999';
    flyer.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    flyer.style.pointerEvents = 'none';

    document.body.appendChild(flyer);

    // Trigger movement
    requestAnimationFrame(() => {
        // Needs a tiny delay to ensure transition applies
        setTimeout(() => {
            flyer.style.left = (cartRect.left + cartRect.width / 2 - 10) + 'px';
            flyer.style.top = (cartRect.top + cartRect.height / 2 - 10) + 'px';
            flyer.style.transform = 'scale(0.3) rotate(360deg)';
            flyer.style.opacity = '0.2';
        }, 10);
    });

    // Cleanup and bounce the cart icon
    setTimeout(() => {
        flyer.remove();
        cartBtn.style.transition = 'transform 0.2s ease';
        cartBtn.style.transform = 'scale(1.2)';
        
        setTimeout(() => {
            cartBtn.style.transform = 'scale(1)';
        }, 200);
    }, 600);
}

// Open/Close Chat Window
function toggleChat() {
    const chatWindow = document.getElementById("chatWindow");
    chatWindow.classList.toggle("open");
}

// Helper: read a cookie value by name (needed for CSRF token)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Send Message
function sendMessage() {

    const input = document.getElementById("userMessage");

    const message = input.value.trim();

    if (message === "") {
        return;
    }

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `<div class="user-message">${message}</div>`;

    chatBox.innerHTML += `<div class="bot-message" id="typing">🤖 Typing...</div>`;

    chatBox.scrollTop = chatBox.scrollHeight;

    input.value = "";

    fetch("/chat/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify({
            message: message
        })

    })

    .then(response => response.json())

    .then(data => {

        document.getElementById("typing").remove();

        chatBox.innerHTML += `<div class="bot-message">🤖 ${data.reply}</div>`;

        chatBox.scrollTop = chatBox.scrollHeight;

    });

}

function updateCartCount() {

    let totalItems = 0;

    cart.forEach(function(item) {

        totalItems += item.quantity;

    });

    let cartCount = document.getElementById("cart-count");

    if (cartCount) {

        cartCount.innerText = totalItems;

    }

}
function displayCart() {

    let container = document.getElementById("cart-items-container");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    let grandTotal = 0;

    cart.forEach(function(item, index) {

        let total = item.price * item.quantity;

        grandTotal += total;

        container.innerHTML += `
            <div class="cart-item">

                <div>${item.name}</div>

                <div>

                    <button onclick="decreaseQuantity(${index})">-</button>

                    ${item.quantity}

                    <button onclick="increaseQuantity(${index})">+</button>

                </div>

                <div>₹${item.price}</div>

                <div>₹${total}</div>

            </div>
        `;

    });

    document.getElementById("cart-total-price").innerText = grandTotal;

}
function increaseQuantity(index){

    cart[index].quantity++;

    localStorage.setItem("cart", JSON.stringify(cart));

    updateCartCount();

    displayCart();

}
function decreaseQuantity(index){

    cart[index].quantity--;

    if(cart[index].quantity <= 0){

        cart.splice(index,1);

    }

    localStorage.setItem("cart", JSON.stringify(cart));

    updateCartCount();

    displayCart();

}
displayCart();

// Send cart to Django
document.addEventListener("DOMContentLoaded", function () {

    const cartInput = document.getElementById("cartData");

    if (cartInput) {

        cartInput.value = JSON.stringify(cart);

    }

});
// ---------- PROFILE DROPDOWN ----------
function toggleProfileDropdown() {
    document.getElementById('profileDropdown').classList.toggle('show');
}

// Close dropdown if user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.profile-btn') && !event.target.closest('.profile-btn')) {
        var dropdowns = document.getElementsByClassName('profile-dropdown');
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

// ---------- MOUSE TRAIL EFFECT ----------
let lastStarTime = 0;
const STAR_ICONS = ['⭐', '✨', '🌟']; // Customizable trail images/icons

document.addEventListener('mousemove', function(e) {
    const now = Date.now();
    // Throttle the star creation to avoid too many DOM elements
    if (now - lastStarTime < 40) return;
    lastStarTime = now;

    const star = document.createElement('div');
    star.className = 'mouse-trail-star';
    
    // Pick a random star icon from the list
    star.innerHTML = STAR_ICONS[Math.floor(Math.random() * STAR_ICONS.length)];
    
    // Offset by a few pixels so it trails slightly behind the exact cursor tip
    star.style.left = (e.clientX + 10) + 'px';
    star.style.top = (e.clientY + 10) + 'px';
    
    document.body.appendChild(star);
    
    // Remove the star after animation completes (800ms matching CSS)
    setTimeout(() => {
        if (star.parentNode) {
            star.remove();
        }
    }, 800);
});

// ---------- TEXT ROLL HOVER EFFECT ----------
document.addEventListener("DOMContentLoaded", () => {
    const rollTargets = document.querySelectorAll('#main-nav a, .brand-logo h1, .hero h1');

    rollTargets.forEach(target => {
        if (target.classList.contains('roll-container')) return;

        const text = target.innerText.trim();
        if (!text) return;

        // Preserve original innerHTML if it contains icons, but for simplicity we assume text nodes
        // If there's an icon, we might strip it, so let's only do this if it's purely text
        // Actually, we'll just split textContent
        
        target.innerHTML = '';
        target.classList.add('roll-container');

        // Use Array.from or spread operator to correctly handle Unicode emojis (surrogate pairs)
        [...text].forEach((char, index) => {
            const span = document.createElement('span');
            span.classList.add('roll-char');
            span.innerText = char === ' ' ? '\u00A0' : char; // Preserve spacing
            span.setAttribute('data-char', char === ' ' ? '\u00A0' : char);
            
            // Stagger the animation delay for each character
            span.style.transitionDelay = `${index * 0.03}s`;
            
            target.appendChild(span);
        });
    });
});

