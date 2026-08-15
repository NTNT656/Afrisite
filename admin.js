// African Frame — Admin panel logic
// Reads/writes the same localStorage content used by the public site (data.js).

let content = getContent();
let activeTab = "news";

const els = {
  tabs: document.querySelectorAll(".admin-tab"),
  panels: {
    news: document.getElementById("tab-news"),
    reviews: document.getElementById("tab-reviews"),
  },
  newsTable: document.getElementById("newsTable"),
  reviewsTable: document.getElementById("reviewsTable"),
  addNewsBtn: document.getElementById("addNewsBtn"),
  addReviewBtn: document.getElementById("addReviewBtn"),
  resetBtn: document.getElementById("resetBtn"),

  modalOverlay: document.getElementById("modalOverlay"),
  modalTitle: document.getElementById("modalTitle"),
  form: document.getElementById("articleForm"),
  fieldId: document.getElementById("fieldId"),
  fieldType: document.getElementById("fieldType"),
  fieldTag: document.getElementById("fieldTag"),
  fieldTitle: document.getElementById("fieldTitle"),
  fieldMeta: document.getElementById("fieldMeta"),
  fieldBlurb: document.getElementById("fieldBlurb"),
  fieldScore: document.getElementById("fieldScore"),
  newsOnlyFields: document.getElementById("newsOnlyFields"),
  reviewOnlyFields: document.getElementById("reviewOnlyFields"),
  cancelBtn: document.getElementById("cancelBtn"),
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------- Rendering ----------

function renderNewsTable() {
  if (content.news.length === 0) {
    els.newsTable.innerHTML = `<div class="admin-empty">No news articles yet. Click "Add Article" to create one.</div>`;
    return;
  }
  els.newsTable.innerHTML = content.news
    .map(
      (n) => `
      <div class="admin-row">
        <div class="admin-row-main">
          <div class="admin-row-tag">${escapeHtml(n.tag)}</div>
          <div class="admin-row-title">${escapeHtml(n.title)}</div>
          <div class="admin-row-meta">${escapeHtml(n.meta)}</div>
        </div>
        <div class="admin-row-actions">
          <button class="edit-btn" data-type="news" data-id="${n.id}">Edit</button>
          <button class="delete-btn" data-type="news" data-id="${n.id}">Delete</button>
        </div>
      </div>`
    )
    .join("");
}

function renderReviewsTable() {
  if (content.reviews.length === 0) {
    els.reviewsTable.innerHTML = `<div class="admin-empty">No reviews yet. Click "Add Review" to create one.</div>`;
    return;
  }
  els.reviewsTable.innerHTML = content.reviews
    .map(
      (r) => `
      <div class="admin-row">
        <div class="admin-row-main">
          <div class="admin-row-tag">${escapeHtml(r.tag)} · Score ${escapeHtml(r.score)}</div>
          <div class="admin-row-title">${escapeHtml(r.title)}</div>
          <div class="admin-row-meta">${escapeHtml(r.blurb)}</div>
        </div>
        <div class="admin-row-actions">
          <button class="edit-btn" data-type="reviews" data-id="${r.id}">Edit</button>
          <button class="delete-btn" data-type="reviews" data-id="${r.id}">Delete</button>
        </div>
      </div>`
    )
    .join("");
}

function renderAll() {
  renderNewsTable();
  renderReviewsTable();
}

// ---------- Tabs ----------

els.tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    activeTab = tab.dataset.tab;
    els.tabs.forEach((t) => t.classList.toggle("active", t === tab));
    els.panels.news.classList.toggle("hidden", activeTab !== "news");
    els.panels.reviews.classList.toggle("hidden", activeTab !== "reviews");
  });
});

// ---------- Modal open/close ----------

function openModal(type, article) {
  els.fieldType.value = type;
  els.fieldId.value = article ? article.id : "";
  els.modalTitle.textContent = article
    ? `Edit ${type === "news" ? "Article" : "Review"}`
    : `Add ${type === "news" ? "Article" : "Review"}`;

  els.fieldTag.value = article ? article.tag : "";
  els.fieldTitle.value = article ? article.title : "";
  els.fieldMeta.value = article && type === "news" ? article.meta : "";
  els.fieldBlurb.value = article && type === "reviews" ? article.blurb : "";
  els.fieldScore.value = article && type === "reviews" ? article.score : "";

  els.newsOnlyFields.classList.toggle("hidden", type !== "news");
  els.reviewOnlyFields.classList.toggle("hidden", type !== "reviews");

  els.modalOverlay.classList.remove("hidden");
  els.fieldTag.focus();
}

function closeModal() {
  els.modalOverlay.classList.add("hidden");
  els.form.reset();
}

els.addNewsBtn.addEventListener("click", () => openModal("news", null));
els.addReviewBtn.addEventListener("click", () => openModal("reviews", null));
els.cancelBtn.addEventListener("click", closeModal);
els.modalOverlay.addEventListener("click", (e) => {
  if (e.target === els.modalOverlay) closeModal();
});

// ---------- Edit / Delete (event delegation) ----------

document.addEventListener("click", (e) => {
  const editBtn = e.target.closest(".edit-btn");
  const deleteBtn = e.target.closest(".delete-btn");

  if (editBtn) {
    const { type, id } = editBtn.dataset;
    const article = content[type].find((a) => a.id === id);
    if (article) openModal(type, article);
  }

  if (deleteBtn) {
    const { type, id } = deleteBtn.dataset;
    const article = content[type].find((a) => a.id === id);
    if (!article) return;
    const ok = confirm(`Delete "${article.title}"? This can't be undone.`);
    if (!ok) return;
    content[type] = content[type].filter((a) => a.id !== id);
    saveContent(content);
    renderAll();
  }
});

// ---------- Save (add or update) ----------

els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const type = els.fieldType.value;
  const id = els.fieldId.value;

  const tag = els.fieldTag.value.trim();
  const title = els.fieldTitle.value.trim();
  if (!tag || !title) return;

  if (type === "news") {
    const meta = els.fieldMeta.value.trim() || "Just now";
    if (id) {
      const article = content.news.find((a) => a.id === id);
      Object.assign(article, { tag, title, meta });
    } else {
      content.news.unshift({ id: makeId("n"), tag, title, meta });
    }
  } else {
    const blurb = els.fieldBlurb.value.trim();
    const score = els.fieldScore.value.trim() || "—";
    if (id) {
      const article = content.reviews.find((a) => a.id === id);
      Object.assign(article, { tag, title, blurb, score });
    } else {
      content.reviews.unshift({ id: makeId("r"), tag, title, blurb, score });
    }
  }

  saveContent(content);
  renderAll();
  closeModal();
});

// ---------- Reset ----------

els.resetBtn.addEventListener("click", () => {
  const ok = confirm("Reset all News and Reviews back to the original defaults? This can't be undone.");
  if (!ok) return;
  resetContent();
  content = getContent();
  renderAll();
});

// ---------- Init ----------

renderAll();
