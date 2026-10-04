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

  var select = document.querySelector(".lang-switch select");
  if (select) {
    select.addEventListener("change", function () {
      window.location.href = select.value;
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
