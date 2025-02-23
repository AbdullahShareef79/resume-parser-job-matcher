document.getElementById("uploadForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const submitBtn = document.getElementById("submitBtn");
    const loading = document.getElementById("loading");
    const errorMessage = document.getElementById("errorMessage");

    submitBtn.disabled = true;
    loading.style.display = "inline-block";
    errorMessage.textContent = "";

    const formData = new FormData();
    formData.append("file", document.getElementById("resumeFile").files[0]);

    try {
        const response = await fetch("/upload/", {
            method: "POST",
            body: formData,
        });
    
        if (!response.ok) {
            throw new Error("Failed to upload resume. Please try again.");
        }
    
        const data = await response.json(); // This might fail if the response is not JSON
        
        // Display parsed data
        document.getElementById("parsedData").textContent = JSON.stringify(data.parsed_data, null, 2);
    
        // Display matched jobs
        const jobsList = data.matched_jobs.map(job => `
            <li class="job-card">
                <h3>${job.title}</h3>
                <p><strong>Company:</strong> ${job.company}</p>
                <p><strong>Location:</strong> ${job.location}</p>
                <div class="details">
                    <p><strong>Description:</strong> ${job.description}</p>
                </div>
            </li>
        `).join('');
        document.getElementById("matchedJobs").innerHTML = jobsList;
    } catch (error) {
        errorMessage.textContent = "An error occurred. " + error.message;
    } finally {
        submitBtn.disabled = false;
        loading.style.display = "none";
    }
    
});