// -------------------------------------------------------------
// script.js — wszystkie skrypty strony w jednym miejscu
// -------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  // ──────────────────────────────────────────────────────────────
  // 1. Ładowanie i inicjalizacja menu (nav.html)
  // ──────────────────────────────────────────────────────────────
  fetch("static/nav.html")
    .then(resp => resp.text())
    .then(html => {
      const placeholder = document.getElementById("nav-placeholder");
      placeholder.innerHTML = html;

      // Mobile menu toggle
      const btn    = document.getElementById("menu-button");
      const mobile = document.getElementById("mobile-menu");
      btn.addEventListener("click", () => {
        const isOpen = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", String(!isOpen));
        mobile.classList.toggle("show");
      });
    })
    .catch(err => console.error("Nav load error:", err));

  // ──────────────────────────────────────────────────────────────
  // 2. Cookie widget — ikonka i panel
  // ──────────────────────────────────────────────────────────────
  const cookieIcon    = document.getElementById("cookieIcon");
  const cookiePanel   = document.getElementById("cookiePanel");
  const cookieClose   = document.getElementById("cookieClose");
  const cookieAccept  = document.getElementById("cookieAccept");

  // Pokaż/ukryj panel
  cookieIcon.addEventListener("click", () => {
    cookiePanel.classList.toggle("open");
  });
  // Zamknij panel
  cookieClose.addEventListener("click", () => {
    cookiePanel.classList.remove("open");
  });
  // Akceptacja ciasteczek — tu możesz zapisać do localStorage
  cookieAccept.addEventListener("click", () => {
    // localStorage.setItem("cookiesAccepted", "true");
    cookiePanel.classList.remove("open");
  });

  // ──────────────────────────────────────────────────────────────
  // 3. Baner polityki prywatności
  // ──────────────────────────────────────────────────────────────
  const privacyBanner = document.getElementById("privacy-banner");
  const privacyBtn    = document.getElementById("privacy-accept");

  // Pokaż baner tylko raz (jeśli nie zaakceptowano wcześniej)
  if (!localStorage.getItem("privacyAccepted")) {
    privacyBanner.classList.remove("hidden");
  }
  // Akceptacja
  privacyBtn.addEventListener("click", () => {
    localStorage.setItem("privacyAccepted", "true");
    privacyBanner.classList.add("hidden");
  });

  // ──────────────────────────────────────────────────────────────
  // 4. Interaktywne tagi w sekcji 'location'
  // ──────────────────────────────────────────────────────────────
  const facilityTags = document.querySelectorAll(".facility-tag");
  facilityTags.forEach(tag => {
    tag.addEventListener("mouseenter", () => {
      tag.style.backgroundColor = "rgba(139, 92, 246, 0.2)";
    });
    tag.addEventListener("mouseleave", () => {
      tag.style.backgroundColor = "rgba(139, 92, 246, 0.1)";
    });
  });

  // ──────────────────────────────────────────────────────────────
  // 5. (Opcjonalnie) Inne skrypty — np. formularze, galerie itd.
  //    Możesz dodać tutaj kolejne bloki w podobnej strukturze.
  // ──────────────────────────────────────────────────────────────
});
document.addEventListener("DOMContentLoaded", function () {
  const banner = document.getElementById("cookie-banner");
  const acceptButton = document.getElementById("accept-button");

  // Sprawdzenie czy już zaakceptowano
  if (localStorage.getItem("cookiesAccepted") === "true") {
    banner.style.display = "none";
  }

  acceptButton.addEventListener("click", function () {
    localStorage.setItem("cookiesAccepted", "true");
    banner.style.display = "none";
  });
});
