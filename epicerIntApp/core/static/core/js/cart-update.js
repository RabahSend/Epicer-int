document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-cart-update]");

  if (!form) return;

  form.querySelectorAll('input[name^="quantity_"]').forEach((input) => {
    input.addEventListener("change", () => form.requestSubmit());
  });
});
