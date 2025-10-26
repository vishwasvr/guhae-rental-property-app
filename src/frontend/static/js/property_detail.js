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

    const savePropertyBtn = document.getElementById("savePropertyBtn");
    if (savePropertyBtn) {
      savePropertyBtn.addEventListener("click", () =>
        this.savePropertyChanges()
      );
    }

    // Finance buttons
    const editPurchaseBtn = document.getElementById("editPurchaseBtn");
    if (editPurchaseBtn) {
      editPurchaseBtn.addEventListener("click", () => this.editPurchaseInfo());
    }

    const addLoanBtn = document.getElementById("addLoanBtn");
    if (addLoanBtn) {
      addLoanBtn.addEventListener("click", () => this.addLoan());
    }

    const savePurchaseBtn = document.getElementById("savePurchaseBtn");
    if (savePurchaseBtn) {
      savePurchaseBtn.addEventListener("click", () => this.savePurchaseInfo());
    }

    const saveLoanBtn = document.getElementById("saveLoanBtn");
    if (saveLoanBtn) {
      saveLoanBtn.addEventListener("click", () => this.saveLoan());
    }
  }

  async loadPropertyData() {
    try {
      console.log(`Loading property data for ID: ${this.propertyId}`);

      // Show loading state
      this.showLoadingState();

      // Use PropertyService to get property data
      this.currentProperty = await PropertyService.getPropertyById(
        this.propertyId
      );

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

    // Update title - just show the property name/title
    const title = this.currentProperty.title || "Property Details";
    document.getElementById("propertyTitle").textContent = title;

    // Update address
    const fullAddress = this.currentProperty.getFullAddress();
    document.getElementById(
      "propertyAddress"
    ).innerHTML = `<i class="fas fa-map-marker-alt me-2"></i>${fullAddress}`;

    // Update property type
    const typeElement = document.getElementById("propertyType");
    const propertyType = this.currentProperty.propertyType || "Unknown Type";
    typeElement.textContent = StringUtils.capitalize(propertyType);
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
      const propertyName = this.currentProperty.title || "Property Details";
      breadcrumb.textContent = propertyName;
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
        value:
          StringUtils.capitalize(this.currentProperty.propertyType) ||
          "Not specified",
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
        label: "County",
        value: this.currentProperty.address?.county
          ? StringUtils.capitalize(
              `${this.currentProperty.address.county} County`
            )
          : "Not specified",
      },
      {
        label: "Garage",
        value:
          this.currentProperty.garageType && this.currentProperty.garageCars
            ? `${StringUtils.capitalize(this.currentProperty.garageType)} (${
                this.currentProperty.garageCars
              } cars)`
            : this.currentProperty.garageType
            ? StringUtils.capitalize(this.currentProperty.garageType)
            : "None",
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
        // Initialize finance tab - ensure content is visible
        this.initializeFinanceTab();
        await this.loadFinanceData();
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
    if (!this.currentProperty) {
      alert("No property data available to edit.");
      return;
    }

    console.log("Opening edit modal for property:", this.currentProperty);

    // Populate the form with current property data
    this.populateEditForm();

    // Show the modal
    const modal = new bootstrap.Modal(
      document.getElementById("editPropertyModal")
    );
    modal.show();
  }

  populateEditForm() {
    if (!this.currentProperty) return;

    console.log("Populating edit form with property:", this.currentProperty);
    console.log("Address data:", this.currentProperty.address);

    // Basic property information
    document.getElementById("editTitle").value =
      this.currentProperty.title || "";
    document.getElementById("editPropertyType").value =
      this.currentProperty.propertyType || "";
    document.getElementById("editDescription").value =
      this.currentProperty.description || "";

    // Financial information
    document.getElementById("editRent").value = this.currentProperty.rent || "";

    // Property specifications
    document.getElementById("editBedrooms").value =
      this.currentProperty.bedrooms || "";
    document.getElementById("editBathrooms").value =
      this.currentProperty.bathrooms || "";
    document.getElementById("editSquareFeet").value =
      this.currentProperty.squareFeet || "";

    // Address information - always structured now
    const address = this.currentProperty.address || {};
    const addressNote = document.getElementById("addressNote");

    console.log("Current property address structure:", address);
    console.log("Address type:", typeof address);
    console.log("Address keys:", Object.keys(address));

    // Always populate address fields from structured address object
    const streetValue = address.streetAddress || address.street || "";
    const cityValue = address.city || "";
    const countyValue = address.county || "";
    const zipValue = address.zipCode || address.zip || "";

    console.log("Setting address fields:", {
      street: streetValue,
      city: cityValue,
      county: countyValue,
      zip: zipValue,
    });

    document.getElementById("editStreetAddress").value = streetValue;
    document.getElementById("editCity").value = cityValue;
    document.getElementById("editCounty").value = countyValue;
    document.getElementById("editZipCode").value = zipValue;

    // Debug: Check if values were actually set
    console.log("After setting - actual field values:", {
      street: document.getElementById("editStreetAddress").value,
      city: document.getElementById("editCity").value,
      county: document.getElementById("editCounty").value,
      zip: document.getElementById("editZipCode").value,
    });

    // Hide address note since fields are populated
    if (addressNote) {
      addressNote.style.display = "none";
    } // Populate state dropdown and set selected value
    if (typeof Components !== "undefined" && Components.populateStateSelect) {
      Components.populateStateSelect("editState");
      document.getElementById("editState").value = address.state || "";
    }

    // Garage information
    document.getElementById("editGarageType").value =
      this.currentProperty.garageType || "";
    document.getElementById("editGarageCars").value =
      this.currentProperty.garageCars || "";
  }

  async savePropertyChanges() {
    try {
      console.log("Saving property changes...");

      // Get form data
      const formData = {
        id: this.currentProperty.id,
        title: document.getElementById("editTitle").value.trim(),
        propertyType: document.getElementById("editPropertyType").value,
        description: document.getElementById("editDescription").value.trim(),
        rent: parseFloat(document.getElementById("editRent").value) || 0,
        bedrooms: parseInt(document.getElementById("editBedrooms").value) || 0,
        bathrooms:
          parseFloat(document.getElementById("editBathrooms").value) || 0,
        squareFeet:
          parseInt(document.getElementById("editSquareFeet").value) || null,

        // Address information
        streetAddress: document
          .getElementById("editStreetAddress")
          .value.trim(),
        city: document.getElementById("editCity").value.trim(),
        county: document.getElementById("editCounty").value.trim(),
        state: document.getElementById("editState").value,
        zipCode: document.getElementById("editZipCode").value.trim(),

        // Garage information
        garageType: document.getElementById("editGarageType").value,
        garageCars:
          parseInt(document.getElementById("editGarageCars").value) || 0,
      };

      console.log("Form data collected:", formData);

      // Show loading state
      const saveBtn = document.getElementById("savePropertyBtn");
      const originalText = saveBtn.innerHTML;
      saveBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
      saveBtn.disabled = true;

      // Update property via PropertyService
      this.currentProperty = await PropertyService.updateProperty(
        this.currentProperty.id,
        formData
      );

      console.log("Property updated successfully:", this.currentProperty);

      // Update UI
      this.updatePropertyHeader();
      this.updateOverviewTab();

      // Close modal
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("editPropertyModal")
      );
      modal.hide();

      // Show success message
      this.showTemporaryMessage("Property updated successfully!", "success");
    } catch (error) {
      console.error("Failed to save property changes:", error);
      this.showTemporaryMessage(
        `Failed to update property: ${error.message}`,
        "error"
      );
    } finally {
      // Restore button state
      const saveBtn = document.getElementById("savePropertyBtn");
      saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Changes';
      saveBtn.disabled = false;
    }
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

  // Finance Management Methods

  initializeFinanceTab() {
    console.log("Initializing finance tab...");

    // Ensure loading state is initially hidden and content is visible
    const loadingState = document.getElementById("financeLoadingState");
    if (loadingState) {
      loadingState.style.display = "none";
    }

    // Ensure all finance cards are visible
    const financeContent = document.querySelectorAll("#tab-finances .card");
    financeContent.forEach((card) => {
      card.style.display = "block";
    });
  }

  async loadFinanceData() {
    try {
      console.log("Loading finance data...");

      // Show loading state
      this.showFinanceLoadingState(true);

      // Load finance data
      this.currentFinance = await FinanceService.getPropertyFinance(
        this.propertyId
      );

      // Update UI
      this.updateFinanceOverview();
      this.updatePurchaseInfoSection();
      this.updateLoansSection();

      console.log("Finance data loaded:", this.currentFinance);
    } catch (error) {
      console.error("Failed to load finance data:", error);
      this.showTemporaryMessage(
        `Failed to load finance data: ${error.message}`,
        "error"
      );
    } finally {
      this.showFinanceLoadingState(false);
    }
  }

  showFinanceLoadingState(show) {
    const loadingState = document.getElementById("financeLoadingState");
    const financeContent = document.querySelectorAll("#tab-finances .card");

    console.log(`Setting finance loading state: ${show}`);

    if (loadingState) {
      loadingState.style.display = show ? "block" : "none";
    }

    financeContent.forEach((card) => {
      card.style.display = show ? "none" : "block";
    });

    // Ensure buttons are visible when not loading
    if (!show) {
      const editPurchaseBtn = document.getElementById("editPurchaseBtn");
      const addLoanBtn = document.getElementById("addLoanBtn");

      console.log("Looking for finance buttons:", {
        editPurchaseBtn: !!editPurchaseBtn,
        addLoanBtn: !!addLoanBtn,
      });

      if (editPurchaseBtn) {
        editPurchaseBtn.style.display = "inline-block";
        console.log("Made editPurchaseBtn visible");
      }
      if (addLoanBtn) {
        addLoanBtn.style.display = "inline-block";
        console.log("Made addLoanBtn visible");
      }
    }
  }

  updateFinanceOverview() {
    // Update ownership type
    const ownershipTypeEl = document.getElementById("ownershipType");
    if (ownershipTypeEl) {
      ownershipTypeEl.textContent = this.currentFinance.ownershipTypeLabel;
    }

    // Update ownership status
    const ownershipStatusEl = document.getElementById("ownershipStatus");
    if (ownershipStatusEl) {
      ownershipStatusEl.textContent = this.currentFinance.ownershipStatusLabel;
    }

    // Update total loan balance
    const totalLoanBalanceEl = document.getElementById("totalLoanBalance");
    if (totalLoanBalanceEl) {
      if (this.currentFinance.totalLoanBalance > 0) {
        totalLoanBalanceEl.textContent = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
        }).format(this.currentFinance.totalLoanBalance);
      } else {
        totalLoanBalanceEl.textContent = "No Active Loans";
      }
    }
  }

  updatePurchaseInfoSection() {
    const purchase = this.currentFinance.purchaseInfo;

    // Update purchase information fields
    document.getElementById("purchasePrice").textContent =
      purchase.purchasePrice ? purchase.formattedPurchasePrice : "-";
    document.getElementById("purchaseDate").textContent =
      purchase.purchaseDate || "-";
    document.getElementById("builder").textContent = purchase.builder || "-";
    document.getElementById("seller").textContent = purchase.seller || "-";
    document.getElementById("buyerAgent").textContent =
      purchase.buyerAgent || "-";
    document.getElementById("sellerAgent").textContent =
      purchase.sellerAgent || "-";
    document.getElementById("titleCompany").textContent =
      purchase.titleCompany || "-";
    document.getElementById("closingCosts").textContent = purchase.closingCosts
      ? purchase.formattedClosingCosts
      : "-";
  }

  updateLoansSection() {
    const container = document.getElementById("loansContainer");
    if (!container) return;

    if (this.currentFinance.loans.length === 0) {
      container.innerHTML = `
        <div class="text-center text-muted py-4">
          <i class="fas fa-university fa-2x mb-3"></i>
          <p>No loans added yet</p>
        </div>
      `;
      return;
    }

    const loansHtml = this.currentFinance.loans
      .map(
        (loan) => `
      <div class="card mb-3" data-loan-id="${loan.id}">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col">
              <h6 class="mb-1">${loan.lender}</h6>
              <div class="d-flex gap-2 mb-2">
                <span class="badge bg-info">${loan.loanTypeLabel}</span>
                <span class="badge ${
                  loan.isActive ? "bg-success" : "bg-secondary"
                }">${loan.statusLabel}</span>
              </div>
              <small class="text-muted">
                ${loan.formattedCurrentBalance} balance • ${
          loan.formattedInterestRate
        } • ${loan.termYears} years
              </small>
            </div>
            <div class="col-auto">
              <div class="text-end">
                <div class="fw-bold text-primary">${
                  loan.formattedMonthlyPayment
                }</div>
                <small class="text-muted">monthly</small>
              </div>
            </div>
            <div class="col-auto">
              <div class="btn-group">
                <button class="btn btn-outline-primary btn-sm" onclick="propertyDetailManager.editLoan('${
                  loan.id
                }')">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="propertyDetailManager.deleteLoan('${
                  loan.id
                }')">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `
      )
      .join("");

    container.innerHTML = loansHtml;
  }

  editPurchaseInfo() {
    if (!this.currentFinance) {
      this.showTemporaryMessage("Finance data not loaded", "error");
      return;
    }

    // Populate modal with current data
    document.getElementById("editOwnershipType").value =
      this.currentFinance.ownershipType;
    document.getElementById("editOwnershipStatus").value =
      this.currentFinance.ownershipStatus;

    const purchase = this.currentFinance.purchaseInfo;
    document.getElementById("editPurchasePrice").value =
      purchase.purchasePrice || "";
    document.getElementById("editPurchaseDate").value =
      purchase.purchaseDate || "";
    document.getElementById("editDownPayment").value =
      purchase.downPayment || "";
    document.getElementById("editClosingCosts").value =
      purchase.closingCosts || "";
    document.getElementById("editBuilder").value = purchase.builder || "";
    document.getElementById("editSeller").value = purchase.seller || "";
    document.getElementById("editBuyerAgent").value = purchase.buyerAgent || "";
    document.getElementById("editSellerAgent").value =
      purchase.sellerAgent || "";
    document.getElementById("editTitleCompany").value =
      purchase.titleCompany || "";

    // Show modal
    const modal = new bootstrap.Modal(
      document.getElementById("editPurchaseModal")
    );
    modal.show();
  }

  async savePurchaseInfo() {
    try {
      // Collect form data
      const formData = {
        ownershipType: document.getElementById("editOwnershipType").value,
        ownershipStatus: document.getElementById("editOwnershipStatus").value,
        purchaseInfo: {
          purchasePrice:
            parseFloat(document.getElementById("editPurchasePrice").value) || 0,
          purchaseDate: document.getElementById("editPurchaseDate").value,
          downPayment:
            parseFloat(document.getElementById("editDownPayment").value) || 0,
          closingCosts:
            parseFloat(document.getElementById("editClosingCosts").value) || 0,
          builder: document.getElementById("editBuilder").value,
          seller: document.getElementById("editSeller").value,
          buyerAgent: document.getElementById("editBuyerAgent").value,
          sellerAgent: document.getElementById("editSellerAgent").value,
          titleCompany: document.getElementById("editTitleCompany").value,
        },
        loans: this.currentFinance.loans.map((loan) => loan.toApiFormat()),
      };

      // Show loading state
      const saveBtn = document.getElementById("savePurchaseBtn");
      const originalText = saveBtn.innerHTML;
      saveBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
      saveBtn.disabled = true;

      // Update finance data
      this.currentFinance = await FinanceService.updatePropertyFinance(
        this.propertyId,
        formData
      );

      // Update UI
      this.updateFinanceOverview();
      this.updatePurchaseInfoSection();

      // Close modal
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("editPurchaseModal")
      );
      modal.hide();

      this.showTemporaryMessage(
        "Purchase information updated successfully!",
        "success"
      );
    } catch (error) {
      console.error("Failed to save purchase info:", error);
      this.showTemporaryMessage(
        `Failed to update purchase info: ${error.message}`,
        "error"
      );
    } finally {
      // Restore button state
      const saveBtn = document.getElementById("savePurchaseBtn");
      saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Changes';
      saveBtn.disabled = false;
    }
  }

  addLoan() {
    this.currentLoanId = null;

    // Reset form
    document.getElementById("editLoanForm").reset();
    document.getElementById("editLoanId").value = "";
    document.getElementById("editIsActive").checked = true;

    // Update modal title
    document.getElementById("loanModalTitle").textContent = "Add Loan";

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById("editLoanModal"));
    modal.show();
  }

  editLoan(loanId) {
    const loan = this.currentFinance.loans.find((l) => l.id === loanId);
    if (!loan) {
      this.showTemporaryMessage("Loan not found", "error");
      return;
    }

    this.currentLoanId = loanId;

    // Populate modal with loan data
    document.getElementById("editLoanId").value = loan.id;
    document.getElementById("editLender").value = loan.lender;
    document.getElementById("editLoanType").value = loan.loanType;
    document.getElementById("editOriginalAmount").value = loan.originalAmount;
    document.getElementById("editCurrentBalance").value = loan.currentBalance;
    document.getElementById("editInterestRate").value = loan.interestRate;
    document.getElementById("editTermYears").value = loan.termYears;
    document.getElementById("editMonthlyPayment").value = loan.monthlyPayment;
    document.getElementById("editStartDate").value = loan.startDate;
    document.getElementById("editMaturityDate").value = loan.maturityDate;
    document.getElementById("editIsActive").checked = loan.isActive;

    // Update modal title
    document.getElementById("loanModalTitle").textContent = "Edit Loan";

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById("editLoanModal"));
    modal.show();
  }

  async saveLoan() {
    try {
      // Collect form data
      const loanData = {
        lender: document.getElementById("editLender").value,
        loanType: document.getElementById("editLoanType").value,
        originalAmount:
          parseFloat(document.getElementById("editOriginalAmount").value) || 0,
        currentBalance:
          parseFloat(document.getElementById("editCurrentBalance").value) || 0,
        interestRate:
          parseFloat(document.getElementById("editInterestRate").value) || 0,
        termYears:
          parseInt(document.getElementById("editTermYears").value) || 30,
        monthlyPayment:
          parseFloat(document.getElementById("editMonthlyPayment").value) || 0,
        startDate: document.getElementById("editStartDate").value,
        maturityDate: document.getElementById("editMaturityDate").value,
        isActive: document.getElementById("editIsActive").checked,
      };

      // Show loading state
      const saveBtn = document.getElementById("saveLoanBtn");
      const originalText = saveBtn.innerHTML;
      saveBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
      saveBtn.disabled = true;

      if (this.currentLoanId) {
        // Update existing loan
        await FinanceService.updatePropertyLoan(
          this.propertyId,
          this.currentLoanId,
          loanData
        );
        this.showTemporaryMessage("Loan updated successfully!", "success");
      } else {
        // Add new loan
        await FinanceService.addPropertyLoan(this.propertyId, loanData);
        this.showTemporaryMessage("Loan added successfully!", "success");
      }

      // Reload finance data
      await this.loadFinanceData();

      // Close modal
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("editLoanModal")
      );
      modal.hide();
    } catch (error) {
      console.error("Failed to save loan:", error);
      this.showTemporaryMessage(
        `Failed to save loan: ${error.message}`,
        "error"
      );
    } finally {
      // Restore button state
      const saveBtn = document.getElementById("saveLoanBtn");
      saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Loan';
      saveBtn.disabled = false;
    }
  }

  async deleteLoan(loanId) {
    if (
      !confirm(
        "Are you sure you want to delete this loan? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      await FinanceService.deletePropertyLoan(this.propertyId, loanId);
      this.showTemporaryMessage("Loan deleted successfully!", "success");

      // Reload finance data
      await this.loadFinanceData();
    } catch (error) {
      console.error("Failed to delete loan:", error);
      this.showTemporaryMessage(
        `Failed to delete loan: ${error.message}`,
        "error"
      );
    }
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
