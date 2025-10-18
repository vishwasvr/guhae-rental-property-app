// Dashboard-specific functionality using our modular architecture

// Dashboard utilities
const DashboardUtils = {
  // Initialize dashboard for property owner
  async initializeDashboard() {
    const currentUser = AuthUtils.getCurrentUser();
    console.log(
      "initializeDashboard - currentUser from localStorage:",
      currentUser
    );

    if (currentUser) {
      // Check if user data is missing profile info (from old login)
      if (!currentUser.firstName && !currentUser.lastName) {
        console.log(
          "User data missing profile info, fetching fresh profile..."
        );
        await this.refreshUserProfile(currentUser);
      } else {
        this.updateUserDisplay(currentUser);
      }
    } else {
      console.log("No current user found");
    }
  },

  // Refresh user profile data if missing
  async refreshUserProfile(currentUser) {
    try {
      // Pass user email as query parameter for authentication
      const profileData = await APIUtils.get(
        `/profile?email=${encodeURIComponent(currentUser.email)}`
      );
      if (profileData.success && profileData.profile) {
        // Merge the fresh profile data with existing user data
        const updatedUser = {
          ...currentUser,
          firstName: profileData.profile.firstName || "",
          lastName: profileData.profile.lastName || "",
          phone: profileData.profile.phone || "",
          company: profileData.profile.company || "",
        };

        // Update localStorage with complete user data
        AuthUtils.updateUserInfo(updatedUser);

        // Update display with fresh data
        this.updateUserDisplay(updatedUser);
      } else {
        console.log(
          "Profile not found or fetch failed, using email for display"
        );
        // If profile fetch fails or profile doesn't exist, still update display with what we have
        // The User model will automatically use email as fallback for displayName
        this.updateUserDisplay(currentUser);
      }
    } catch (error) {
      console.log("Could not fetch fresh profile data:", error);
      // Use email as display name when profile is not available
      this.updateUserDisplay(currentUser);
    }
  },

  // Setup dashboard for property owners

  // Update user display in dashboard
  updateUserDisplay(user) {
    if (!user) {
      console.log("updateUserDisplay: No user data provided");
      return;
    }

    console.log("updateUserDisplay called with user:", user);

    // Create a User model instance to use consistent display logic
    const userModel = new User(user);
    const displayName = userModel.displayName;

    console.log("Computed displayName:", displayName);

    // Update main dropdown button
    const currentUserElement = document.getElementById("currentUser");
    if (currentUserElement) {
      currentUserElement.textContent = displayName;
    }

    // Update dropdown header
    const dropdownNameElement = document.getElementById("dropdown-user-name");
    if (dropdownNameElement) {
      dropdownNameElement.textContent = displayName;
    }
  },

  // Load and display dashboard statistics
  async loadDashboardData() {
    try {
      const data = await APIUtils.get("/dashboard");

      // Update statistics using our UIUtils
      this.updateStatElement("totalProperties", data.total_properties || 0);
      this.updateStatElement("totalUsers", data.total_users || 1);
      this.updateStatElement("totalLeases", data.total_leases || 0);

      // Update timestamp
      document.getElementById("lastUpdated").textContent =
        new Date().toLocaleTimeString();
    } catch (error) {
      console.error("Error loading dashboard data:", error);
      UIUtils.showMessage(
        "errorAlert",
        "Failed to load dashboard data",
        "danger"
      );
    }
  },

  // Load and display properties list
  async loadProperties() {
    try {
      const data = await APIUtils.get("/properties");
      const container = document.getElementById("propertiesList");

      // Store properties data globally for property detail modal
      if (!window.dashboardData) {
        window.dashboardData = {};
      }
      window.dashboardData.properties = data.properties || [];

      if (data.properties && data.properties.length > 0) {
        container.innerHTML = this.renderPropertiesList(data.properties);
      } else {
        container.innerHTML = this.renderEmptyPropertiesState();
      }
    } catch (error) {
      console.error("Error loading properties:", error);
      UIUtils.showMessage("errorAlert", "Failed to load properties", "danger");
    }
  },

  // Check API health status
  async checkApiHealth() {
    const statusElement = document.getElementById("apiStatus");

    try {
      const data = await APIUtils.get("/health");

      if (data.status === "healthy") {
        statusElement.innerHTML = '<i class="fas fa-circle"></i> Online';
        statusElement.className = "text-success";
      } else {
        statusElement.innerHTML =
          '<i class="fas fa-exclamation-triangle"></i> Issues';
        statusElement.className = "text-warning";
      }
    } catch (error) {
      statusElement.innerHTML = '<i class="fas fa-times-circle"></i> Offline';
      statusElement.className = "text-danger";
    }
  },

  // Update statistic element with animation
  updateStatElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
      // Add counting animation
      const currentValue = parseInt(element.textContent) || 0;
      this.animateCount(element, currentValue, value, 1000);
    }
  },

  // Animate counting numbers
  animateCount(element, start, end, duration) {
    const increment = (end - start) / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if (
        (increment > 0 && current >= end) ||
        (increment < 0 && current <= end)
      ) {
        element.textContent = end;
        clearInterval(timer);
      } else {
        element.textContent = Math.floor(current);
      }
    }, 16);
  },

  // Render properties list HTML
  renderPropertiesList(properties) {
    return properties
      .map((property) => {
        const propertyModel = new Property(property);
        return `
        <div class="activity-item property-card" data-property-id="${
          property.id
        }" style="cursor: pointer;">
          <div class="d-flex align-items-center">
            <div class="flex-grow-1">
              <p class="mb-1">${propertyModel.title || "Untitled Property"}</p>
              <small class="text-muted">${propertyModel.address.format()}</small>
              <div class="mt-1">
                <span class="badge bg-info">${
                  propertyModel.propertyTypeLabel
                }</span>
                <span class="text-muted ms-2">${
                  propertyModel.formattedRent
                }/month</span>
              </div>
            </div>
            <div class="d-flex align-items-center">
              <span class="badge ${
                propertyModel.isActive ? "bg-success" : "bg-secondary"
              } me-2">
                ${propertyModel.isActive ? "Active" : "Inactive"}
              </span>
              <i class="fas fa-chevron-right text-muted"></i>
            </div>
          </div>
        </div>
      `;
      })
      .join("");
  },

  // Render empty state for properties
  renderEmptyPropertiesState() {
    return `
      <div class="text-center text-muted py-4">
        <i class="fas fa-home fa-2x mb-3"></i>
        <p>No properties yet</p>
        <button class="btn btn-outline-primary btn-sm" onclick="DashboardActions.addProperty()">
          Add Your First Property
        </button>
      </div>
    `;
  },

  // Set up auto-refresh
  setupAutoRefresh(intervalMs = 30000) {
    setInterval(() => {
      this.loadDashboardData();
      this.checkApiHealth();
    }, intervalMs);
  },
};

