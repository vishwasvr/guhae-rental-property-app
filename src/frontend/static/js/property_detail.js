/**
 * Property Detail Page - Main JavaScript
 * Handles property data loading, tab navigation, and page interactions
 */

class PropertyDetailManager {
  constructor() {
    this.currentProperty = null;
    this.currentTab = "overview";
    this.propertyId = null;

    this.init();
  }

  async init() {
    try {
      // Extract property ID from URL parameters
      this.propertyId = this.getPropertyIdFromURL();

      if (!this.propertyId) {
        this.showError("Property ID not found in URL");
        return;
      }

      // Setup event listeners
      this.setupEventListeners();

      // Load property data
      await this.loadPropertyData();

      console.log("Property detail manager initialized successfully");
    } catch (error) {
      console.error("Failed to initialize property detail manager:", error);
      this.showError("Failed to load property details");
    }
  }

  getPropertyIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("id");
  }

  setupEventListeners() {
    // Tab navigation
    document.querySelectorAll(".nav-link[data-tab]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = e.currentTarget.getAttribute("data-tab");
        this.switchTab(tab);
      });
    });

    // Action buttons
    const editPropertyBtn = document.getElementById("editPropertyBtn");
    if (editPropertyBtn) {
      editPropertyBtn.addEventListener("click", () => this.editProperty());
    }

    const addTenantBtn = document.getElementById("addTenantBtn");
    if (addTenantBtn) {
      addTenantBtn.addEventListener("click", () => this.addTenant());
    }

    const refreshDataBtn = document.getElementById("refreshDataBtn");
    if (refreshDataBtn) {
      refreshDataBtn.addEventListener("click", () => this.refreshData());
    }
  }

  async loadPropertyData() {
    try {
      console.log(`Loading property data for ID: ${this.propertyId}`);

      // Show loading state
      this.showLoadingState();

      // Get auth token
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Fetch property data
      const response = await APIUtils.makeRequest("/properties", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.success || !response.data) {
        throw new Error(response.message || "Failed to load properties");
      }

      // Find the specific property
      const property = response.data.find(
        (p) => p.property_id === this.propertyId
      );
      if (!property) {
        throw new Error("Property not found");
      }

      // Create Property instance with proper formatting
      this.currentProperty = new Property(property);

      // Update UI
      this.updatePropertyHeader();
      this.updateOverviewTab();
      this.updateBreadcrumb();

      console.log("Property data loaded successfully:", this.currentProperty);
    } catch (error) {
      console.error("Failed to load property data:", error);
      this.showError(`Failed to load property: ${error.message}`);
    }
  }

  showLoadingState() {
    // Update header with loading text
    document.getElementById("propertyTitle").textContent = "Loading...";
    document.getElementById("propertyAddress").innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Loading address...';
    document.getElementById("propertyType").textContent = "Loading...";
    document.getElementById("propertyStatus").textContent = "Loading...";
    document.getElementById("propertyRent").textContent = "Loading...";
  }

  updatePropertyHeader() {
    if (!this.currentProperty) return;

    // Update title
    const title =
      this.currentProperty.getDisplayAddress() || "Property Details";
    document.getElementById("propertyTitle").textContent = title;

    // Update address
    const fullAddress = this.currentProperty.getFullAddress();
    document.getElementById(
      "propertyAddress"
    ).innerHTML = `<i class="fas fa-map-marker-alt me-2"></i>${fullAddress}`;

    // Update property type
    const typeElement = document.getElementById("propertyType");
    typeElement.textContent =
      this.currentProperty.propertyType || "Unknown Type";
    typeElement.className = `badge bg-info`;

    // Update status (placeholder - you can add status logic later)
    const statusElement = document.getElementById("propertyStatus");
    statusElement.textContent = "Active";
    statusElement.className = `badge bg-success`;

    // Update rent
    const rentElement = document.getElementById("propertyRent");
    const rent = this.currentProperty.rent;
    if (rent && rent > 0) {
      rentElement.textContent = `$${rent.toLocaleString()}`;
    } else {
      rentElement.textContent = "Rent Not Set";
    }
  }

  updateBreadcrumb() {
    const breadcrumb = document.getElementById("propertyBreadcrumb");
    if (this.currentProperty) {
      const address =
        this.currentProperty.getDisplayAddress() || "Property Details";
      breadcrumb.textContent = address;
    }
  }

  updateOverviewTab() {
    if (!this.currentProperty) return;

    // Update stats (placeholder data - replace with real data when available)
    document.getElementById("tenantCount").textContent = "0";
    document.getElementById("monthlyIncome").textContent = this.currentProperty
      .rent
      ? `$${this.currentProperty.rent.toLocaleString()}`
      : "$0";
    document.getElementById("maintenanceRequests").textContent = "0";
    document.getElementById("occupancyRate").textContent = "0%";

    // Update property details
    this.updatePropertyDetailsSection();
  }

  updatePropertyDetailsSection() {
    const detailsContainer = document.getElementById("propertyDetails");

    const details = [
      {
        label: "Property Type",
        value: this.currentProperty.propertyType || "Not specified",
      },
      {
        label: "Monthly Rent",
        value: this.currentProperty.rent
          ? `$${this.currentProperty.rent.toLocaleString()}`
          : "Not set",
      },
      {
        label: "Bedrooms",
        value: this.currentProperty.bedrooms || "Not specified",
      },
      {
        label: "Bathrooms",
        value: this.currentProperty.bathrooms || "Not specified",
      },
      {
        label: "Square Feet",
        value: this.currentProperty.squareFeet
          ? `${this.currentProperty.squareFeet} sq ft`
          : "Not specified",
      },
      {
        label: "Date Added",
        value: this.currentProperty.createdAt
          ? new Date(this.currentProperty.createdAt).toLocaleDateString()
          : "Unknown",
      },
    ];

    const detailsHtml = details
      .map(
        (detail) => `
            <div class="d-flex justify-content-between py-2 border-bottom">
                <span class="text-muted">${detail.label}:</span>
                <span class="fw-semibold">${detail.value}</span>
            </div>
        `
      )
      .join("");

    detailsContainer.innerHTML = detailsHtml;
  }

  switchTab(tabName) {
    if (this.currentTab === tabName) return;

    // Update navigation
    document.querySelectorAll(".nav-link[data-tab]").forEach((link) => {
      if (link.getAttribute("data-tab") === tabName) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    // Hide all tab content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.style.display = "none";
    });

    // Show selected tab
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
      selectedTab.style.display = "block";
    }

    this.currentTab = tabName;

    // Load tab-specific data
    this.loadTabData(tabName);

    console.log(`Switched to tab: ${tabName}`);
  }

  async loadTabData(tabName) {
    // Placeholder for loading tab-specific data
    // This will be implemented as features are added
    console.log(`Loading data for tab: ${tabName}`);

    switch (tabName) {
      case "overview":
        // Overview data is already loaded
        break;
      case "tenants":
        // TODO: Load tenant data
        break;
      case "finances":
        // TODO: Load financial data
        break;
      case "income":
        // TODO: Load income data
        break;
      case "expenses":
        // TODO: Load expense data
        break;
      case "maintenance":
        // TODO: Load maintenance data
        break;
    }
  }

  editProperty() {
    // TODO: Implement property editing
    console.log("Edit property clicked");
    alert("Property editing feature coming soon!");
  }

  addTenant() {
    // TODO: Implement add tenant functionality
    console.log("Add tenant clicked");
    alert("Add tenant feature coming soon!");
  }

  async refreshData() {
    console.log("Refreshing property data...");

    // Show loading state on refresh button
    const refreshBtn = document.getElementById("refreshDataBtn");
    const originalHtml = refreshBtn.innerHTML;
    refreshBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...';
    refreshBtn.disabled = true;

    try {
      await this.loadPropertyData();

      // Show success message
      this.showTemporaryMessage("Data refreshed successfully!", "success");
    } catch (error) {
      console.error("Failed to refresh data:", error);
      this.showTemporaryMessage("Failed to refresh data", "error");
    } finally {
      // Restore button state
      refreshBtn.innerHTML = originalHtml;
      refreshBtn.disabled = false;
    }
  }

  showError(message) {
    console.error("Property detail error:", message);

    // Update main content with error message
    const contentArea = document.querySelector(".content-area");
    if (contentArea) {
      contentArea.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h4>Error Loading Property</h4>
                    <p class="text-muted mb-3">${message}</p>
                    <button class="btn btn-primary" onclick="window.location.href='dashboard.html'">
                        <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                    </button>
                </div>
            `;
    }
  }

  showTemporaryMessage(message, type = "info") {
    // Create temporary alert
    const alert = document.createElement("div");
    alert.className = `alert alert-${
      type === "error" ? "danger" : type
    } alert-dismissible fade show position-fixed`;
    alert.style.top = "20px";
    alert.style.right = "20px";
    alert.style.zIndex = "9999";
    alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

    document.body.appendChild(alert);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      if (alert.parentNode) {
        alert.remove();
      }
    }, 3000);
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Check authentication first
  if (!AuthUtils.getToken()) {
    console.warn("No authentication token found, redirecting to login");
    window.location.href = "index.html";
    return;
  }

  // Initialize property detail manager
  window.propertyDetailManager = new PropertyDetailManager();
});

// Handle back navigation
window.addEventListener("beforeunload", () => {
  console.log("Leaving property detail page");
});

// Export for testing/debugging
if (typeof module !== "undefined" && module.exports) {
  module.exports = PropertyDetailManager;
}
