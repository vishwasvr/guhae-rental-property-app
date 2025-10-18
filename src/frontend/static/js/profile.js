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
          console.log("Profile found in DynamoDB:", data.profile);
          loadProfileFromAPI(data.profile);
          return;
        } else {
          console.log(
            "Profile not found in DynamoDB, attempting to create from localStorage data"
          );
          // Profile doesn't exist in DynamoDB, try to create it from localStorage data
          await createProfileFromLocalStorage(userInfo);
          return;
        }
      } catch (apiError) {
        console.log(
          "Profile API error, using localStorage fallback:",
          apiError
        );
        console.log("Error status:", apiError.status);

        // If it's a 404 (profile not found), try to create the profile
        if (
          apiError.status === 404 ||
          apiError.message?.includes("Profile not found")
        ) {
          console.log(
            "Profile not found (404 or message) - creating profile from localStorage"
          );
          await createProfileFromLocalStorage(userInfo);
          return;
        } else {
          console.log("Other API error, falling back to localStorage display");
          // For other errors, just display what we have in localStorage
          loadProfileFromLocalStorage(userInfo);
        }
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
  console.log("Loading profile from storage with userData:", userData);

  // Handle both our format and Cognito format
  const normalizedData = {
    id: userData.id || userData.sub,
    email: userData.email,
    firstName:
      userData.firstName ||
      userData.given_name ||
      userData.name?.split(" ")[0] ||
      "",
    lastName:
      userData.lastName ||
      userData.family_name ||
      userData.name?.split(" ")[1] ||
      "",
    phone: userData.phone || userData.phone_number || "",
    dateOfBirth: userData.dateOfBirth || userData.birthdate || "",
    // Removed accountType field - all users are property owners now
    company: userData.company || "",
    address: userData.address || {},
  };

  console.log("Normalized userData:", normalizedData);

  // Create user model from normalized data
  const user = new User(normalizedData);
  console.log("Created User model:", user);

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
    company: user.company,
  };

  console.log("Profile data to populate form:", profile);
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
    company: user.company,
  };

  populateProfileForm(profile);
  console.log("Profile loaded from API:", user);
}

async function createProfileFromLocalStorage(userInfo) {
  console.log("Creating profile in DynamoDB from localStorage:", userInfo);

  try {
    // Normalize the data like we do in loadProfileFromStorage
    const normalizedData = {
      id: userInfo.id || userInfo.sub,
      email: userInfo.email,
      firstName:
        userInfo.firstName ||
        userInfo.given_name ||
        userInfo.name?.split(" ")[0] ||
        "",
      lastName:
        userInfo.lastName ||
        userInfo.family_name ||
        userInfo.name?.split(" ")[1] ||
        "",
      phone: userInfo.phone || userInfo.phone_number || "",
      dateOfBirth: userInfo.dateOfBirth || userInfo.birthdate || "",
      company: userInfo.company || "",
      address: userInfo.address || {},
    };

    // Create the profile in DynamoDB
    const profileData = {
      email: normalizedData.email,
      firstName: normalizedData.firstName,
      lastName: normalizedData.lastName,
      phone: normalizedData.phone,
      dateOfBirth: normalizedData.dateOfBirth,
      address: normalizedData.address,
      company: normalizedData.company,
    };

    console.log("Sending profile data to API:", profileData);

    const response = await APIUtils.put("/profile", profileData);

    if (response.success) {
      console.log("Profile created successfully, loading from API");
      loadProfileFromAPI(response.profile);
      showAlert("Profile initialized successfully", "success");
    } else {
      throw new Error(response.message || "Failed to create profile");
    }
  } catch (error) {
    console.error("Error creating profile:", error);
    showAlert("Could not initialize profile. Using local data.", "error");
    // Fall back to localStorage data
    loadProfileFromStorage(userInfo);
  }
}

function populateProfileForm(profile) {
  console.log("Populating form with profile:", profile);

  // Store original data for cancel functionality
  originalProfileData = { ...profile };

  // Populate form fields
  Object.keys(profile).forEach((key) => {
    const element = document.getElementById(key);
    const value =
      profile[key] !== undefined && profile[key] !== null
        ? String(profile[key])
        : "";
    console.log(`Setting ${key} = "${value}" -> element found:`, !!element);

    if (element) {
      if (element.tagName === "SELECT") {
        // For select elements, set the selected option
        element.value = value;
        console.log(
          `Select ${key} set to: ${element.value} (options: ${Array.from(
            element.options
          )
            .map((o) => o.value)
            .join(", ")})`
        );
      } else {
        element.value = value;
      }
    } else {
      console.warn(`No element found for field: ${key}`);
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

    // Remove email from form data if it exists (email should never change)
    delete formData.email;

    console.log("Form data collected (email excluded):", formData);
    console.log("Profile save initiated at:", new Date().toISOString());

    // Create user model from form data (keeping existing email)
    const currentUser = AuthUtils.getCurrentUser();
    console.log("Current user from localStorage:", currentUser);

    const updatedUser = new User({
      email: currentUser.email, // Keep existing email
      firstName: formData.firstName,
      lastName: formData.lastName,
      phone: formData.phone,
      dateOfBirth: formData.dateOfBirth,
      company: formData.company || null,
      address: Address.fromFormData(formData),
    });
    console.log("Created updated user model:", updatedUser);

    // Validate using model validation
    const validation = updatedUser.validate();
    if (!validation.isValid) {
      console.error("Validation failed:", validation.errors);
      throw new Error(validation.errors[0]);
    }

    // Send to backend API using model's API format
    const updatePayload = updatedUser.toApiFormat();

    // For profile updates, only send email for identification, not as a field to update
    const profileUpdatePayload = {
      email: currentUser.email, // For backend identification only
      firstName: updatePayload.firstName,
      lastName: updatePayload.lastName,
      phone: updatePayload.phone,
      dateOfBirth: updatePayload.dateOfBirth,
      company: updatePayload.company,
      streetAddress: updatePayload.address.streetAddress,
      city: updatePayload.address.city,
      state: updatePayload.address.state,
      zipCode: updatePayload.address.zipCode,
    };

    console.log("Sending update payload to API:", profileUpdatePayload);

    const result = await APIUtils.put("/profile", profileUpdatePayload);
    console.log("API response:", result);

    if (result.success) {
      console.log("Profile update successful, updating localStorage");
      // Update localStorage with new user model data
      AuthUtils.storeAuthData(null, updatedUser);

      // Reload the profile to show the updated data
      await loadProfile();
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
