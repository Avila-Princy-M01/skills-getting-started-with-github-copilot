document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

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

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-list">
            <h5>Current Participants:</h5>
            <ul>
              ${details.participants.map(email => `<li>${email} <button class="delete-participant" data-email="${email}">Delete</button></li>`).join('')}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

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
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Dynamically update the participant list
        const activityCard = [...activitiesList.children].find(card => card.querySelector('h4').textContent === activity);
        if (activityCard) {
          const participantsList = activityCard.querySelector('.participants-list ul');
          const newParticipant = document.createElement('li');
          newParticipant.innerHTML = `${email} <button class="delete-participant" data-email="${email}">Delete</button>`;
          participantsList.appendChild(newParticipant);
        }
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle participant deletion
  document.getElementById("participants-list").addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-participant")) {
      const email = event.target.dataset.email;
      const activity = document.getElementById("activity").value;

      try {
        const response = await fetch(`/activities/${activity}/unregister?email=${email}`, {
          method: "DELETE",
        });

        if (response.ok) {
          event.target.parentElement.remove();
          console.log(`Successfully unregistered ${email} from ${activity}`);
        } else {
          console.error("Failed to unregister participant.");
        }
      } catch (error) {
        console.error("Error unregistering participant:", error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
