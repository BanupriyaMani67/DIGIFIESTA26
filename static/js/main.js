"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".top-nav");
  toggle?.addEventListener("click", () => {
    const expanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!expanded));
    nav?.classList.toggle("is-open", !expanded);
  });

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (event.defaultPrevented) return;
      const button = event.submitter;
      if (!button || button.disabled) return;
      button.dataset.originalLabel = button instanceof HTMLInputElement
        ? button.value
        : button.textContent;
      if (button instanceof HTMLInputElement) button.value = "Saving...";
      else button.textContent = "Saving...";
      button.disabled = true;
      form.setAttribute("aria-busy", "true");
    });
  });

  document.querySelectorAll("[data-add-member]").forEach((button) => {
    button.addEventListener("click", () => {
      const form = button.closest("form");
      const list = form?.querySelector("[data-member-list]");
      const template = document.getElementById("admin-member-row-template")
        || document.getElementById("member-row-template");
      if (!list || !template) return;
      list.append(template.content.cloneNode(true));
      updateMemberRemoval(list);
    });
  });

  document.addEventListener("click", (event) => {
    const remove = event.target.closest("[data-remove-member]");
    if (!remove) return;
    const list = remove.closest("[data-member-list]");
    if (!list || list.querySelectorAll(".member-row").length <= 2) return;
    remove.closest(".member-row").remove();
    updateMemberRemoval(list);
  });

  document.querySelectorAll("[data-select-event]").forEach((link) => {
    link.addEventListener("click", () => {
      const eventName = link.dataset.selectEvent;
      const checkbox = [...document.querySelectorAll("[data-event-choice]")]
        .find((input) => input.value === eventName);
      if (checkbox) {
        checkbox.checked = true;
        checkbox.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
  });

  function updateMemberRemoval(list) {
    const rows = [...list.querySelectorAll(".member-row")];
    rows.forEach((row) => {
      const button = row.querySelector("[data-remove-member]");
      if (button) button.hidden = rows.length <= 2;
    });
  }

  window.addEventListener("pageshow", () => {
    document.querySelectorAll("form[aria-busy='true']").forEach((form) => {
      form.removeAttribute("aria-busy");
      const button = form.querySelector("button[disabled], input[type='submit'][disabled]");
      if (!button || !button.dataset.originalLabel) return;
      if (button instanceof HTMLInputElement) button.value = button.dataset.originalLabel;
      else button.textContent = button.dataset.originalLabel;
      button.disabled = false;
    });
  });
});
