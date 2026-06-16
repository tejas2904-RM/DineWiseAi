const API_URL = "http://localhost:8001/v1/recommendations";
const FEEDBACK_URL = "http://localhost:8001/v1/feedback";
const AUTH_STATUS_URL = "http://localhost:8001/v1/auth/status";
const TELEMETRY_URL = "http://localhost:8001/v1/telemetry";

const form = document.getElementById("prefForm");
const formSection = document.getElementById("formSection");
const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");
const cardsContainer = document.getElementById("cardsContainer");
const summaryText = document.getElementById("summaryText");
const metaText = document.getElementById("metaText");
const fallbackBanner = document.getElementById("fallbackBanner");
const fallbackReason = document.getElementById("fallbackReason");
const authErrorBanner = document.getElementById("authErrorBanner");
const authErrorReason = document.getElementById("authErrorReason");
const rateLimitBanner = document.getElementById("rateLimitBanner");
const rateLimitReason = document.getElementById("rateLimitReason");
const cuisineFilters = document.getElementById("cuisineFilters");
const sortSelect = document.getElementById("sortSelect");
const submitBtn = document.getElementById("submitBtn");
const retryBtn = document.getElementById("retryBtn");
const refineBtn = document.getElementById("refineBtn");
const authStatusBtn = document.getElementById("authStatusBtn");
const apiKeyInput = document.getElementById("apiKey");
const authStatus = document.getElementById("authStatus");
const stages = document.querySelectorAll(".stage");
const loadingText = document.getElementById("loadingText");

let lastPayload = null;
let lastResponse = null;
let activeCuisineFilter = "all";

function getApiKey() {
  return apiKeyInput.value.trim();
}

function setError(field, message) {
  const el = document.querySelector(`[data-error-for="${field}"]`);
  if (el) el.textContent = message || "";
}

function clearErrors() {
  ["location", "budget", "cuisine", "minRating"].forEach((f) => setError(f, ""));
}

function validate(payload) {
  clearErrors();
  let valid = true;

  if (!payload.location.trim()) {
    setError("location", "Location is required.");
    valid = false;
  }
  if (!payload.budget.trim()) {
    setError("budget", "Budget is required.");
    valid = false;
  }
  if (!payload.cuisine.trim()) {
    setError("cuisine", "Cuisine is required.");
    valid = false;
  }
  if (Number.isNaN(payload.minRating) || payload.minRating < 0 || payload.minRating > 5) {
    setError("minRating", "Rating must be between 0 and 5.");
    valid = false;
  }

  return valid;
}

function setStage(n) {
  stages.forEach((s) => {
    const stageNum = parseInt(s.dataset.stage, 10);
    s.classList.remove("active", "done");
    if (stageNum < n) s.classList.add("done");
    if (stageNum === n) s.classList.add("active");
  });
}

function setLoading(isLoading, stage = 1) {
  if (isLoading) {
    formSection.classList.add("hidden");
    loadingSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    setStage(stage);
  } else {
    loadingSection.classList.add("hidden");
    resultsSection.classList.remove("hidden");
  }
}

function hideBanners() {
  fallbackBanner.classList.add("hidden");
  authErrorBanner.classList.add("hidden");
  rateLimitBanner.classList.add("hidden");
}

function showAuthError(message) {
  authErrorReason.textContent = message;
  authErrorBanner.classList.remove("hidden");
}

function showRateLimit(message, retryAfter) {
  rateLimitReason.textContent = message + (retryAfter ? ` Retry after ${retryAfter}s.` : "");
  rateLimitBanner.classList.remove("hidden");
}

function buildPayload() {
  return {
    location: document.getElementById("location").value,
    budget: document.getElementById("budget").value,
    cuisine: document.getElementById("cuisine").value,
    minRating: parseFloat(document.getElementById("minRating").value),
    tags: document
      .getElementById("tags")
      .value.split(",")
      .map((v) => v.trim())
      .filter(Boolean),
    topK: 5,
  };
}

