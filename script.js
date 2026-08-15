// African Frame — full navigation and rendering

function renderNews() {
    var container = document.getElementById("newsList");
    if (!container) return;
    var data = getContent();
    var news = data.news || [];
    container.innerHTML = news
        .map(function(n) {
            return `
      <div class="card">
        <div class="thumb">
          <span class="tag mono">News</span>
          <div class="poster p-news1"><div class="shape"></div><div class="grain"></div><div class="vig"></div></div>
        </div>
        <div class="meta">
          <div class="kicker mono">${escapeHtml(n.tag)}</div>
          <h3>${escapeHtml(n.title)}</h3>
          <div class="foot-meta"><span>${escapeHtml(n.meta)}</span></div>
        </div>
      </div>`;
        })
        .join("");
}

function renderReviews() {
    var container = document.getElementById("reviewsList");
    if (!container) return;
    var data = getContent();
    var reviews = data.reviews || [];
    var posterClasses = ["p-drama", "p-action", "p-comedy", "p-horror", "p-scifi"];
    container.innerHTML = reviews
        .map(function(r) {
            var posterClass = posterClasses[Math.floor(Math.random() * posterClasses.length)];
            return `
      <div class="card">
        <div class="thumb">
          <div class="poster ${posterClass}"><div class="shape"></div><div class="figure fig-duo"><svg viewBox="0 0 100 140" preserveAspectRatio="xMidYMax meet" fill="#0A0806"><circle cx="50" cy="30" r="22"/><path d="M50 55 C20 55 6 82 6 140 L94 140 C94 82 80 55 50 55 Z"/></svg><svg viewBox="0 0 100 140" preserveAspectRatio="xMidYMax meet" fill="#0A0806" style="opacity:.7"><circle cx="50" cy="30" r="20"/><path d="M50 53 C24 53 12 80 12 140 L88 140 C88 80 76 53 50 53 Z"/></svg></div><div class="grain"></div><div class="vig"></div>
            <div class="cap"><span class="genre">${escapeHtml(r.tag)}</span><span class="t1">${escapeHtml(r.title)}</span></div>
          </div>
          <div class="score-badge">${escapeHtml(r.score)}</div>
        </div>
        <div class="meta">
          <div class="kicker mono">${escapeHtml(r.tag)}</div>
          <h3>${escapeHtml(r.title)}</h3>
          <p>${escapeHtml(r.blurb)}</p>
        </div>
      </div>`;
        })
        .join("");
}

function renderArchitecture() {
    var container = document.getElementById("architectureList");
    if (!container) return;
    var data = getContent();
    var architecture = data.architecture || [];
    container.innerHTML = architecture
        .map(function(a) {
            return `
      <div class="card">
        <div class="thumb">
          <span class="tag mono">Architecture</span>
          <div class="poster p-news3"><div class="shape"></div><div class="grain"></div><div class="vig"></div></div>
        </div>
        <div class="meta">
          <div class="kicker mono">${escapeHtml(a.tag)}</div>
          <h3>${escapeHtml(a.title)}</h3>
          <div class="foot-meta"><span>${escapeHtml(a.meta)}</span></div>
        </div>
      </div>`;
        })
        .join("");
}

// Full list renderers
function renderFullNews() {
    var container = document.getElementById("newsFullList");
    if (!container) return;
    var data = getContent();
    var news = data.news || [];
    container.innerHTML = news
        .map(function(n) {
            return `
      <div class="card">
        <div class="thumb">
          <span class="tag mono">News</span>
          <div class="poster p-news2"><div class="shape"></div><div class="grain"></div><div class="vig"></div></div>
        </div>
        <div class="meta">
          <div class="kicker mono">${escapeHtml(n.tag)}</div>
          <h3>${escapeHtml(n.title)}</h3>
          <div class="foot-meta"><span>${escapeHtml(n.meta)}</span></div>
        </div>
      </div>`;
        })
        .join("");
}

function renderFullReviews() {
    var container = document.getElementById("reviewsFullList");
    if (!container) return;
    var data = getContent();
    var reviews = data.reviews || [];
    container.innerHTML = reviews
        .map(function(r) {
            return `
      <div class="card">
        <div class="thumb">
          <div class="poster p-drama"><div class="shape"></div><div class="grain"></div><div class="vig"></div></div>
          <div class="score-badge">${escapeHtml(r.score)}</div>
        </div>
        <div class="meta">
          <div class="kicker mono">${escapeHtml(r.tag)}</div>
          <h3>${escapeHtml(r.title)}</h3>
          <p>${escapeHtml(r.blurb)}</p>
        </div>
      </div>`;
        })
        .join("");
}

function renderFullArchitecture() {
    var container = document.getElementById("architectureFullList");
    if (!container) return;
    var data = getContent();
    var architecture = data.architecture || [];
    container.innerHTML = architecture
        .map(function(a) {
            return `
      <div class="card">
        <div class="thumb">
          <span class="tag mono">Architecture</span>
          <div class="poster p-news4"><div class="shape"></div><div class="grain"></div><div class="vig"></div></div>
        </div>
        <div class="meta">
          <div class="kicker mono">${escapeHtml(a.tag)}</div>
          <h3>${escapeHtml(a.title)}</h3>
          <div class="foot-meta"><span>${escapeHtml(a.meta)}</span></div>
        </div>
      </div>`;
        })
        .join("");
}

