// Profile page functionality

let isEditMode = false;
let originalProfileData = {};

// Initialize profile page
function initProfilePage() {
  // Require authentication
  if (!requireAuth()) {
    return;
  }

  // Populate state dropdown using our components
  Components.populateStateSelect("state");

  loadProfile();

  // Handle form submission
  document
    .getElementById("profileForm")
    .addEventListener("submit", handleProfileUpdate);
}

// Alert display utility for profile page
function showAlert(message, type = "success") {
  const alertElement = document.getElementById(
    type === "success" ? "successAlert" : "errorAlert"
  );
  alertElement.textContent = message;
  alertElement.style.display = "block";

  // Hide other alert
  const otherAlert = document.getElementById(
    type === "success" ? "errorAlert" : "successAlert"
  );
  otherAlert.style.display = "none";

  // Auto-hide after 5 seconds
  setTimeout(() => {
    alertElement.style.display = "none";
  }, 5000);
}

async function loadProfile() {
  try {
    // First get basic user info from localStorage for header
    const userInfo = AuthUtils.getCurrentUser();

    if (userInfo) {
      // Update header with basic info
      document.getElementById("profileName").textContent =
        `${userInfo.firstName || "User"} ${userInfo.lastName || ""}`.trim() ||
        userInfo.email;
      document.getElementById("profileEmail").textContent = userInfo.email;
    }

    // Try to fetch complete profile from backend
    if (AuthUtils.isAuthenticated() && userInfo) {
      try {
        const data = await APIUtils.get(
          `/profile?email=${encodeURIComponent(userInfo.email)}`
        );

        if (data.success && data.profile) {
          loadProfileFromAPI(data.profile);
          return;
        }
      } catch (apiError) {
        console.log(
          "Profile API error, using localStorage fallback:",
          apiError
        );
      }
    }

    // Fallback to localStorage if API fails
    if (userInfo) {
      loadProfileFromStorage(userInfo);
    }
  } catch (error) {
    console.error("Error loading profile:", error);
    showAlert("Failed to load profile information", "error");
  }
}

function loadProfileFromStorage(userData) {
  // Create user model from localStorage data
  const user = new User(userData);

  // Convert user model to profile format for form population
  const profile = {
    firstName: user.firstName,
    lastName: user.lastName,
    email: user.email,
    phone: user.phone,
    dateOfBirth: user.dateOfBirth,
    streetAddress: user.address.streetAddress,
    city: user.address.city,
    state: user.address.state,
    zipCode: user.address.zipCode,
    accountType: user.accountType,
    company: user.company,
  };

  populateProfileForm(profile);
}

function loadProfileFromAPI(apiProfile) {
  // Create user model from API response
  const user = User.fromApiResponse(apiProfile);

  // Update header with API data
  document.getElementById("profileName").textContent = user.displayName;
  document.getElementById("profileEmail").textContent = user.email;

  // Convert user model to profile format for form population
  const profile = {
    firstName: user.firstName,
    lastName: user.lastName,
    email: user.email,
    phone: user.phone,
    dateOfBirth: user.dateOfBirth,
    streetAddress: user.address.streetAddress,
    city: user.address.city,
    state: user.address.state,
    zipCode: user.address.zipCode,
    accountType: user.accountType,
    company: user.company,
  };

  populateProfileForm(profile);
  console.log("Profile loaded from API:", user);
}

function populateProfileForm(profile) {
  // Store original data for cancel functionality
  originalProfileData = { ...profile };

  // Populate form fields
  Object.keys(profile).forEach((key) => {
    const element = document.getElementById(key);
    if (element) {
      element.value = profile[key];
    }
  });
}

function toggleEditMode() {
  isEditMode = !isEditMode;

  const formElements = document.querySelectorAll(
    "#profileForm input:not(#email), #profileForm select"
  );
  const editButton = document.getElementById("editButtonText");
  const editActions = document.getElementById("editActions");

  if (isEditMode) {
    // Enable editing
    formElements.forEach((element) => (element.disabled = false));
    editButton.textContent = "Cancel Edit";
    editActions.style.display = "block";
  } else {
    // Disable editing and restore original data
    cancelEdit();
  }
}

function cancelEdit() {
  isEditMode = false;

  const formElements = document.querySelectorAll(
    "#profileForm input:not(#email), #profileForm select"
  );
  const editButton = document.getElementById("editButtonText");
  const editActions = document.getElementById("editActions");

  // Disable all form elements
  formElements.forEach((element) => (element.disabled = true));

  // Restore original data
  Object.keys(originalProfileData).forEach((key) => {
    const element = document.getElementById(key);
    if (element) {
      element.value = originalProfileData[key];
    }
  });

  editButton.textContent = "Edit Profile";
  editActions.style.display = "none";

  // Hide any alerts
  document.getElementById("successAlert").style.display = "none";
  document.getElementById("errorAlert").style.display = "none";
}

async function handleProfileUpdate(event) {
  event.preventDefault();

  if (!isEditMode) return;

  const submitButton = document.querySelector(
    '#profileForm button[type="submit"]'
  );
  const saveButtonText = document.getElementById("saveButtonText");

  // Show loading state
  UIUtils.showLoading(saveButtonText, "Saving...");
  submitButton.disabled = true;

  try {
    // Collect form data using FormUtils
    const formData = FormUtils.getFormData(
      document.getElementById("profileForm")
    );

    // Create user model from form data (keeping existing email)
    const currentUser = AuthUtils.getCurrentUser();
    const updatedUser = new User({
      email: currentUser.email, // Keep existing email
      firstName: formData.firstName,
      lastName: formData.lastName,
      phone: formData.phone,
      dateOfBirth: formData.dateOfBirth,
      accountType: formData.accountType,
      company: formData.company || null,
      address: Address.fromFormData(formData),
    });

    // Validate using model validation
    const validation = updatedUser.validate();
    if (!validation.isValid) {
      throw new Error(validation.errors[0]);
    }

    // Send to backend API using model's API format
    const updatePayload = updatedUser.toApiFormat();
    updatePayload.email = currentUser.email; // Ensure email is included for backend identification

    const result = await APIUtils.put("/profile", updatePayload);

    if (result.success) {
      // Update localStorage with new user model data
      AuthUtils.storeAuthData(null, updatedUser);
    }

    showAlert("Profile updated successfully!");

    // Update original data and exit edit mode
    originalProfileData = {
      firstName: updatedUser.firstName,
      lastName: updatedUser.lastName,
      phone: updatedUser.phone,
      dateOfBirth: updatedUser.dateOfBirth,
      streetAddress: updatedUser.address.streetAddress,
      city: updatedUser.address.city,
      state: updatedUser.address.state,
      zipCode: updatedUser.address.zipCode,
      accountType: updatedUser.accountType,
      company: updatedUser.company,
    };
    toggleEditMode();
  } catch (error) {
    console.error("Profile update error:", error);
    showAlert(error.message || "Failed to update profile", "error");
  } finally {
    // Hide loading state
    UIUtils.hideLoading(saveButtonText);
    submitButton.disabled = false;
  }
}

// Make functions globally available
window.toggleEditMode = toggleEditMode;
window.cancelEdit = cancelEdit;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initProfilePage);
