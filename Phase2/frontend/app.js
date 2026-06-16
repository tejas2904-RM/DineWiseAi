const form = document.getElementById("prefForm");
const statusText = document.getElementById("statusText");
const resultBox = document.getElementById("resultBox");
const retryBtn = document.getElementById("retryBtn");
const submitBtn = document.getElementById("submitBtn");

let lastPayload = null;

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

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading ? "Loading..." : "Get Recommendations";
}

async function callApi(payload) {
  statusText.textContent = "Submitting preferences and validating...";
  setLoading(true);
  resultBox.textContent = "";
  retryBtn.classList.add("hidden");

  try {
    const res = await fetch("http://localhost:8000/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      statusText.textContent = "Validation/server error. Please review and retry.";
      resultBox.textContent = JSON.stringify(data, null, 2);
      retryBtn.classList.remove("hidden");
      return;
    }

    statusText.textContent = "Preferences captured successfully.";
    resultBox.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    statusText.textContent = "Network error. Ensure backend is running, then retry.";
    resultBox.textContent = String(err);
    retryBtn.classList.remove("hidden");
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
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

  if (!validate(payload)) {
    statusText.textContent = "Fix validation errors before submitting.";
    return;
  }

  lastPayload = payload;
  await callApi(payload);
});

retryBtn.addEventListener("click", async () => {
  if (!lastPayload) return;
  await callApi(lastPayload);
});
