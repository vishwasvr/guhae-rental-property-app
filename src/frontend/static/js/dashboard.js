// Dashboard-specific functionality using our modular architecture

// Dashboard utilities
const DashboardUtils = {
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
        <div class="activity-item">
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
            <span class="badge ${
              propertyModel.isActive ? "bg-success" : "bg-secondary"
            }">
              ${propertyModel.isActive ? "Active" : "Inactive"}
            </span>
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
};

// Initialize dashboard
function initDashboard() {
  // Require authentication
  if (!requireAuth()) {
    return;
  }

  // Set current user info
  const user = AuthUtils.getCurrentUser();
  if (user) {
    document.getElementById("currentUser").textContent = user.displayName;
  }

  // Load all dashboard data
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
    }
  });
}

// Export for global use
window.DashboardUtils = DashboardUtils;
window.DashboardActions = DashboardActions;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initDashboard);
