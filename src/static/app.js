document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const messageText = document.getElementById("message-text");
  const messageClose = document.querySelector(".notification-close");
  let messageTimeout;

  // Handle message close button
  messageClose.addEventListener("click", () => {
    closeNotification();
  });

  function showNotification(text, type = "success") {
    // Clear any existing timeout
    if (messageTimeout) {
      clearTimeout(messageTimeout);
    }

    messageText.textContent = text;
    messageDiv.className = `notification ${type}`;
    messageDiv.classList.remove("hidden");

    // Auto-close after 5 seconds
    messageTimeout = setTimeout(() => {
      closeNotification();
    }, 5000);
  }

  function closeNotification() {
    messageDiv.classList.add("closing");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
      messageDiv.classList.remove("closing");
    }, 300);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsList = details.participants.map(p => `<li><span class="participant-email">${p}</span><button class="delete-btn" data-activity="${name}" data-email="${p}" title="Remove participant" aria-label="Remove ${p} from ${name}">×</button></li>`).join('');

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants (${details.participants.length}/${details.max_participants}):</strong>
            <ul class="participants-list">
              ${participantsList || '<li class="no-participants">No participants yet</li>'}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete button event listeners
        const deleteButtons = activityCard.querySelectorAll(".delete-btn");
        deleteButtons.forEach(btn => {
          btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const activity = btn.getAttribute("data-activity");
            const email = btn.getAttribute("data-email");

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activity)}/remove?email=${encodeURIComponent(email)}`,
                { method: "DELETE" }
              );

              if (response.ok) {
                showNotification(`${email} has been removed from ${activity}`, "success");
                // Refresh activities
                fetchActivities();
              } else {
                const result = await response.json();
                showNotification(result.detail || "Failed to remove participant", "error");
              }
            } catch (error) {
              showNotification("Failed to remove participant. Please try again.", "error");
              console.error("Error removing participant:", error);
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showNotification(result.message, "success");
        signupForm.reset();
        // Refresh activities to show updated participant count
        fetchActivities();
      } else {
        showNotification(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showNotification("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
