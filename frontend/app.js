// API Configuration
const API_BASE_URL = "http://localhost:8000";
const API_VERSION = "/api/v1";

// Store recent job IDs
let recentJobIds = JSON.parse(localStorage.getItem("recentJobIds") || "[]");

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  initializeApp();
});

function initializeApp() {
  // Setup file input handler
  const fileInput = document.getElementById("fileInput");
  const fileName = document.getElementById("fileName");

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      fileName.textContent = e.target.files[0].name;
    } else {
      fileName.textContent = "No file selected";
    }
  });

  // Setup form submission
  const uploadForm = document.getElementById("uploadForm");
  uploadForm.addEventListener("submit", handleUpload);

  // Load recent jobs if any
  if (recentJobIds.length > 0) {
    loadRecentJobs();
  }

  // Check health on load
  checkHealth();
}

// Handle file upload
async function handleUpload(e) {
  e.preventDefault();

  const fileInput = document.getElementById("fileInput");
  const recipientEmail = document.getElementById("recipientEmail").value;
  const userId = document.getElementById("userId").value;
  const uploadBtn = document.getElementById("uploadBtn");
  const uploadStatus = document.getElementById("uploadStatus");

  // Validate file
  if (!fileInput.files || fileInput.files.length === 0) {
    showStatus("error", "Please select a PDF file", uploadStatus);
    return;
  }

  const file = fileInput.files[0];

  // Check file type
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showStatus("error", "Please select a valid PDF file", uploadStatus);
    return;
  }

  // Show loading state
  toggleButtonLoading(uploadBtn, true);
  uploadStatus.style.display = "none";

  try {
    // Create form data
    const formData = new FormData();
    formData.append("file", file);
    formData.append("recipient_email", recipientEmail);
    formData.append("user_id", userId);

    // Upload file
    const response = await fetch(
      `${API_BASE_URL}${API_VERSION}/documents/upload`,
      {
        method: "POST",
        body: formData,
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload failed");
    }

    const data = await response.json();

    // Store job ID
    addRecentJob(data.job_id);

    // Show success message
    showStatus(
      "success",
      `
            <strong>✅ Upload Successful!</strong><br>
            Document: ${data.document.original_filename}<br>
            Job ID: <code>${data.job_id}</code><br>
            Status: PENDING
        `,
      uploadStatus,
    );

    showToast("Document uploaded successfully!", "success");

    // Update job ID input
    document.getElementById("jobIdInput").value = data.job_id;

    // Load job details
    await loadJobDetails(data.job_id);

    // Refresh recent jobs
    loadRecentJobs();

    // Reset form
    uploadForm.reset();
    document.getElementById("fileName").textContent = "No file selected";

    // Start polling for job status
    pollJobStatus(data.job_id);
  } catch (error) {
    console.error("Upload error:", error);
    showStatus("error", `❌ ${error.message}`, uploadStatus);
    showToast(error.message, "error");
  } finally {
    toggleButtonLoading(uploadBtn, false);
  }
}

// Check job status
async function checkJobStatus() {
  const jobId = document.getElementById("jobIdInput").value.trim();

  if (!jobId) {
    showToast("Please enter a Job ID", "error");
    return;
  }

  await loadJobDetails(jobId);
}

// Load job details
async function loadJobDetails(jobId) {
  const jobDetails = document.getElementById("jobDetails");

  try {
    jobDetails.innerHTML = '<div class="loading">Loading job details...</div>';

    const response = await fetch(`${API_BASE_URL}${API_VERSION}/jobs/${jobId}`);

    if (!response.ok) {
      throw new Error("Job not found");
    }

    const job = await response.json();

    // Render job details
    jobDetails.innerHTML = renderJobDetails(job);
  } catch (error) {
    console.error("Error loading job:", error);
    jobDetails.innerHTML = `
            <div class="status-message error show">
                ❌ ${error.message}
            </div>
        `;
  }
}

