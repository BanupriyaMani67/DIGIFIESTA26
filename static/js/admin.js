"use strict";

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".admin-member2").forEach((section) => {
    const checkbox = [...document.querySelectorAll(".add-panel input[name='events']")]
      .find((input) => input.value === "Construct2Conquer");
    if (!checkbox) return;
    const update = () => {
      section.hidden = !checkbox.checked;
      section.querySelectorAll("input").forEach((input) => { input.required = checkbox.checked; });
    };
    checkbox.addEventListener("change", update);
    update();
  });
});
