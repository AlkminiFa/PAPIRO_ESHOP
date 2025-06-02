// Ενημέρωση αριθμού προϊόντων στο header
function updateCartCount() {
  const cart = JSON.parse(localStorage.getItem("cart")) || [];
  const count = cart.reduce((total, item) => total + (item.quantity || 1), 0);
  const cartCountElement = document.getElementById("cart-count");
  if (cartCountElement) {
    cartCountElement.textContent = count;
  }
}

// Προσθήκη προϊόντος στο καλάθι
function setupCartButtons() {
  document.querySelectorAll(".add-to-cart").forEach(button => {
    button.addEventListener("click", () => {
      const id = button.dataset.id;
      const name = button.dataset.name;
      const price = parseFloat(button.dataset.price);

      let cart = JSON.parse(localStorage.getItem("cart")) || [];
      const existing = cart.find(item => item.id === id);

      if (existing) {
        existing.quantity += 1;
      } else {
        cart.push({ id, name, price, quantity: 1 });
      }

      localStorage.setItem("cart", JSON.stringify(cart));
      updateCartCount();
      alert(`Το προϊόν "${name}" προστέθηκε στο καλάθι.`);
    });
  });
}

// Εμφάνιση προϊόντων
function renderProducts(data) {
  const results = document.getElementById("results");
  results.innerHTML = "";

  data.forEach(product => {
    const div = document.createElement("div");
    div.classList.add("product-card");

    div.innerHTML = `
      <div class="like-icon" data-id="${product._id}">${product.liked ? '❤️' : '♡'}</div>
      <img src="/images/${product.image}" width="100" onerror="this.src='/static/fallback.jpg'"><br>
      <strong>${product.name}</strong><br>
      ${product.description}<br>
      Τιμή: ${product.price}€<br>
      Likes: <span class="like-count">${product.like ?? 0}</span><br>
      <a href="#" class="add-to-cart"
       data-id="${product._id}"
       data-name="${product.name}"
       data-price="${product.price}">
       Προσθήκη στο καλάθι
     </a>
    `;

    results.appendChild(div);
  });

  setupLikeButtons();
  setupCartButtons();
}

// Like λογική
function setupLikeButtons() {
  document.querySelectorAll(".like-icon").forEach(icon => {
    icon.addEventListener("click", () => {
      const id = icon.dataset.id;

      fetch(`/products/${id}/like`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" }
      })
      .then(() => {
        icon.classList.toggle("liked");
        const isLiked = icon.classList.contains("liked");
        icon.textContent = isLiked ? "❤️" : "♡";

        const likeCount = icon.parentElement.querySelector(".like-count");
        if (likeCount) {
          let current = parseInt(likeCount.textContent);
          likeCount.textContent = isLiked ? current + 1 : current - 1;
        }
      });
    });
  });
}

// Αναζήτηση προϊόντος
const searchButton = document.getElementById("search-button");
if (searchButton) {
  searchButton.addEventListener("click", () => {
    const query = document.getElementById("search-input").value;

    fetch(`/products/search?name=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(renderProducts);
  });
}

// Slideshow για την αρχική
function setupSlideshow() {
  const slideshow = document.getElementById("slideshow");
  if (!slideshow) return;

  fetch("/products/popular-products")
    .then(res => res.json())
    .then(products => {
      slideshow.innerHTML = "";
      products.forEach(product => {
        const item = document.createElement("div");
        item.classList.add("slideshow-item");
        item.innerHTML = `
          <img src="/images/${product.image}" width="120" onerror="this.src='/static/fallback.jpg'"><br>
          <strong>${product.name}</strong>
        `;
        slideshow.appendChild(item);
      });
    });
}

// Φόρτωση όλων των προϊόντων
function loadAllProducts() {
  fetch("/products/search")
    .then(res => res.json())
    .then(renderProducts);
}

// Εναλλαγή sidebar για το καλάθι
function setupCartSidebar() {
  const cartLink = document.getElementById("cart-link");
  const cartSidebar = document.getElementById("cart-sidebar");
  const closeCart = document.getElementById("close-cart");
  const cartContent = document.getElementById("cart-content");

  if (cartLink && cartSidebar && closeCart) {
    cartLink.addEventListener("click", (e) => {
      e.preventDefault();
      cartSidebar.classList.add("visible"); 
      displayCartItems(cartContent);
    });

    closeCart.addEventListener("click", () => {
      cartSidebar.classList.remove("visible");
    });
  }
}

//  Εμφάνιση αντικειμένων καλαθιού
function displayCartItems(container) {
  const cart = JSON.parse(localStorage.getItem("cart")) || [];

  if (cart.length === 0) {
    container.innerHTML = `<p>Το καλάθι σας είναι άδειο.</p>`;
    return;
  }

  container.innerHTML = `<ul>` + cart.map(item => `
    <li>
      ${item.name} × ${item.quantity} — ${item.price * item.quantity}€
      <button class="remove-from-cart" data-id="${item.id}">✖</button>
    </li>
  `).join("") + `</ul>`;

  setupRemoveButtons();
}

//  Αφαίρεση προϊόντων από το καλάθι
function setupRemoveButtons() {
  document.querySelectorAll(".remove-from-cart").forEach(button => {
    button.addEventListener("click", () => {
      const id = button.dataset.id;
      let cart = JSON.parse(localStorage.getItem("cart")) || [];

      const item = cart.find(item => item.id === id);
      if (item.quantity > 1) {
        item.quantity -= 1;
      } else {
        cart = cart.filter(item => item.id !== id);
      }

      localStorage.setItem("cart", JSON.stringify(cart));
      updateCartCount();
      displayCartItems(document.getElementById("cart-content"));
    });
  });
}

// Slideshow λογική (βελάκια & τελείες)
let currentSlide = 0;

function moveSlide(direction) {
  const track = document.getElementById("slideshow-track");
  const totalSlides = track.children.length;

  currentSlide += direction;

  if (currentSlide < 0) {
    currentSlide = totalSlides - 1; // Πήγαινε στην τελευταία αν πας πίσω από την πρώτη
  } else if (currentSlide >= totalSlides) {
    currentSlide = 0; // Γύρνα στην αρχή όταν τελειώσουν οι διαφάνειες
  }

  track.style.transform = `translateX(-${currentSlide * 100}%)`;
  updateDots();
}


function goToSlide(index) {
  currentSlide = index;
  const track = document.getElementById("slideshow-track");
  if (track) {
    track.style.transform = `translateX(-${currentSlide * 100}%)`;
  }
  updateDots();
}

function updateDots() {
  const dots = document.querySelectorAll("#slide-dots .dot");
  dots.forEach((dot, index) => {
    dot.classList.toggle("active", index === currentSlide);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("results")) {
    loadAllProducts();
  }

  updateCartCount();
  setupCartSidebar();
  setupSlideshow();
  updateDots();
  startAutoplay(); // Αυτόματη εναλλαγή slide

  const track = document.getElementById("slideshow-track");
  if (track) {
    track.addEventListener("mouseenter", stopAutoplay);
    track.addEventListener("mouseleave", startAutoplay);
  }
});



let autoplayInterval;

function startAutoplay() {
  autoplayInterval = setInterval(() => {
    moveSlide(1);
  }, 4000); // αλλαγή κάθε 4 δευτερόλεπτα
}

function stopAutoplay() {
  clearInterval(autoplayInterval);
}

const track = document.getElementById("slideshow-track");
if (track) {
  track.addEventListener("mouseenter", stopAutoplay);
  track.addEventListener("mouseleave", startAutoplay);
}
