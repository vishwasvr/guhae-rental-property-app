// Add Property Page JavaScript
class AddPropertyManager {
  constructor() {
    this.initializePage();
    this.setupEventListeners();
  }

  async initializePage() {
    try {
      // Verify authentication
      if (!AuthUtils.isAuthenticated()) {
        window.location.href = "index.html";
        return;
      }

      // Update user display
      await this.updateUserDisplay();

      // Populate state dropdown
      this.populateStateDropdown();
    } catch (error) {
      console.error("Error initializing add property page:", error);
      this.showError("Failed to initialize page. Please try again.");
    }
  }

  async updateUserDisplay() {
    try {
      const user = AuthUtils.getCurrentUser();
      if (user) {
        const userNameElement = document.getElementById("user-name");
        if (userNameElement) {
          userNameElement.textContent = user.fullName || "User";
        }
      }
    } catch (error) {
      console.error("Error updating user display:", error);
    }
  }

  populateStateDropdown() {
    try {
      // Use the Components utility to populate the state dropdown
      if (typeof Components !== "undefined" && Components.populateStateSelect) {
        Components.populateStateSelect("state");
      }
    } catch (error) {
      console.error("Error populating state dropdown:", error);
    }
  }

  setupEventListeners() {
    // Form submission
    const form = document.getElementById("addPropertyForm");
    if (form) {
      form.addEventListener("submit", (e) => this.handleFormSubmit(e));

      // Clear messages when user starts typing
      const inputs = form.querySelectorAll("input, textarea, select");
      inputs.forEach((input) => {
        input.addEventListener("input", () => this.clearMessages());
      });
    }

    // Back to dashboard button
    const backButton = document.getElementById("back-to-dashboard");
    if (backButton) {
      backButton.addEventListener("click", () => {
        window.location.href = "dashboard.html";
      });
    }
  }

  async handleFormSubmit(event) {
    event.preventDefault();

    try {
      this.showLoading(true);
      this.clearMessages();

      const form = document.getElementById("addPropertyForm");
      const formData = new FormData(form);

      // Use PropertyService to transform form data
      const propertyData = PropertyService.transformFormData(formData);

      // Submit property using PropertyService
      await PropertyService.createProperty(propertyData);

      this.showSuccess("Property added successfully!");

      // Clear form
      form.reset();

      // Redirect to dashboard after a short delay
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 2000);
    } catch (error) {
      console.error("Error submitting property:", error);
      this.showError(`Failed to add property: ${error.message}`);
      this.showLoading(false);
    }
  }

  showError(message) {
    const errorDiv = document.getElementById("errorMessage");
    const errorText = document.getElementById("errorText");
    if (errorDiv && errorText) {
      errorText.textContent = message;
      errorDiv.classList.remove("d-none");
    }
  }

  showSuccess(message) {
    const successDiv = document.getElementById("successMessage");
    const successText = document.getElementById("successText");
    if (successDiv && successText) {
      successText.textContent = message;
      successDiv.classList.remove("d-none");
    }
  }

  clearMessages() {
    const errorDiv = document.getElementById("errorMessage");
    const successDiv = document.getElementById("successMessage");

    if (errorDiv) {
      errorDiv.classList.add("d-none");
    }

    if (successDiv) {
      successDiv.classList.add("d-none");
    }
  }

  showLoading(show) {
    const submitBtn = document.getElementById("submitBtn");

    if (submitBtn) {
      if (show) {
        submitBtn.disabled = true;
        submitBtn.innerHTML =
          '<i class="fas fa-spinner fa-spin me-2"></i>Adding Property...';
      } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus me-2"></i>Add Property';
      }
    }
  }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  window.addPropertyManager = new AddPropertyManager();
});
