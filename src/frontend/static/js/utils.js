// Common utilities and configuration for the Guhae application

// Configuration
const CONFIG = {
  API_BASE_URL:
    "https://exs79pbewg.execute-api.us-east-1.amazonaws.com/prod/api",
  STORAGE_KEYS: {
    ACCESS_TOKEN: "accessToken",
    ID_TOKEN: "idToken",
    REFRESH_TOKEN: "refreshToken",
    USER_INFO: "userInfo",
  },
};

// Authentication utilities
const AuthUtils = {
  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
  },

  // Get current user info
  getCurrentUser() {
    const userInfo = localStorage.getItem(CONFIG.STORAGE_KEYS.USER_INFO);
    return userInfo ? JSON.parse(userInfo) : null;
  },

  // Get authentication headers for API requests
  getAuthHeaders() {
    const token = localStorage.getItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  // Get access token
  getToken() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
  },

  // Clear all authentication data
  logout() {
    localStorage.removeItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.ID_TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_INFO);
    window.location.href = "index.html";
  },

  // Store authentication data
  storeAuthData(tokens, userInfo) {
    if (tokens) {
      localStorage.setItem(
        CONFIG.STORAGE_KEYS.ACCESS_TOKEN,
        tokens.access_token
      );
      localStorage.setItem(CONFIG.STORAGE_KEYS.ID_TOKEN, tokens.id_token);
      localStorage.setItem(
        CONFIG.STORAGE_KEYS.REFRESH_TOKEN,
        tokens.refresh_token
      );
    }

    if (userInfo) {
      localStorage.setItem(
        CONFIG.STORAGE_KEYS.USER_INFO,
        JSON.stringify(userInfo)
      );
    }
  },

  // Update user info in localStorage
  updateUserInfo(userInfo) {
    if (userInfo) {
      localStorage.setItem(
        CONFIG.STORAGE_KEYS.USER_INFO,
        JSON.stringify(userInfo)
      );
    }
  },
};

// API utilities
const APIUtils = {
  // Make authenticated API request
  async request(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const defaultHeaders = {
      "Content-Type": "application/json",
      ...AuthUtils.getAuthHeaders(),
    };

    const config = {
      headers: defaultHeaders,
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        const error = new Error(
          data.message || `HTTP ${response.status}: ${response.statusText}`
        );
        error.status = response.status;
        error.statusText = response.statusText;
        error.response = data;
        throw error;
      }

      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  },

  // Convenience methods for different HTTP verbs
  get(endpoint, options = {}) {
    return this.request(endpoint, { method: "GET", ...options });
  },

  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
      ...options,
    });
  },

  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
      ...options,
    });
  },

  delete(endpoint, options = {}) {
    return this.request(endpoint, { method: "DELETE", ...options });
  },

  // Alias for backward compatibility
  makeRequest(endpoint, options = {}) {
    return this.request(endpoint, options);
  },
};

// UI utilities
const UIUtils = {
  // Show loading state
  showLoading(element, text = "Loading...") {
    if (!element) return;

    element.dataset.originalText = element.innerHTML;
    element.disabled = true;
    element.innerHTML = `<div class="loading-spinner"></div> ${text}`;
  },

  // Hide loading state
  hideLoading(element) {
    if (!element) return;

    element.disabled = false;
    element.innerHTML = element.dataset.originalText || element.innerHTML;
    delete element.dataset.originalText;
  },

  // Show message in element
  showMessage(elementId, message, type = "info") {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.textContent = message;
    element.className = `alert alert-${type}`;
    element.style.display = "block";
  },

  // Hide message element
  hideMessage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.style.display = "none";
    }
  },

  // Animate element entrance
  animateIn(element, delay = 0) {
    if (!element) return;

    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";

    setTimeout(() => {
      element.style.transition = "all 0.6s ease";
      element.style.opacity = "1";
      element.style.transform = "translateY(0)";
    }, delay);
  },
};

// Form utilities
const FormUtils = {
  // Validate email format
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Validate phone number format
  isValidPhone(phone) {
    const phoneRegex = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
    return phoneRegex.test(phone);
  },

  // Validate ZIP code format
  isValidZipCode(zipCode) {
    const zipRegex = /^\d{5}(-\d{4})?$/;
    return zipRegex.test(zipCode);
  },

  // Get form data as object
  getFormData(formElement) {
    const formData = new FormData(formElement);
    const data = {};

    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }

    return data;
  },

  // Clear form
  clearForm(formElement) {
    if (formElement) {
      formElement.reset();
    }
  },
};

// String formatting utilities
const StringUtils = {
  // Capitalize first letter of each word
  capitalize(str) {
    if (!str) return "";
    return str.replace(/\b\w/g, (l) => l.toUpperCase());
  },

  // Capitalize first letter only
  capitalizeFirst(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },

  // Convert to title case (proper case)
  toTitleCase(str) {
    if (!str) return "";
    return str.replace(
      /\w\S*/g,
      (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
  },
};

// Page protection - redirect to login if not authenticated
function requireAuth() {
  if (!AuthUtils.isAuthenticated()) {
    window.location.href = "index.html";
    return false;
  }
  return true;
}

// Global error handler
window.addEventListener("error", (event) => {
  console.error("Global error:", event.error);
});

// Export utilities globally
window.CONFIG = CONFIG;
window.AuthUtils = AuthUtils;
window.APIUtils = APIUtils;
window.UIUtils = UIUtils;
window.FormUtils = FormUtils;
window.StringUtils = StringUtils;
window.requireAuth = requireAuth;
