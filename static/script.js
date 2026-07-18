// ============================================================
// SignSpeak frontend — talks to POST /scan and POST /ask
// ============================================================

const API_BASE = "";

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

  spawnCelebrationSparks(scanResults);
}

function spawnCelebrationSparks(container) {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  // clear any previous spark layer before adding a new one
  const existing = container.querySelector(".spark-layer");
  if (existing) existing.remove();

  const layer = document.createElement("div");
  layer.className = "spark-layer";
  layer.setAttribute("aria-hidden", "true");
  container.appendChild(layer);

  const sparkCount = 14;
  for (let i = 0; i < sparkCount; i++) {
    const spark = document.createElement("span");
    spark.className = "spark" + (i % 3 === 0 ? " spark-chalk" : "");
    const angle = (Math.PI * 2 * i) / sparkCount + (Math.random() * 0.4 - 0.2);
    const distance = 40 + Math.random() * 50;
    const sx = Math.cos(angle) * distance;
    const sy = Math.sin(angle) * distance - 20; // bias slightly upward
    spark.style.setProperty("--sx", `${sx}px`);
    spark.style.setProperty("--sy", `${sy}px`);
    spark.style.animationDelay = `${Math.random() * 0.1}s`;
    layer.appendChild(spark);
  }

  // clean up after the animation finishes
  setTimeout(() => layer.remove(), 900);
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

// -------- Splash screen cleanup --------
// Remove the splash screen from the DOM once its animation finishes,
// so it doesn't linger as an invisible element.
const splashScreen = document.getElementById("splash-screen");
if (splashScreen) {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const removeDelay = prefersReducedMotion ? 0 : 3500;
  setTimeout(() => splashScreen.remove(), removeDelay);
}

// -------- Language chip strip --------

const LANGUAGE_TO_BCP47 = {
  Arabic: "ar-SA",
  Chinese: "zh-CN",
  English: "en-US",
  French: "fr-FR",
  German: "de-DE",
  Hindi: "hi-IN",
  Japanese: "ja-JP",
  Korean: "ko-KR",
  Portuguese: "pt-PT",
  Spanish: "es-ES",
};

const langChips = document.querySelectorAll(".lang-chip");

langChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const lang = chip.dataset.lang;
    if (languageSelect) {
      languageSelect.value = lang;
    }
    langChips.forEach((c) => c.classList.toggle("is-active", c === chip));
  });
});

// keep chips in sync if the dropdown itself is changed directly
if (languageSelect) {
  languageSelect.addEventListener("change", () => {
    langChips.forEach((c) => {
      c.classList.toggle("is-active", c.dataset.lang === languageSelect.value);
    });
  });
}

// -------- Listen button (Web Speech API text-to-speech) --------

const listenBtn = document.getElementById("listen-btn");
const listenIconPlay = listenBtn?.querySelector(".listen-icon-play");
const listenIconStop = listenBtn?.querySelector(".listen-icon-stop");

if (listenBtn && "speechSynthesis" in window) {
  listenBtn.addEventListener("click", () => {
    // if already speaking, stop instead of starting a new utterance
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      setListenState(false);
      return;
    }

    const text = resultTranslation.textContent.trim();
    if (!text) return;

    const targetLanguage = languageSelect.value;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = LANGUAGE_TO_BCP47[targetLanguage] || "en-US";

    utterance.onstart = () => setListenState(true);
    utterance.onend = () => setListenState(false);
    utterance.onerror = () => setListenState(false);

    window.speechSynthesis.speak(utterance);
  });
} else if (listenBtn) {
  // browser doesn't support speech synthesis at all
  listenBtn.disabled = true;
  listenBtn.title = "Text-to-speech isn't supported in this browser";
}

function setListenState(isSpeaking) {
  listenBtn.classList.toggle("is-speaking", isSpeaking);
  if (listenIconPlay) listenIconPlay.hidden = isSpeaking;
  if (listenIconStop) listenIconStop.hidden = !isSpeaking;
}

// stop any speech in progress if a new scan starts
scanButton.addEventListener("click", () => {
  if (window.speechSynthesis?.speaking) {
    window.speechSynthesis.cancel();
    setListenState(false);
  }
});