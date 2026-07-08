async function loadSigns() {
    try {
        const response = await fetch("/api/signs");
        const signs = await response.json();
        const container = document.getElementById("signs-list");
        container.innerHTML = "";
        for (const [term, meaning] of Object.entries(signs)) {
            const div = document.createElement("div");
            div.className = "sign-item";
            div.innerHTML = `<div class="sign-term">${term}</div><div class="sign-meaning">${meaning}</div>`;
            container.appendChild(div);
        }
    } catch (error) {
        document.getElementById("signs-list").innerHTML = "Failed to load signs.";
    }
}


document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("image-input");
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload-image", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `
            <strong>Extracted Text:</strong> ${data.extracted_text}<br>
            <strong>Translated:</strong> ${data.translated_text}<br>
            <strong>Sign Meaning:</strong> ${data.sign_meaning}
        `;
    } catch (error) {
        document.getElementById("result").innerHTML = "Error processing image.";
    }
});


loadSigns();
