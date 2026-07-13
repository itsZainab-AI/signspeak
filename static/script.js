// ============================================================
// SignSpeak frontend — talks to POST /scan and POST /ask
// ============================================================

const API_BASE = "http://localhost:8000";

const RTL_LANGUAGES = new Set(["Arabic"]);

// -------- Scan & Translate --------

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const scanPreview = document.getElementById("scan-preview");
const previewImage = document.getElementById("preview-image");
const languageSelect = document.getElementById("language-select");
const scanButton = document.getElementById("scan-button");
const scanLoading = document.getElementById("scan-loading");
const scanError = document.getElementById("scan-error");
const scanResults = document.getElementById("scan-results");
const resultOriginal = document.getElementById("result-original");
const resultTranslation = document.getElementById("result-translation");
const resultExplanation = document.getElementById("result-explanation");

let selectedFile = null;

dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fileInput.click();
  }
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;
  selectedFile = file;
  scanButton.disabled = false;

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    scanPreview.hidden = false;
  };
  reader.readAsDataURL(file);

  hideScanStatus();
});

scanButton.addEventListener("click", async () => {
  if (!selectedFile) return;

  hideScanStatus();
  scanLoading.hidden = false;
  scanButton.disabled = true;

  const targetLanguage = languageSelect.value;

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("target_language", targetLanguage);

    const response = await fetch(`${API_BASE}/scan`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await safeJson(response);
      throw new Error(errorBody?.detail || `Request failed (${response.status})`);
    }

    const data = await response.json();
    showScanResults(data, targetLanguage);
  } catch (err) {
    showScanError(err.message || "Couldn't reach the scan service. Is the server running?");
  } finally {
    scanLoading.hidden = true;
    scanButton.disabled = false;
  }
});

function showScanResults(data, targetLanguage) {
  resultOriginal.textContent = data.original_text || "—";
  resultTranslation.textContent = data.translation || "—";
  resultExplanation.textContent = data.explanation || "—";

  const isRtl = RTL_LANGUAGES.has(targetLanguage);
  resultTranslation.dir = isRtl ? "rtl" : "auto";

  // restart the flap-in animation on repeat scans
  scanResults.hidden = false;
  scanResults.style.animation = "none";
  document.querySelectorAll("#scan-results .result-row").forEach((row) => {
    row.style.animation = "none";
    // force reflow so the animation restarts
    void row.offsetWidth;
    row.style.animation = "";
  });
}

function showScanError(message) {
  scanError.textContent = message;
  scanError.hidden = false;
}

function hideScanStatus() {
  scanError.hidden = true;
  scanResults.hidden = true;
}

async function safeJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

// -------- Ask a Question --------

const askForm = document.getElementById("ask-form");
const questionInput = document.getElementById("question-input");
const askLoading = document.getElementById("ask-loading");
const askError = document.getElementById("ask-error");
const answerCard = document.getElementById("answer-card");
const answerText = document.getElementById("answer-text");

askForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  hideAskStatus();
  askLoading.hidden = false;

  try {
    const response = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const errorBody = await safeJson(response);
      throw new Error(errorBody?.detail || `Request failed (${response.status})`);
    }

    const data = await response.json();
    showAnswer(data.answer);
  } catch (err) {
    showAskError(err.message || "Couldn't reach the assistant. Is the server running?");
  } finally {
    askLoading.hidden = true;
  }
});

function showAnswer(answer) {
  answerText.textContent = answer || "—";
  answerCard.hidden = false;
  answerCard.style.animation = "none";
  void answerCard.offsetWidth;
  answerCard.style.animation = "";
}

function showAskError(message) {
  askError.textContent = message;
  askError.hidden = false;
}

function hideAskStatus() {
  askError.hidden = true;
  answerCard.hidden = true;
}