async function submitRecommendations(payload) {
  setLoading(true, 1);
  loadingText.textContent = "Capturing and validating preferences...";
  retryBtn.classList.add("hidden");
  hideBanners();

  const apiKey = getApiKey();
  if (!apiKey) {
    showAuthError("Please enter an API key.");
    setLoading(false);
    formSection.classList.remove("hidden");
    return;
  }

  try {
    await new Promise((r) => setTimeout(r, 300));
    setStage(2);
    loadingText.textContent = "Retrieving candidates from dataset...";
    await new Promise((r) => setTimeout(r, 400));
    setStage(3);
    loadingText.textContent = "Generating recommendations with AI...";

    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify(payload),
    });

    if (res.status === 429) {
      const retryAfter = res.headers.get("Retry-After") || "10";
      showRateLimit("Too many requests.", retryAfter);
      retryBtn.classList.remove("hidden");
      setLoading(false);
      formSection.classList.remove("hidden");
      return;
    }

    if (res.status === 401 || res.status === 403) {
      const data = await res.json().catch(() => ({}));
      showAuthError(data.detail || "Invalid API key or insufficient permissions.");
      retryBtn.classList.remove("hidden");
      setLoading(false);
      formSection.classList.remove("hidden");
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      showError(data.message || `Server error (${res.status}). Please try again.`);
      retryBtn.classList.remove("hidden");
      return;
    }

    lastResponse = data;
    renderResults(data);
  } catch (err) {
    showError("Network or server error. Please ensure the backend is running on port 8001.");
    retryBtn.classList.remove("hidden");
  } finally {
    setLoading(false);
  }
}

function showError(message) {
  loadingSection.classList.add("hidden");
  formSection.classList.remove("hidden");
  alert(message);
}

function renderResults(data) {
  summaryText.textContent = data.summary || "Your top recommendations";

  if (data.usedFallback) {
    fallbackBanner.classList.remove("hidden");
    fallbackReason.textContent = data.fallbackReason
      ? `Reason: ${data.fallbackReason}`
      : "";
  } else {
    fallbackBanner.classList.add("hidden");
  }

  const metaParts = [];
  if (data.latencyMs) metaParts.push(`Latency: ${data.latencyMs}ms`);
  if (data.requestId) metaParts.push(`Request ID: ${data.requestId.slice(0, 8)}...`);
  if (data.circuitBreakerState) metaParts.push(`CB: ${data.circuitBreakerState}`);
  metaText.textContent = metaParts.join("  |  ");

  buildCuisineFilters(data.recommendations);
  renderCards(data.recommendations);
}

function buildCuisineFilters(recommendations) {
  const cuisines = [...new Set(recommendations.map((r) => r.cuisine))];
  cuisineFilters.innerHTML = "";

  const allBtn = document.createElement("button");
  allBtn.className = `pill ${activeCuisineFilter === "all" ? "active" : ""}`;
  allBtn.textContent = "All";
  allBtn.addEventListener("click", () => {
    activeCuisineFilter = "all";
    buildCuisineFilters(recommendations);
    applySortAndFilter();
  });
  cuisineFilters.appendChild(allBtn);

  cuisines.forEach((c) => {
    const btn = document.createElement("button");
    btn.className = `pill ${activeCuisineFilter === c ? "active" : ""}`;
    btn.textContent = c;
    btn.addEventListener("click", () => {
      activeCuisineFilter = c;
      buildCuisineFilters(recommendations);
      applySortAndFilter();
    });
    cuisineFilters.appendChild(btn);
  });
}

