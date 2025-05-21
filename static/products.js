// Απόκριση για "Like"
function setupLikeButtons() {
  document.querySelectorAll("button[data-id]").forEach(btn => {
    btn.addEventListener("click", () => {
      fetch(`/products/${btn.dataset.id}/like`, {
  method: "PATCH",
  headers: {
    "Content-Type": "application/json"
  }
})

        .then(() => alert("Έκανες like!"));
    });
  });
}

// Εμφάνιση προϊόντων
function renderProducts(data) {
  const results = document.getElementById("results");
  results.innerHTML = ""; // Καθαρισμός πριν την εισαγωγή νέων

  data.forEach(product => {
    const div = document.createElement("div");
    div.classList.add("product-card");

 div.innerHTML = `
  <div class="like-icon" data-id="${product._id}">${product.liked ? '❤️' : '♡'}</div>
  <img src="/images/${product.image}" width="100" onerror="this.src='/static/fallback.jpg'"><br>
  <strong>${product.name}</strong><br>
  ${product.description}<br>
  Τιμή: ${product.price}€<br>
  Likes: <span class="like-count">${product.like ?? 0}</span>
`;

    results.appendChild(div);
  });

  function setupLikeButtons() {
  document.querySelectorAll(".like-icon").forEach(icon => {
    icon.addEventListener("click", () => {
      const id = icon.dataset.id;

      fetch(`/products/${id}/like`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" }
      })
        .then(() => {
          // toggle like icon
          icon.classList.toggle("liked");
          const isLiked = icon.classList.contains("liked");
          icon.textContent = isLiked ? "❤️" : "♡";

          // optionally increment like count
          const likeCount = icon.parentElement.querySelector(".like-count");
          if (likeCount) {
            let current = parseInt(likeCount.textContent);
            likeCount.textContent = isLiked ? current + 1 : current - 1;
          }
        });
    });
  });
}
setupLikeButtons();

}

// Φόρτωση όλων των προϊόντων κατά την εκκίνηση
function loadAllProducts() {
  fetch("/products/search")
    .then(res => res.json())
    .then(renderProducts);
}

// Αναζήτηση με το κουμπί
document.getElementById("search-button").addEventListener("click", () => {
  const query = document.getElementById("search-input").value;

  fetch(`/products/search?name=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(renderProducts);
});

// Εκκίνηση με όλα τα προϊόντα
loadAllProducts();

// Slideshow στην αρχική (homepage.html)
document.addEventListener("DOMContentLoaded", () => {
  const slideshow = document.getElementById("slideshow");
  if (slideshow) {
    fetch("/products/popular-products")
      .then(res => res.json())
      .then(products => {
        slideshow.innerHTML = ""; // Καθαρισμός slideshow

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
});
