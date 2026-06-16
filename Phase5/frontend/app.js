const API_URL = "http://localhost:8000/recommendations";
const FEEDBACK_URL = "http://localhost:8000/feedback";
const TELEMETRY_URL = "http://localhost:8000/telemetry";

// Session tracking for Phase 6 observability
const SESSION_ID = generateSessionId();
let formStarted = false;

const form = document.getElementById("prefForm");
const formSection = document.getElementById("formSection");
const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");
const cardsContainer = document.getElementById("cardsContainer");
const summaryText = document.getElementById("summaryText");
const metaText = document.getElementById("metaText");
const fallbackBanner = document.getElementById("fallbackBanner");
const fallbackReason = document.getElementById("fallbackReason");
const cuisineFilters = document.getElementById("cuisineFilters");
const sortSelect = document.getElementById("sortSelect");
const submitBtn = document.getElementById("submitBtn");
const retryBtn = document.getElementById("retryBtn");
const refineBtn = document.getElementById("refineBtn");
const stages = document.querySelectorAll(".stage");
const loadingText = document.getElementById("loadingText");

let lastPayload = null;
let lastResponse = null;
let activeCuisineFilter = "all";

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

  try {
    // Simulate progressive stages for UX
    await new Promise((r) => setTimeout(r, 300));
    setStage(2);
    loadingText.textContent = "Retrieving candidates from dataset...";
    await new Promise((r) => setTimeout(r, 400));
    setStage(3);
    loadingText.textContent = "Generating recommendations with AI...";

    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.message || "Server error. Please try again.");
      retryBtn.classList.remove("hidden");
      return;
    }

    lastResponse = data;
    renderResults(data);
    sendTelemetryEvent("results_rendered", {
      requestId: data.requestId,
      recommendationCount: data.recommendations?.length || 0,
      usedFallback: data.usedFallback,
      latencyMs: data.latencyMs,
    });
  } catch (err) {
    showError("Network or server error. Please ensure the backend is running.");
    retryBtn.classList.remove("hidden");
    sendTelemetryEvent("request_error", { error: err.message });
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

  // Fallback banner
  if (data.usedFallback) {
    fallbackBanner.classList.remove("hidden");
    fallbackReason.textContent = data.fallbackReason
      ? `Reason: ${data.fallbackReason}`
      : "";
  } else {
    fallbackBanner.classList.add("hidden");
  }

  // Metadata
  const metaParts = [];
  if (data.latencyMs) metaParts.push(`Latency: ${data.latencyMs}ms`);
  if (data.requestId) metaParts.push(`Request ID: ${data.requestId.slice(0, 8)}...`);
  metaText.textContent = metaParts.join("  |  ");

  // Build cuisine filter pills
  buildCuisineFilters(data.recommendations);

  // Render cards
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

  // Filter
  if (activeCuisineFilter !== "all") {
    recs = recs.filter((r) => r.cuisine === activeCuisineFilter);
  }

  // Sort
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
  try {
    await fetch(FEEDBACK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        requestId: lastResponse.requestId,
        restaurantId,
        helpful,
      }),
    });
    sendTelemetryEvent("feedback_given", { restaurantId, helpful });
    msgEl.textContent = helpful ? "Thanks for your feedback!" : "Feedback recorded.";
    msgEl.classList.remove("hidden");
    upBtn.disabled = true;
    downBtn.disabled = true;
  } catch {
    msgEl.textContent = "Could not send feedback.";
    msgEl.classList.remove("hidden");
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Phase 6: UX Telemetry
// ---------------------------------------------------------------------------
function generateSessionId() {
  return "ses-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

function sendTelemetryEvent(event, payload = {}) {
  try {
    fetch(TELEMETRY_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId: SESSION_ID, event, payload }),
    });
  } catch {
    // Telemetry is best-effort
  }
}

// Track form interaction start
["location", "budget", "cuisine", "minRating", "tags"].forEach((id) => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener("focus", () => {
      if (!formStarted) {
        formStarted = true;
        sendTelemetryEvent("form_started");
      }
    }, { once: true });
  }
});

// Event listeners
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = buildPayload();

  if (!validate(payload)) {
    sendTelemetryEvent("form_validation_error", { fields: ["location", "budget", "cuisine", "minRating"] });
    return;
  }

  sendTelemetryEvent("form_submitted", { location: payload.location, budget: payload.budget });
  lastPayload = payload;
  await submitRecommendations(payload);
});

retryBtn.addEventListener("click", async () => {
  sendTelemetryEvent("request_retry");
  if (!lastPayload) return;
  await submitRecommendations(lastPayload);
});

refineBtn.addEventListener("click", () => {
  sendTelemetryEvent("refine_clicked");
  formSection.classList.remove("hidden");
  resultsSection.classList.add("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

sortSelect.addEventListener("change", () => {
  sendTelemetryEvent("sort_changed", { sortMode: sortSelect.value });
  applySortAndFilter();
});