// Dashboard actions
const DashboardActions = {
  // Navigate to add property page
  addProperty() {
    window.location.href = "add_property.html";
  },

  // Logout user
  logout() {
    if (confirm("Are you sure you want to logout?")) {
      AuthUtils.logout();
    }
  },

  // Navigate to profile
  goToProfile() {
    window.location.href = "profile.html";
  },

  // Refresh dashboard data
  refresh() {
    const refreshBtn = document.getElementById("refreshBtn");
    UIUtils.showLoading(refreshBtn, "Refreshing...");

    Promise.all([
      DashboardUtils.loadDashboardData(),
      DashboardUtils.loadProperties(),
      DashboardUtils.checkApiHealth(),
    ]).finally(() => {
      UIUtils.hideLoading(refreshBtn);
    });
  },

  // Show property details in modal
  async showPropertyDetail(propertyId) {
    try {
      // Find the property in the current data
      const properties = window.dashboardData?.properties || [];
      const property = properties.find((p) => p.id === propertyId);

      if (!property) {
        console.error("Property not found:", propertyId);
        return;
      }

      // Store current property ID for editing
      this.currentPropertyId = propertyId;

      // Create property model for consistent formatting
      const propertyModel = new Property(property);

      // Populate modal content
      const modalContent = document.getElementById("propertyDetailContent");
      modalContent.innerHTML = this.renderPropertyDetailContent(propertyModel);

      // Update modal title
      document.getElementById("propertyDetailModalLabel").textContent =
        propertyModel.title || "Property Details";

      // Show the modal
      const modal = new bootstrap.Modal(
        document.getElementById("propertyDetailModal")
      );
      modal.show();
    } catch (error) {
      console.error("Error showing property details:", error);
      alert("Failed to load property details. Please try again.");
    }
  },

  // Render property detail content for modal
  renderPropertyDetailContent(propertyModel) {
    return `
      <div class="row">
        <div class="col-md-8">
          <h6 class="text-muted mb-3">Property Information</h6>
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Title:</strong></div>
            <div class="col-sm-8">${propertyModel.title || "N/A"}</div>
          </div>
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Type:</strong></div>
            <div class="col-sm-8">
              <span class="badge bg-info">${
                propertyModel.propertyTypeLabel
              }</span>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Address:</strong></div>
            <div class="col-sm-8">${propertyModel.address.format()}</div>
          </div>
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Monthly Rent:</strong></div>
            <div class="col-sm-8"><strong class="text-success">${
              propertyModel.formattedRent
            }</strong></div>
          </div>
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Status:</strong></div>
            <div class="col-sm-8">
              <span class="badge ${
                propertyModel.isActive ? "bg-success" : "bg-secondary"
              }">
                ${propertyModel.isActive ? "Active" : "Inactive"}
              </span>
            </div>
          </div>
          ${
            propertyModel.bedrooms !== undefined
              ? `
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Bedrooms:</strong></div>
            <div class="col-sm-8">${propertyModel.bedrooms} bedroom${
                  propertyModel.bedrooms !== 1 ? "s" : ""
                }</div>
          </div>
          `
              : ""
          }
          ${
            propertyModel.bathrooms !== undefined
              ? `
          <div class="row mb-3">
            <div class="col-sm-4"><strong>Bathrooms:</strong></div>
            <div class="col-sm-8">${propertyModel.bathrooms} bathroom${
                  propertyModel.bathrooms !== 1 ? "s" : ""
                }</div>
          </div>
          `
              : ""
          }
        </div>
        <div class="col-md-4">
          <h6 class="text-muted mb-3">Property Details</h6>
          <div class="mb-3">
            <small class="text-muted">Created:</small><br>
            <span>${new Date(
              propertyModel.createdAt
            ).toLocaleDateString()}</span>
          </div>
          <div class="mb-3">
            <small class="text-muted">Property ID:</small><br>
            <small class="font-monospace text-muted">${propertyModel.id}</small>
          </div>
        </div>
      </div>
      ${
        propertyModel.description
          ? `
      <div class="mt-4">
        <h6 class="text-muted mb-2">Description</h6>
        <p class="text-muted">${propertyModel.description}</p>
      </div>
      `
          : ""
      }
    `;
  },

  // Store current property for editing
  currentPropertyId: null,

  // Navigate to property details page
  goToPropertyDetails() {
    if (this.currentPropertyId) {
      // Navigate to dedicated property detail page
      window.location.href = `property_detail.html?id=${this.currentPropertyId}`;
    } else {
      alert("No property selected.");
    }
  },
};

