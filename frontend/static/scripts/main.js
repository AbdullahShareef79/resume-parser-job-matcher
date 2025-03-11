document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("resumeFile");
    const fileName = document.getElementById("fileName");
    const submitButton = document.getElementById("submitButton");
    const uploadForm = document.getElementById("uploadForm");
    const loading = document.getElementById("loading");
    const errorBox = document.getElementById("error");
    const results = document.getElementById("results");

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
            fileName.style.display = "block";
            submitButton.disabled = false;
        }
    });

    uploadForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        submitButton.disabled = true;
        loading.style.display = "block";
        errorBox.style.display = "none";
        results.style.display = "none";

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                results.innerHTML = `<p>Job matches found: ${result.matches}</p>`;
                results.style.display = "block";
            } else {
                errorBox.textContent = result.error || "Error processing the file.";
                errorBox.style.display = "block";
            }
        } catch (error) {
            errorBox.textContent = "Server error. Please try again later.";
            errorBox.style.display = "block";
        } finally {
            loading.style.display = "none";
            submitButton.disabled = false;
        }
    });
});