// Render job details
function renderJobDetails(job) {
  const statusClass = `status-${job.status.toLowerCase()}`;
  const executionTime = job.execution_time_ms
    ? `${(job.execution_time_ms / 1000).toFixed(2)}s`
    : "N/A";

  let html = `
        <div class="job-info">
            <div class="job-header">
                <div class="job-id">Job ID: ${job.job_id}</div>
                <span class="status-badge ${statusClass}">${job.status}</span>
            </div>
            
            <div class="job-details-grid">
                <div class="detail-item">
                    <div class="detail-label">Document ID</div>
                    <div class="detail-value">#${job.document_id}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Execution Time</div>
                    <div class="detail-value">${executionTime}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Retry Count</div>
                    <div class="detail-value">${job.retry_count} / ${job.max_retries}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Created At</div>
                    <div class="detail-value">${formatDate(job.created_at)}</div>
                </div>
            </div>
    `;

  // Add error message if failed
  if (job.error_message) {
    html += `
            <div class="status-message error show" style="margin-top: 16px;">
                <strong>Error:</strong> ${job.error_message}
            </div>
        `;
  }

  // Agent outputs
  if (job.agent_outputs && job.agent_outputs.length > 0) {
    html +=
      '<h3 style="margin-top: 24px; margin-bottom: 12px;">🤖 Agent Outputs</h3>';
    job.agent_outputs.forEach((output) => {
      html += `
                <div class="detail-item" style="margin-bottom: 12px;">
                    <div class="detail-label">${output.agent_name} (${output.agent_role})</div>
                    <div class="detail-value" style="font-size: 0.875rem; font-weight: normal; margin-top: 8px;">
                        ${output.execution_time_ms ? `⏱️ ${(output.execution_time_ms / 1000).toFixed(2)}s` : ""}
                    </div>
                    ${output.output_data ? `<div class="json-display"><pre>${JSON.stringify(output.output_data, null, 2)}</pre></div>` : ""}
                </div>
            `;
    });
  }

  // Email records
  if (job.email_records && job.email_records.length > 0) {
    html +=
      '<h3 style="margin-top: 24px; margin-bottom: 12px;">📧 Email Records</h3>';
    job.email_records.forEach((email) => {
      const emailStatusClass = email.status === "sent" ? "success" : "error";
      html += `
                <div class="detail-item" style="margin-bottom: 12px;">
                    <div class="detail-label">To: ${email.to_email}</div>
                    <div class="detail-value" style="font-size: 0.875rem;">
                        ${email.subject}
                    </div>
                    <span class="status-badge status-${emailStatusClass}" style="margin-top: 8px; display: inline-block;">
                        ${email.status}
                    </span>
                    ${email.error_message ? `<div class="status-message error show" style="margin-top: 8px; font-size: 0.875rem;">${email.error_message}</div>` : ""}
                </div>
            `;
    });
  }

  // Execution logs
  if (job.execution_logs && job.execution_logs.length > 0) {
    html +=
      '<h3 style="margin-top: 24px; margin-bottom: 12px;">📋 Execution Logs</h3>';
    html += '<div class="logs-section">';
    job.execution_logs.forEach((log) => {
      html += `
                <div class="log-entry ${log.level}">
                    <div><strong>${log.step}</strong>: ${log.message}</div>
                    <div class="log-time">${formatDate(log.created_at)}</div>
                </div>
            `;
    });
    html += "</div>";
  }

  html += "</div>";
  return html;
}

