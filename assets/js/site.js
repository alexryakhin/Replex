// Replex landing page: header hairline on scroll, reveal-on-scroll, language switcher and
// App Store click events. Everything works without it; this only adds polish.
(function () {
  document.documentElement.classList.add("js");

  var bar = document.querySelector(".bar");
  function onScroll() {
    if (bar) bar.classList.toggle("scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    items.forEach(function (item) { observer.observe(item); });
  } else {
    items.forEach(function (item) { item.classList.add("in"); });
  }

  // Language picker: remember the choice (the English pages' auto-redirect then follows it), and
  // close when clicking outside or pressing Escape.
  var picker = document.querySelector("details.lang");
  if (picker) {
    picker.querySelectorAll("a[hreflang]").forEach(function (link) {
      link.addEventListener("click", function () {
        try { localStorage.setItem("replex.lang", link.getAttribute("hreflang").toLowerCase()); } catch (e) {}
      });
    });
    document.addEventListener("click", function (event) {
      if (picker.open && !picker.contains(event.target)) picker.open = false;
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && picker.open) {
        picker.open = false;
        picker.querySelector("summary").focus();
      }
    });
  }

  document.querySelectorAll("[data-cta]").forEach(function (link) {
    link.addEventListener("click", function () {
      if (typeof window.gtag === "function") {
        window.gtag("event", "app_store_click", { placement: link.getAttribute("data-cta") });
      }
    });
  });
})();
