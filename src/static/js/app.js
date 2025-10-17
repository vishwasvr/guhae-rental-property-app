// Guhae Frontend JavaScript

// Global app object
const GuhaeApp = {
  // API endpoints
  API: {
    BASE_URL: "/api/v1",
    PROPERTIES: "/api/v1/properties",
  },

  // Utility functions
  Utils: {
    // Show loading spinner
    showLoading: (element) => {
      if (element) {
        element.classList.add("loading");
      }
    },

    // Hide loading spinner
    hideLoading: (element) => {
      if (element) {
        element.classList.remove("loading");
      }
    },

    // Format currency
    formatCurrency: (amount) => {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
    },

    // Format date
    formatDate: (dateString) => {
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },

    // Show toast notification
    showToast: (message, type = "info") => {
      // Create toast element
      const toast = document.createElement("div");
      toast.className = `toast align-items-center text-white bg-${type} border-0`;
      toast.setAttribute("role", "alert");
      toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;

      // Add to toast container (create if doesn't exist)
      let toastContainer = document.getElementById("toast-container");
      if (!toastContainer) {
        toastContainer = document.createElement("div");
        toastContainer.id = "toast-container";
        toastContainer.className =
          "toast-container position-fixed top-0 end-0 p-3";
        toastContainer.style.zIndex = "1100";
        document.body.appendChild(toastContainer);
      }

      toastContainer.appendChild(toast);

      // Show toast
      const bsToast = new bootstrap.Toast(toast);
      bsToast.show();

      // Remove from DOM after hiding
      toast.addEventListener("hidden.bs.toast", () => {
        toast.remove();
      });
    },

    // Debounce function for search
    debounce: (func, wait) => {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },
  },

  // Property management functions
  Properties: {
    // Delete property
    delete: async (propertyId) => {
      try {
        const response = await fetch(
          `${GuhaeApp.API.PROPERTIES}/${propertyId}`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        const data = await response.json();

        if (response.ok) {
          GuhaeApp.Utils.showToast("Property deleted successfully", "success");
          return true;
        } else {
          throw new Error(data.error || "Failed to delete property");
        }
      } catch (error) {
        GuhaeApp.Utils.showToast(`Error: ${error.message}`, "danger");
        return false;
      }
    },

    // Update property
    update: async (propertyId, data) => {
      try {
        const response = await fetch(
          `${GuhaeApp.API.PROPERTIES}/${propertyId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
          }
        );

        const result = await response.json();

        if (response.ok) {
          GuhaeApp.Utils.showToast("Property updated successfully", "success");
          return result;
        } else {
          throw new Error(result.error || "Failed to update property");
        }
      } catch (error) {
        GuhaeApp.Utils.showToast(`Error: ${error.message}`, "danger");
        throw error;
      }
    },

    // Upload image
    uploadImage: async (propertyId, file) => {
      try {
        const formData = new FormData();
        formData.append("image", file);

        const response = await fetch(
          `${GuhaeApp.API.PROPERTIES}/${propertyId}/images`,
          {
            method: "POST",
            body: formData,
          }
        );

        const data = await response.json();

        if (response.ok) {
          GuhaeApp.Utils.showToast("Image uploaded successfully", "success");
          return data.image_url;
        } else {
          throw new Error(data.error || "Failed to upload image");
        }
      } catch (error) {
        GuhaeApp.Utils.showToast(`Error: ${error.message}`, "danger");
        throw error;
      }
    },
  },

  // Search functionality
  Search: {
    // Initialize search
    init: () => {
      const searchInput = document.getElementById("search");
      if (searchInput) {
        searchInput.addEventListener(
          "input",
          GuhaeApp.Utils.debounce(GuhaeApp.Search.performSearch, 300)
        );
      }
    },

    // Perform search
    performSearch: () => {
      const searchTerm = document.getElementById("search").value;
      if (searchTerm.length > 2) {
        // Perform search (implement based on your needs)
        console.log("Searching for:", searchTerm);
      }
    },
  },

  // Form validation
  Validation: {
    // Validate property form
    validatePropertyForm: (formData) => {
      const errors = [];

      if (
        !formData.get("address") ||
        formData.get("address").trim().length < 5
      ) {
        errors.push("Address must be at least 5 characters long");
      }

      if (!formData.get("rent") || parseFloat(formData.get("rent")) <= 0) {
        errors.push("Rent must be a positive number");
      }

      if (!formData.get("property_type")) {
        errors.push("Property type is required");
      }

      return errors;
    },

    // Show validation errors
    showErrors: (errors, formElement) => {
      // Clear previous errors
      formElement.querySelectorAll(".is-invalid").forEach((el) => {
        el.classList.remove("is-invalid");
      });
      formElement.querySelectorAll(".invalid-feedback").forEach((el) => {
        el.textContent = "";
      });

      if (errors.length > 0) {
        errors.forEach((error) => {
          GuhaeApp.Utils.showToast(error, "danger");
        });
        return false;
      }

      return true;
    },
  },
};

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize search
  GuhaeApp.Search.init();

  // Add smooth scrolling to anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });

  // Auto-hide alerts after 5 seconds
  setTimeout(() => {
    document.querySelectorAll(".alert").forEach((alert) => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);

  // Add loading states to buttons
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';

        // Re-enable after 5 seconds (fallback)
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }, 5000);
      }
    });
  });

  console.log("Guhae App initialized successfully");
});

// Global error handler
window.addEventListener("error", function (e) {
  console.error("Global error:", e.error);
  GuhaeApp.Utils.showToast("An unexpected error occurred", "danger");
});

// Export for use in other scripts
window.GuhaeApp = GuhaeApp;
