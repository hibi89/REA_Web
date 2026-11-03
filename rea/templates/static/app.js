"use strict";
const $ = (selector) => document.querySelector(selector);
const ui = { results: $("#results"), detail: $("#detail"), search: $("#search"),
             category: $("#category"), error: $("#error"), count: $("#count") };
let requestId = 0;

function element(tag, value, className) {
  const node = document.createElement(tag);
  if (value !== undefined) node.textContent = String(value);
  if (className) node.className = className;
  return node;
}
function showError(message) { ui.error.hidden = false; ui.error.textContent = message; }
function clearError() { ui.error.hidden = true; ui.error.textContent = ""; }

async function jsonGet(url) {
  const response = await fetch(url, { credentials: "same-origin" });
  if (!response.ok) throw new Error("데이터 응답 오류 (" + response.status + ")");
  return response.json();
}

function showDetails(item) {
  ui.detail.replaceChildren();
  ui.detail.append(element("span", item.category, "chip"),
                   element("h3", item.title),
                   element("p", "ID: " + item.id, "muted"));
  const dl = element("dl");
  for (const [key, value] of Object.entries(item.attributes || {})) {
    dl.append(element("dt", key), element("dd", value || "—"));
  }
  if (dl.children.length) ui.detail.append(dl);
}

async function loadItems() {
  const current = ++requestId;
  clearError();
  const params = new URLSearchParams({q: ui.search.value, category: ui.category.value, limit: "100"});
  try {
    const data = await jsonGet("/api/items?" + params.toString());
    if (current !== requestId) return;
    ui.count.textContent = data.total + "건" + (data.total > 100 ? " · 첫 100건 표시" : "");
    ui.results.replaceChildren();
    if (!data.items.length) { ui.results.append(element("p", "조건에 맞는 데이터가 없습니다.", "empty")); return; }
    for (const item of data.items) {
      const button = element("button", undefined, "item");
      button.type = "button";
      button.append(element("strong", item.title), element("span", item.category, "chip"));
      button.addEventListener("click", () => showDetails(item));
      ui.results.append(button);
    }
  } catch (error) { if (current === requestId) showError(error.message); }
}

async function init() {
  try {
    const { categories } = await jsonGet("/api/categories");
    for (const category of categories) {
      const option = element("option", category);
      option.value = category;
      ui.category.add(option);
    }
    await loadItems();
  } catch (error) { showError(error.message); }
}
let debounce;
ui.search.addEventListener("input", () => { clearTimeout(debounce); debounce = setTimeout(loadItems, 160); });
ui.category.addEventListener("change", loadItems);
init();