function renderCards(recommendations) {
  cardsContainer.innerHTML = "";
  recommendations.forEach((rec) => {
    const card = document.createElement("div");
    card.className = "card";
    card.dataset.cuisine = rec.cuisine;
    card.dataset.rating = rec.rating;
    card.dataset.cost = rec.estimatedCost;
    card.dataset.rank = rec.rank;

    const stars = "&#9733;".repeat(Math.round(rec.rating)) + "&#9734;".repeat(5 - Math.round(rec.rating));

    card.innerHTML = `
      <div class="card-header">
        <div class="card-rank">${rec.rank}</div>
        <h3 class="card-title">${escapeHtml(rec.name)}</h3>
      </div>
      <div class="card-meta">
        <span title="Cuisine">&#127860; ${escapeHtml(rec.cuisine)}</span>
        <span title="Rating">${stars} ${rec.rating.toFixed(1)}</span>
        <span title="Estimated cost for two">&#128176; ${Math.round(rec.estimatedCost)}</span>
      </div>
      <div class="card-reason">
        <strong>Why this was chosen:</strong> ${escapeHtml(rec.reason)}
      </div>
      <div class="card-feedback">
        <button class="secondary thumbs-up" data-rid="${rec.restaurantId}">&#128077; Helpful</button>
        <button class="secondary thumbs-down" data-rid="${rec.restaurantId}">&#128078; Not helpful</button>
        <span class="feedback-msg hidden"></span>
      </div>
    `;

    const upBtn = card.querySelector(".thumbs-up");
    const downBtn = card.querySelector(".thumbs-down");
    const msg = card.querySelector(".feedback-msg");

    upBtn.addEventListener("click", () => sendFeedback(rec.restaurantId, true, msg, upBtn, downBtn));
    downBtn.addEventListener("click", () => sendFeedback(rec.restaurantId, false, msg, upBtn, downBtn));

    cardsContainer.appendChild(card);
  });
}

function applySortAndFilter() {
  if (!lastResponse) return;
  let recs = [...lastResponse.recommendations];

  if (activeCuisineFilter !== "all") {
    recs = recs.filter((r) => r.cuisine === activeCuisineFilter);
  }

  const sortMode = sortSelect.value;
  switch (sortMode) {
    case "ratingDesc":
      recs.sort((a, b) => b.rating - a.rating);
      break;
    case "ratingAsc":
      recs.sort((a, b) => a.rating - b.rating);
      break;
    case "costDesc":
      recs.sort((a, b) => b.estimatedCost - a.estimatedCost);
      break;
    case "costAsc":
      recs.sort((a, b) => a.estimatedCost - b.estimatedCost);
      break;
    default:
      recs.sort((a, b) => a.rank - b.rank);
      break;
  }

  renderCards(recs);
}

async function sendFeedback(restaurantId, helpful, msgEl, upBtn, downBtn) {
  if (!lastResponse) return;
  const apiKey = getApiKey();
  try {
    await fetch(FEEDBACK_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        requestId: lastResponse.requestId,
        restaurantId,
        helpful,
      }),
    });
    msgEl.textContent = helpful ? "Thanks for your feedback!" : "Feedback recorded.";
    msgEl.classList.remove("hidden");
    upBtn.disabled = true;
    downBtn.disabled = true;
  } catch {
    msgEl.textContent = "Could not send feedback.";
    msgEl.classList.remove("hidden");
  }
}

async function checkAuthStatus() {
  const apiKey = getApiKey();
  if (!apiKey) {
    authStatus.textContent = "No API key entered";
    authStatus.className = "auth-status error";
    return;
  }
  try {
    const res = await fetch(AUTH_STATUS_URL, {
      headers: { "Authorization": `Bearer ${apiKey}` },
    });
    const data = await res.json();
    if (data.authenticated) {
      authStatus.textContent = `Authenticated (${data.roles.join(", ")})`;
      authStatus.className = "auth-status ok";
    } else {
      authStatus.textContent = "Not authenticated";
      authStatus.className = "auth-status error";
    }
  } catch {
    authStatus.textContent = "Backend unreachable";
    authStatus.className = "auth-status error";
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Event listeners
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = buildPayload();

  if (!validate(payload)) {
    return;
  }

  lastPayload = payload;
  await submitRecommendations(payload);
});

retryBtn.addEventListener("click", async () => {
  if (!lastPayload) return;
  await submitRecommendations(lastPayload);
});

refineBtn.addEventListener("click", () => {
  formSection.classList.remove("hidden");
  resultsSection.classList.add("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

sortSelect.addEventListener("change", applySortAndFilter);
authStatusBtn.addEventListener("click", checkAuthStatus);

// Auto-check auth on load
checkAuthStatus();