function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = (str != null) ? str : "";
    return div.innerHTML;
}

// ========== SEARCH FUNCTION ==========
function performSearch(query) {
    var results = [];
    var data = getContent();
    var allItems = [];

    // Collect all items with type labels
    data.news.forEach(function(item) {
        allItems.push({ type: "News", item: item });
    });
    data.reviews.forEach(function(item) {
        allItems.push({ type: "Review", item: item });
    });
    data.architecture.forEach(function(item) {
        allItems.push({ type: "Architecture", item: item });
    });

    var q = query.toLowerCase().trim();
    if (q.length === 0) return [];

    results = allItems.filter(function(entry) {
        var item = entry.item;
        var searchable = (item.title || "") + " " + (item.tag || "") + " " + (item.blurb || "") + " " + (item.meta || "");
        return searchable.toLowerCase().indexOf(q) !== -1;
    });

    return results;
}

function renderSearchResults(query) {
    var container = document.getElementById("searchResults");
    if (!container) return;
    var results = performSearch(query);

    if (query.trim().length === 0) {
        container.innerHTML = '<p style="color:var(--ink-soft);text-align:center;padding:20px 0;">Start typing to search across News, Reviews, and Architecture.</p>';
        return;
    }

    if (results.length === 0) {
        container.innerHTML = '<div class="no-results">No results found for "' + escapeHtml(query) + '"</div>';
        return;
    }

    container.innerHTML = results.map(function(entry) {
        var item = entry.item;
        var type = entry.type;
        var meta = item.meta || item.blurb || "";
        return `
      <div class="search-result-item">
        <span class="type">${escapeHtml(type)} · ${escapeHtml(item.tag)}</span>
        <h3>${escapeHtml(item.title)}</h3>
        <div class="meta">${escapeHtml(meta)}</div>
      </div>
    `;
    }).join("");
}

// ========== PAGE ROUTING ==========
var pages = {
    home: document.getElementById("page-home"),
    news: document.getElementById("page-news"),
    reviews: document.getElementById("page-reviews"),
    architecture: document.getElementById("page-architecture"),
    features: document.getElementById("page-features"),
    streaming: document.getElementById("page-streaming"),
    boxoffice: document.getElementById("page-boxoffice"),
    shows: document.getElementById("page-shows"),
    genre: document.getElementById("page-genre"),
    awards: document.getElementById("page-awards"),
    people: document.getElementById("page-people"),
    events: document.getElementById("page-events"),
    videos: document.getElementById("page-videos"),
    podcast: document.getElementById("page-podcast"),
    community: document.getElementById("page-community"),
    shop: document.getElementById("page-shop"),
    search: document.getElementById("page-search"),
    origins: document.getElementById("page-origins")
};

var navLinks = document.querySelectorAll("[data-nav]");

function goTo(pageName) {
    // Hide all pages
    for (var key in pages) {
        if (pages[key]) pages[key].classList.remove("active");
    }
    // Show target
    if (pages[pageName]) pages[pageName].classList.add("active");

    // Update active nav
    var allNav = document.querySelectorAll("nav.links a, .mobile-nav a");
    for (var i = 0; i < allNav.length; i++) {
        allNav[i].classList.remove("active");
        if (allNav[i].getAttribute("data-nav") === pageName) {
            allNav[i].classList.add("active");
        }
    }

    // Focus search input if on search page
    if (pageName === "search") {
        var searchInput = document.getElementById("searchInput");
        if (searchInput) setTimeout(function() { searchInput.focus(); }, 100);
    }

    // Close mobile nav
    var mobileNav = document.getElementById("mobileNav");
    if (mobileNav) mobileNav.classList.remove("open");

    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
}

// Wire up nav links
for (var i = 0; i < navLinks.length; i++) {
    (function(el) {
        el.addEventListener("click", function(e) {
            e.preventDefault();
            var target = el.getAttribute("data-nav");
            if (pages[target]) {
                goTo(target);
            } else {
                goTo("home");
            }
        });
    })(navLinks[i]);
}

// Mobile toggle
var toggle = document.getElementById("mobileToggle");
var mobileNav = document.getElementById("mobileNav");
if (toggle && mobileNav) {
    toggle.addEventListener("click", function() {
        mobileNav.classList.toggle("open");
    });
}

// Search input handler
var searchInput = document.getElementById("searchInput");
if (searchInput) {
    searchInput.addEventListener("input", function() {
        renderSearchResults(this.value);
    });
}

// ========== RENDER ALL ==========
renderNews();
renderReviews();
renderArchitecture();
renderFullNews();
renderFullReviews();
renderFullArchitecture();

// Start on home
goTo("home");