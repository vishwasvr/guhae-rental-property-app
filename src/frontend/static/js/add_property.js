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

      const formData = this.collectFormData();

      // Validate form data
      const validation = this.validateFormData(formData);
      if (!validation.isValid) {
        this.showError(validation.message);
        this.showLoading(false);
        return;
      }

      // Submit property
      await this.submitProperty(formData);
    } catch (error) {
      console.error("Error submitting property:", error);
      this.showError("Failed to add property. Please try again.");
      this.showLoading(false);
    }
  }

  collectFormData() {
    const form = document.getElementById("addPropertyForm");
    const formData = new FormData(form);

    // Combine address fields into a full address
    const streetAddress = formData.get("streetAddress")?.trim();
    const city = formData.get("city")?.trim();
    const state = formData.get("state");
    const zipCode = formData.get("zipCode")?.trim();
    const fullAddress = `${streetAddress}, ${city}, ${state} ${zipCode}`;

    return {
      title: formData.get("title")?.trim(),
      property_type: formData.get("property_type"),
      address: fullAddress,
      streetAddress: streetAddress,
      city: city,
      state: state,
      zipCode: zipCode,
      description: formData.get("description")?.trim(),
      price: parseFloat(formData.get("price")),
      bedrooms: parseInt(formData.get("bedrooms")),
      bathrooms: parseFloat(formData.get("bathrooms")),
    };
  }

  validateFormData(data) {
    if (!data.title) {
      return { isValid: false, message: "Property title is required." };
    }

    if (!data.property_type) {
      return { isValid: false, message: "Property type is required." };
    }

    if (!data.streetAddress) {
      return { isValid: false, message: "Street address is required." };
    }

    if (!data.city) {
      return { isValid: false, message: "City is required." };
    }

    if (!data.state) {
      return { isValid: false, message: "State is required." };
    }

    if (!data.zipCode) {
      return { isValid: false, message: "Zip code is required." };
    }

    // Validate zip code format
    const zipPattern = /^[0-9]{5}(-[0-9]{4})?$/;
    if (!zipPattern.test(data.zipCode)) {
      return {
        isValid: false,
        message: "Please enter a valid zip code (12345 or 12345-6789).",
      };
    }

    if (!data.description) {
      return { isValid: false, message: "Description is required." };
    }

    if (!data.price || data.price <= 0) {
      return { isValid: false, message: "Please enter a valid price." };
    }

    if (!data.bedrooms || data.bedrooms < 0) {
      return {
        isValid: false,
        message: "Please enter a valid number of bedrooms.",
      };
    }

    if (!data.bathrooms || data.bathrooms < 0) {
      return {
        isValid: false,
        message: "Please enter a valid number of bathrooms.",
      };
    }

    return { isValid: true };
  }

  async submitProperty(propertyData) {
    try {
      if (!AuthUtils.isAuthenticated()) {
        throw new Error("Authentication token not found");
      }

      const result = await APIUtils.post("/properties", propertyData);

      this.showSuccess("Property added successfully!");

      // Clear form
      document.getElementById("addPropertyForm").reset(); // Redirect to dashboard after a short delay
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 2000);
    } catch (error) {
      console.error("Error submitting property:", error);
      throw error;
    } finally {
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
