// ---------- AUTHENTICATION ----------
// Load cart from localStorage
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// Update cart count when page loads
updateCartCount();


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

function addToCart(name, price) {

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

    alert(name + " added to cart.");
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
