// =====================================================
// LOGIN PAGE — Static JavaScript
// Only functions actually used by login.html
// =====================================================

// Clear cart on every fresh visit to the login page
localStorage.removeItem("cart");

// ---- Helper: go back to registration form from OTP step ----
function showSignupDetails() {
    document.getElementById('signup-details').style.display = 'block';
    document.getElementById('signup-otp').style.display = 'none';
}

// ---- Hamburger / Mobile Nav ----
function toggleMobileMenu() {
    const nav = document.getElementById('main-nav');
    const btn = document.getElementById('hamburger-btn');
    nav.classList.toggle('mobile-open');
    btn.classList.toggle('open');
}

function closeMobileMenu() {
    const nav = document.getElementById('main-nav');
    const btn = document.getElementById('hamburger-btn');
    nav.classList.remove('mobile-open');
    btn.classList.remove('open');
}

// Close login panel when clicking outside it
document.addEventListener('click', function(e) {
    const panel = document.getElementById('auth-wrapper');
    if (panel && panel.classList.contains('active') &&
        !panel.contains(e.target) &&
        !e.target.closest('[onclick*="openLogin"]')) {
        closeLogin();
    }
});

// ==========================================
// Particle Disintegration Effect on Submit
// ==========================================
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        
        // --- Custom Email Spelling Check for Signup Form ---
        if (form.id === 'signupForm') {
            const emailInput = document.getElementById('signupEmail');
            if (emailInput && emailInput.value) {
                const email = emailInput.value.toLowerCase();
                // Check for common gmail typos
                if (/@(gamil\.com|gmal\.com|gmail\.con|gmai\.com|gmail\.co|gamil\.con)$/.test(email)) {
                    e.preventDefault();
                    alert("It looks like there's a typo in your email domain (e.g., @gmail.com). Please fix it before sending the OTP.");
                    emailInput.focus();
                    return; // Stop form submission
                }
                
                // Hide email text and change background color when processing
                emailInput.style.color = 'transparent';
                emailInput.style.backgroundColor = '#e0f7fa'; // light cyan color
                emailInput.style.transition = 'background-color 0.3s ease';
            }
        }
        // ---------------------------------------------------

        e.preventDefault();

        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.innerHTML = 'Wait...';
            btn.disabled = true;
        }

        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        let canvases = [];
        let allParticles = [];

        inputs.forEach(input => {
            if (!input.value) return;

            const rect = input.getBoundingClientRect();
            const canvas = document.createElement('canvas');
            canvas.width = rect.width;
            canvas.height = rect.height;
            canvas.style.position = 'fixed';
            canvas.style.left = rect.left + 'px';
            canvas.style.top = rect.top + 'px';
            canvas.style.pointerEvents = 'none';
            canvas.style.zIndex = '9999';
            document.body.appendChild(canvas);
            canvases.push(canvas);

            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            const style = window.getComputedStyle(input);
            ctx.font = style.font;
            ctx.fillStyle = style.color;
            ctx.textBaseline = 'middle';

            const paddingLeft = parseFloat(style.paddingLeft);
            const height = rect.height;
            const text = input.type === 'password' ? '•'.repeat(input.value.length) : input.value;
            ctx.fillText(text, paddingLeft, height / 2 + 1);
            input.style.color = 'transparent';

            const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imgData.data;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let y = 0; y < canvas.height; y += 2) {
                for (let x = 0; x < canvas.width; x += 2) {
                    const idx = (y * canvas.width + x) * 4;
                    if (data[idx + 3] > 128) {
                        allParticles.push({
                            x, y,
                            vx: (Math.random() - 0.5) * 8,
                            vy: (Math.random() - 0.5) * 8 - 2,
                            color: `rgba(${data[idx]}, ${data[idx+1]}, ${data[idx+2]}, 1)`,
                            life: 1.0,
                            ctx
                        });
                    }
                }
            }
        });

        function animateParticles() {
            canvases.forEach(c => c.getContext('2d').clearRect(0, 0, c.width, c.height));
            let alive = false;
            allParticles.forEach(p => {
                if (p.life <= 0) return;
                alive = true;
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.4;
                p.life -= 0.02;
                p.ctx.fillStyle = p.color.replace('1)', `${Math.max(0, p.life)})`);
                p.ctx.fillRect(p.x, p.y, 2.5, 2.5);
            });
            if (alive) requestAnimationFrame(animateParticles);
            else form.submit();
        }

        if (allParticles.length > 0) animateParticles();
        else form.submit();

        setTimeout(() => { form.submit(); }, 1500);
    });
});

// ==========================================
// Auth Required URL Parameter Handler
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_required') === '1') {
        openLogin();
        const loginMsgBox = document.querySelector('#login-section .message-box');
        if (loginMsgBox) {
            loginMsgBox.innerHTML = '<p style="color:#ff4757;font-weight:bold;background:rgba(255,71,87,0.1);padding:10px;border-radius:8px;margin-top:15px;">⚠️ Please register or login first!</p>';
        }
    }
});