// Initialize dashboard
function initDashboard() {
  // Require authentication
  if (!requireAuth()) {
    return;
  }

  // Initialize dashboard
  DashboardUtils.initializeDashboard();

  // Load dashboard data for property owner
  DashboardUtils.loadDashboardData();
  DashboardUtils.loadProperties();
  DashboardUtils.checkApiHealth();

  // Setup auto-refresh
  DashboardUtils.setupAutoRefresh();

  // Add event listeners
  document.addEventListener("click", (e) => {
    if (e.target.matches('[data-action="logout"]')) {
      DashboardActions.logout();
    } else if (e.target.matches('[data-action="refresh"]')) {
      DashboardActions.refresh();
    } else if (e.target.matches('[data-action="add-property"]')) {
      DashboardActions.addProperty();
    } else if (e.target.matches("#detailsPropertyBtn")) {
      // Handle details property button click
      DashboardActions.goToPropertyDetails();
    } else if (e.target.closest(".property-card")) {
      // Handle property card clicks
      const propertyCard = e.target.closest(".property-card");
      const propertyId = propertyCard.getAttribute("data-property-id");
      DashboardActions.showPropertyDetail(propertyId);
    }
  });
}

// Export for global use
window.DashboardUtils = DashboardUtils;
window.DashboardActions = DashboardActions;

// Global functions for HTML onclick handlers
window.logout = function () {
  DashboardActions.logout();
};

window.addProperty = function () {
  DashboardActions.addProperty();
};

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initDashboard);