// Poll job status
async function pollJobStatus(jobId, maxAttempts = 60) {
  let attempts = 0;

  const poll = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}${API_VERSION}/jobs/${jobId}`,
      );
      const job = await response.json();

      // Update display
      await loadJobDetails(jobId);

      // Check if job is complete
      if (job.status === "completed" || job.status === "failed") {
        showToast(
          `Job ${job.status}!`,
          job.status === "completed" ? "success" : "error",
        );
        loadRecentJobs(); // Refresh recent jobs
        return;
      }

      // Continue polling
      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(poll, 2000); // Poll every 2 seconds
      }
    } catch (error) {
      console.error("Polling error:", error);
    }
  };

  poll();
}

// Load recent jobs
async function loadRecentJobs() {
  const recentJobsDiv = document.getElementById("recentJobs");

  if (recentJobIds.length === 0) {
    recentJobsDiv.innerHTML =
      '<p class="empty-state">No recent jobs yet. Upload a document to get started!</p>';
    return;
  }

  recentJobsDiv.innerHTML = '<div class="loading">Loading recent jobs...</div>';

  try {
    const jobPromises = recentJobIds.map(async (jobId) => {
      try {
        const response = await fetch(
          `${API_BASE_URL}${API_VERSION}/jobs/${jobId}`,
        );
        if (response.ok) {
          return await response.json();
        }
      } catch (error) {
        console.error(`Error loading job ${jobId}:`, error);
      }
      return null;
    });

    const jobs = (await Promise.all(jobPromises)).filter((j) => j !== null);

    if (jobs.length === 0) {
      recentJobsDiv.innerHTML = '<p class="empty-state">No jobs found.</p>';
      return;
    }

    let html = "";
    jobs.forEach((job) => {
      const statusClass = `status-${job.status.toLowerCase()}`;
      html += `
                <div class="job-item" onclick="loadJobDetails('${job.job_id}')">
                    <div class="job-item-header">
                        <span class="job-item-id">${job.job_id}</span>
                        <span class="status-badge ${statusClass}">${job.status}</span>
                    </div>
                    <div class="job-item-details">
                        Document #${job.document_id} • ${formatDate(job.created_at)}
                    </div>
                </div>
            `;
    });

    recentJobsDiv.innerHTML = html;
  } catch (error) {
    console.error("Error loading recent jobs:", error);
    recentJobsDiv.innerHTML = '<p class="empty-state">Error loading jobs.</p>';
  }
}

// Check system health
async function checkHealth() {
  const healthDetails = document.getElementById("healthDetails");

  try {
    healthDetails.innerHTML =
      '<div class="loading">Checking system health...</div>';

    const response = await fetch(`${API_BASE_URL}/health`);
    const health = await response.json();

    let html = '<div class="health-details">';
    html += `
            <div class="health-item">
                <span class="health-check">Status</span>
                <span class="health-ok">✅ ${health.status}</span>
            </div>
            <div class="health-item">
                <span class="health-check">Service</span>
                <span>${health.service}</span>
            </div>
            <div class="health-item">
                <span class="health-check">Version</span>
                <span>${health.version}</span>
            </div>
            <div class="health-item">
                <span class="health-check">Environment</span>
                <span>${health.environment}</span>
            </div>
        `;

    if (health.checks) {
      Object.entries(health.checks).forEach(([key, value]) => {
        const isHealthy = value === "healthy";
        html += `
                    <div class="health-item">
                        <span class="health-check">${key}</span>
                        <span class="${isHealthy ? "health-ok" : "health-error"}">
                            ${isHealthy ? "✅" : "❌"} ${value}
                        </span>
                    </div>
                `;
      });
    }

    html += "</div>";
    healthDetails.innerHTML = html;
  } catch (error) {
    console.error("Health check error:", error);
    healthDetails.innerHTML = `
            <div class="status-message error show">
                ❌ Failed to check system health
            </div>
        `;
  }
}

// Utility Functions

function showStatus(type, message, element) {
  element.className = `status-message ${type} show`;
  element.innerHTML = message;
  element.style.display = "block";
}

function toggleButtonLoading(button, isLoading) {
  const btnText = button.querySelector(".btn-text");
  const btnLoader = button.querySelector(".btn-loader");

  if (isLoading) {
    btnText.style.display = "none";
    btnLoader.style.display = "flex";
    button.disabled = true;
  } else {
    btnText.style.display = "inline";
    btnLoader.style.display = "none";
    button.disabled = false;
  }
}

function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type} show`;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function addRecentJob(jobId) {
  // Add to beginning of array
  recentJobIds = [jobId, ...recentJobIds.filter((id) => id !== jobId)];

  // Keep only last 10
  if (recentJobIds.length > 10) {
    recentJobIds = recentJobIds.slice(0, 10);
  }

  // Save to localStorage
  localStorage.setItem("recentJobIds", JSON.stringify(recentJobIds));
}

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + Enter to check job status
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    const jobIdInput = document.getElementById("jobIdInput");
    if (document.activeElement === jobIdInput) {
      checkJobStatus();
    }
  }
});
