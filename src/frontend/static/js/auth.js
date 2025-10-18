// Authentication page specific functionality

// Utility functions for messages (specific to auth page layout)
function showError(message) {
  UIUtils.showMessage("errorMessage", message, "danger");
  UIUtils.hideMessage("successMessage");
}

function showSuccess(message) {
  UIUtils.showMessage("successMessage", message, "success");
  UIUtils.hideMessage("errorMessage");
}

function hideMessages() {
  UIUtils.hideMessage("errorMessage");
  UIUtils.hideMessage("successMessage");
} // Authentication functions
async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  // Basic validation
  if (!email || !password) {
    showError("Please enter both email and password");
    return;
  }

  // Show loading state
  const submitButton = event.target.querySelector('button[type="submit"]');
  UIUtils.showLoading(submitButton, "Signing In...");

  try {
    const data = await APIUtils.post("/auth/login", {
      username: email,
      password: password,
    });

    showSuccess("Login successful! Redirecting to dashboard...");

    // Store authentication data
    AuthUtils.storeAuthData(data.tokens, data.user);

    // Redirect to dashboard after a brief delay
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 1500);
  } catch (error) {
    console.error("Login error:", error);
    showError(
      `Connection error: ${error.message}. Check browser console for details.`
    );
  } finally {
    // Hide loading state
    UIUtils.hideLoading(submitButton);
  }
}

async function handleRegistration(event) {
  event.preventDefault();

  // Collect all form data
  const formData = {
    // Personal Information
    firstName: document.getElementById("firstName").value.trim(),
    lastName: document.getElementById("lastName").value.trim(),
    email: document.getElementById("registerEmail").value.trim(),
    phone: document.getElementById("phone").value.trim(),
    dateOfBirth: document.getElementById("dateOfBirth").value,

    // Address Information
    streetAddress: document.getElementById("streetAddress").value.trim(),
    city: document.getElementById("city").value.trim(),
    state: document.getElementById("state").value,
    zipCode: document.getElementById("zipCode").value.trim(),

    // Account Security
    password: document.getElementById("registerPassword").value,
    confirmPassword: document.getElementById("confirmPassword").value,

    // Profile Information
    company: document.getElementById("company").value.trim(),

    // Terms agreement
    agreeTerms: document.getElementById("agreeTerms").checked,
  };

  // Comprehensive validation
  if (!validateRegistrationForm(formData)) {
    return;
  }

  // Show loading state
  const submitButton = event.target.querySelector('button[type="submit"]');
  UIUtils.showLoading(submitButton, "Creating Account...");

  try {
    // Create user model and validate
    const user = new User({
      email: formData.email,
      firstName: formData.firstName,
      lastName: formData.lastName,
      phone: formData.phone,
      dateOfBirth: formData.dateOfBirth,
      company: formData.company || null,
      address: {
        streetAddress: formData.streetAddress,
        city: formData.city,
        state: formData.state,
        zipCode: formData.zipCode,
      },
    });

    // Additional model validation (already done in validateRegistrationForm, but good practice)
    const modelValidation = user.validate();
    if (!modelValidation.isValid) {
      showError(modelValidation.errors[0]);
      return;
    }

    // Prepare payload for backend
    const registrationPayload = {
      username: formData.email,
      password: formData.password,
      email: formData.email,
      profile: user.toApiFormat(),
    };

    const data = await APIUtils.post("/auth/register", registrationPayload);

    showSuccess(
      "Registration successful! Please sign in with your credentials."
    );

    // Switch to login tab
    showLogin();

    // Pre-fill email in login form
    document.getElementById("loginEmail").value = formData.email;
  } catch (error) {
    console.error("Registration error:", error);
    showError(
      `Connection error: ${error.message}. Check browser console for details.`
    );
  } finally {
    // Hide loading state
    UIUtils.hideLoading(submitButton);
  }
}

// Form validation functions
function validateRegistrationForm(formData) {
  const requiredFields = [
    { field: "firstName", message: "First name is required" },
    { field: "lastName", message: "Last name is required" },
    { field: "email", message: "Email address is required" },
    { field: "phone", message: "Phone number is required" },
    { field: "dateOfBirth", message: "Date of birth is required" },
    { field: "streetAddress", message: "Street address is required" },
    { field: "city", message: "City is required" },
    { field: "state", message: "State is required" },
    { field: "zipCode", message: "ZIP code is required" },
    { field: "password", message: "Password is required" },
  ];

  // Check required fields
  for (const req of requiredFields) {
    if (!formData[req.field]) {
      showError(req.message);
      return false;
    }
  }

  // Password validation
  if (formData.password !== formData.confirmPassword) {
    showError("Passwords do not match");
    return false;
  }

  if (formData.password.length < 8) {
    showError("Password must be at least 8 characters long");
    return false;
  }

  // Email validation
  if (!FormUtils.isValidEmail(formData.email)) {
    showError("Please enter a valid email address");
    return false;
  }

  // Phone validation
  if (!FormUtils.isValidPhone(formData.phone)) {
    showError("Please enter a valid phone number");
    return false;
  }

  // ZIP code validation
  if (!FormUtils.isValidZipCode(formData.zipCode)) {
    showError("Please enter a valid ZIP code");
    return false;
  }

  // Terms agreement validation
  if (!formData.agreeTerms) {
    showError("You must agree to the Terms of Service and Privacy Policy");
    return false;
  }

  return true;
}

// Tab switching functions
function showLogin() {
  document.getElementById("loginForm").style.display = "block";
  document.getElementById("registerForm").style.display = "none";

  // Update tab buttons
  const tabs = document.querySelectorAll(".tab-button");
  tabs[0].classList.add("active");
  tabs[1].classList.remove("active");
}

function showRegister() {
  document.getElementById("loginForm").style.display = "none";
  document.getElementById("registerForm").style.display = "block";

  // Update tab buttons
  const tabs = document.querySelectorAll(".tab-button");
  tabs[0].classList.remove("active");
  tabs[1].classList.add("active");
}

// Initialize authentication page
function initAuthPage() {
  // Only redirect if we're on the main auth page (index.html)
  const currentPage = window.location.pathname;
  const isAuthPage =
    currentPage === "/" ||
    currentPage.endsWith("/index.html") ||
    currentPage === "/index.html" ||
    !currentPage ||
    currentPage === "/index";

  // Check if user is already logged in
  if (AuthUtils.isAuthenticated() && isAuthPage) {
    // User is already logged in, redirect to dashboard
    window.location.href = "dashboard.html";
    return;
  }

  // Only run auth page specific initialization if we're on the auth page
  if (isAuthPage) {
    // Populate state dropdown using our components
    try {
      if (typeof Components !== "undefined" && Components.populateStateSelect) {
        Components.populateStateSelect("state");
      }
    } catch (error) {
      console.warn("Could not populate state dropdown:", error);
    }

    // Add event listeners
    try {
      const loginForm = document.getElementById("loginForm");
      const registerForm = document.getElementById("registerForm");

      if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
      }

      if (registerForm) {
        registerForm.addEventListener("submit", handleRegistration);
      }
    } catch (error) {
      console.warn("Could not add form event listeners:", error);
    }

    // Add subtle animation to the welcome card
    try {
      const welcomeCard = document.querySelector(".welcome-card");
      if (welcomeCard && typeof UIUtils !== "undefined" && UIUtils.animateIn) {
        UIUtils.animateIn(welcomeCard, 100);
      }
    } catch (error) {
      console.warn("Could not animate welcome card:", error);
    }
  }
}

// Make functions globally available
window.showLogin = showLogin;
window.showRegister = showRegister;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initAuthPage);
