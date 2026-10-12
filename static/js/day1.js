"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const teamFields = document.querySelector("[data-day1-team-fields]");
  const construct = [...document.querySelectorAll("[data-event-choice]")]
    .find((input) => input.value === "Construct2Conquer");
  if (!teamFields || !construct) return;
  const fields = [...teamFields.querySelectorAll("input")];
  const update = () => {
    teamFields.hidden = !construct.checked;
    fields.forEach((input) => { input.required = construct.checked; });
  };
  construct.addEventListener("change", update);
  document.querySelectorAll("[data-select-event='Construct2Conquer']").forEach((link) => {
    link.addEventListener("click", update);
  });
  update();
});
