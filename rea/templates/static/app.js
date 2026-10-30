"use strict";
const $ = (selector) => document.querySelector(selector);
const ui = { results: $("#results"), detail: $("#detail"), search: $("#search"),
             category: $("#category"), error: $("#error"), count: $("#count"),
             overviewTotal: $("#overview-total"), categoriesList: $("#category-stats"),
             categoryWarning: $("#category-warning"), schemaFields: $("#schema-fields"),
             pagination: $(".pagination"), pagePrev: $("#page-prev"),
             pageNext: $("#page-next"), pageStatus: $("#page-status") };
let requestId = 0;
const PAGE_SIZE = 100;
let pageOffset = 0;

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
  ui.pagePrev.disabled = true;
  ui.pageNext.disabled = true;
  const params = new URLSearchParams({
    q: ui.search.value, category: ui.category.value,
    limit: String(PAGE_SIZE), offset: String(pageOffset)
  });
  try {
    const data = await jsonGet("/api/items?" + params.toString());
    if (current !== requestId) return;
    // A previously selected page may disappear after a search or data update.
    if (data.total > 0 && pageOffset >= data.total) {
      pageOffset = Math.floor((data.total - 1) / PAGE_SIZE) * PAGE_SIZE;
      return loadItems();
    }
    const start = data.items.length ? pageOffset + 1 : 0;
    const end = pageOffset + data.items.length;
    ui.count.textContent = data.total + "건";
    ui.pageStatus.textContent = start + "–" + end + " / " + data.total + "건";
    ui.pagination.hidden = data.total <= PAGE_SIZE;
    ui.pagePrev.disabled = pageOffset === 0;
    ui.pageNext.disabled = end >= data.total || data.items.length === 0;
    ui.results.replaceChildren();
    ui.detail.replaceChildren(element("p", "목록에서 항목을 선택하세요.", "empty"));
    if (!data.items.length) {
      ui.results.append(element("p", "조건에 맞는 데이터가 없습니다.", "empty"));
      return;
    }
    for (const item of data.items) {
      const button = element("button", undefined, "item");
      button.type = "button";
      button.append(element("strong", item.title), element("span", item.category, "chip"));
      button.addEventListener("click", () => showDetails(item));
      ui.results.append(button);
    }
  } catch (error) {
    if (current === requestId) {
      // A failed new query must not leave the previous query's rows visible.
      ui.count.textContent = "조회 실패";
      ui.pageStatus.textContent = "—";
      ui.pagination.hidden = true;
      ui.results.replaceChildren(element("p", "목록을 불러오지 못했습니다.", "empty"));
      ui.detail.replaceChildren(element("p", "조회 실패로 이전 선택을 지웠습니다.", "empty"));
      showError(error.message);
    }
  }
}


async function loadOverview() {
  const [summary, schema] = await Promise.all([jsonGet("/api/summary"), jsonGet("/api/schema")]);
  ui.overviewTotal.textContent = summary.total_items + "건";
  ui.categoriesList.replaceChildren();
  for (const row of summary.category_counts) {
    const item = element("li");
    item.append(element("span", row.category), element("strong", row.count + "건"));
    ui.categoriesList.append(item);
  }
  ui.categoryWarning.hidden = !summary.categories_truncated;
  ui.schemaFields.replaceChildren();
  for (const field of schema.fields) {
    const item = element("li");
    item.append(element("strong", field.name),
      element("span", field.inferred_type + " · 값 " + field.present_count +
      " · 비어 있음 " + field.missing_count));
    ui.schemaFields.append(item);
  }
}

async function init() {
  try {
    const { categories } = await jsonGet("/api/categories");
    for (const category of categories) {
      const option = element("option", category);
      option.value = category;
      ui.category.add(option);
    }
    await Promise.all([loadItems(), loadOverview()]);
  } catch (error) { showError(error.message); }
}
let debounce;
ui.search.addEventListener("input", () => {
  // Invalidate old responses immediately, not only after the debounce fires.
  ++requestId;
  pageOffset = 0;
  clearTimeout(debounce);
  debounce = setTimeout(loadItems, 160);
});
ui.category.addEventListener("change", () => { pageOffset = 0; loadItems(); });
ui.pagePrev.addEventListener("click", () => {
  if (pageOffset === 0) return;
  pageOffset = Math.max(0, pageOffset - PAGE_SIZE);
  loadItems();
});
ui.pageNext.addEventListener("click", () => {
  if (ui.pageNext.disabled) return;
  pageOffset += PAGE_SIZE;
  loadItems();
});
init();
