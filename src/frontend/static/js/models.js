// Data models for the Guhae application

// User model
class User {
  constructor(data = {}) {
    this.id = data.id || null;
    this.email = data.email || "";
    // Handle both our format and Cognito format for names
    this.firstName =
      data.firstName || data.given_name || data.name?.split(" ")[0] || "";
    this.lastName =
      data.lastName || data.family_name || data.name?.split(" ")[1] || "";
    this.phone = data.phone || "";
    this.dateOfBirth = data.dateOfBirth || "";
    this.company = data.company || "";
    this.address = new Address(data.address || {});
    this.createdAt = data.createdAt || null;
    this.updatedAt = data.updatedAt || null;
  }

  get fullName() {
    return `${this.firstName} ${this.lastName}`.trim() || this.email;
  }

  get displayName() {
    return this.fullName || "User";
  }

  // Validate user data
  validate() {
    const errors = [];

    if (!this.email?.trim()) {
      errors.push("Email is required");
    } else if (!FormUtils.isValidEmail(this.email)) {
      errors.push("Please enter a valid email address");
    }

    if (!this.firstName?.trim()) {
      errors.push("First name is required");
    }

    if (!this.lastName?.trim()) {
      errors.push("Last name is required");
    }

    if (!this.phone?.trim()) {
      errors.push("Phone number is required");
    } else if (!FormUtils.isValidPhone(this.phone)) {
      errors.push("Please enter a valid phone number");
    }

    // Validate address
    const addressValidation = this.address.validate();
    if (!addressValidation.isValid) {
      errors.push(...addressValidation.errors);
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // All users are property owners with full permissions
  hasPermission(permission) {
    return true; // All users are owners with full permissions
  }

  // All users have owner-level permissions
  getPermissionLevel() {
    return 80; // Owner permission level
  }

  // All users can access all resources
  canAccess(resourceType, action = "read") {
    return true; // All users are owners with full access
  }

  // Convert to API format
  toApiFormat() {
    return {
      email: this.email,
      firstName: this.firstName,
      lastName: this.lastName,
      phone: this.phone,
      dateOfBirth: this.dateOfBirth,
      company: this.company,
      address: this.address.toApiFormat(),
    };
  }

  // Create from API response
  static fromApiResponse(data) {
    return new User({
      id: data.id,
      email: data.email,
      firstName: data.firstName,
      lastName: data.lastName,
      phone: data.phone,
      dateOfBirth: data.dateOfBirth,
      company: data.company,
      address: data.address,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
    });
  }
}

// Address model - simplified for consistent API format
class Address {
  constructor(data = {}) {
    this.streetAddress = data.streetAddress || "";
    this.city = data.city || "";
    this.county = data.county || "";
    this.state = data.state || "";
    this.zipCode = data.zipCode || "";
    this.country = data.country || "US";
  }

  // Validate address
  validate() {
    return AddressUtils.validateAddress(this);
  }

  // Format for display
  format(options = {}) {
    return AddressUtils.formatAddress(this, options);
  }

  // Check if address is complete
  isComplete() {
    return !!(this.streetAddress && this.city && this.state && this.zipCode);
  }

  // Convert to API format
  toApiFormat() {
    return {
      streetAddress: this.streetAddress,
      city: this.city,
      county: this.county,
      state: this.state,
      zipCode: this.zipCode,
      country: this.country,
    };
  }

  // Create from form data
  static fromFormData(formData, prefix = "") {
    return new Address({
      streetAddress: formData[`${prefix}streetAddress`] || "",
      city: formData[`${prefix}city`] || "",
      county: formData[`${prefix}county`] || "",
      state: formData[`${prefix}state`] || "",
      zipCode: formData[`${prefix}zipCode`] || "",
    });
  }
}

// Property model - simplified for consistent API format
class Property {
  constructor(data = {}) {
    this.id = data.id || null;
    this.title = data.title || "";
    this.description = data.description || "";
    this.propertyType = data.propertyType || "";
    this.address = new Address(data.address || {});
    this.rent = data.rent || 0;
    this.bedrooms = data.bedrooms || 0;
    this.bathrooms = data.bathrooms || 0;
    this.squareFeet = data.squareFeet || null;
    this.garageType = data.garageType || "";
    this.garageCars = data.garageCars || 0;
    this.status = data.status || "active";
    this.createdAt = data.createdAt || null;
    this.updatedAt = data.updatedAt || null;
    this.images = data.images || [];
  }

  get formattedRent() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.rent);
  }

  get propertyTypeLabel() {
    return StringUtils.capitalize(this.propertyType);
  }

  get isActive() {
    return this.status === "active";
  }

  // Validate property data
  validate() {
    const errors = [];

    if (!this.title?.trim()) {
      errors.push("Property title is required");
    }

    if (!this.propertyType) {
      errors.push("Property type is required");
    }

    if (!this.rent || this.rent <= 0) {
      errors.push("Rent amount is required and must be greater than 0");
    }

    if (!this.bedrooms || this.bedrooms < 0) {
      errors.push("Number of bedrooms is required");
    }

    if (!this.bathrooms || this.bathrooms < 0) {
      errors.push("Number of bathrooms is required");
    }

    // Validate address
    const addressValidation = this.address.validate();
    if (!addressValidation.isValid) {
      errors.push(...addressValidation.errors);
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Get display address
  getDisplayAddress() {
    return this.address.streetAddress || this.title || "Address not available";
  }

  // Get full formatted address
  getFullAddress() {
    const parts = [
      this.address.streetAddress,
      this.address.city,
      this.address.state,
      this.address.zipCode,
    ].filter((part) => part && part.trim());
    return parts.join(", ") || this.getDisplayAddress();
  }

  // Convert to API format
  toApiFormat() {
    return {
      id: this.id,
      title: this.title,
      description: this.description,
      propertyType: this.propertyType,
      address: this.address.toApiFormat(),
      rent: this.rent,
      bedrooms: this.bedrooms,
      bathrooms: this.bathrooms,
      squareFeet: this.squareFeet,
      garageType: this.garageType,
      garageCars: this.garageCars,
      status: this.status,
      images: this.images,
    };
  }

  // Create from API response
  static fromApiResponse(data) {
    return new Property(data);
  }
}

// Tenant model (for non-user tenants)
class Tenant {
  constructor(data = {}) {
    this.id = data.id || null;
    this.firstName = data.firstName || "";
    this.lastName = data.lastName || "";
    this.email = data.email || "";
    this.phone = data.phone || "";
    this.dateOfBirth = data.dateOfBirth || "";
    this.emergencyContact = data.emergencyContact || {};
    this.currentAddress = new Address(data.currentAddress || {});
    this.employmentInfo = data.employmentInfo || {};
    this.references = data.references || [];
    this.propertyId = data.propertyId || null;
    this.leaseStart = data.leaseStart || "";
    this.leaseEnd = data.leaseEnd || "";
    this.monthlyRent = data.monthlyRent || 0;
    this.depositPaid = data.depositPaid || 0;
    this.isActive = data.isActive !== undefined ? data.isActive : true;
  }

  get fullName() {
    return `${this.firstName} ${this.lastName}`.trim() || this.email;
  }

  // Validate tenant data
  validate() {
    const errors = [];

    if (!this.firstName?.trim()) {
      errors.push("First name is required");
    }

    if (!this.lastName?.trim()) {
      errors.push("Last name is required");
    }

    if (!this.email?.trim()) {
      errors.push("Email is required");
    } else if (!FormUtils.isValidEmail(this.email)) {
      errors.push("Please enter a valid email address");
    }

    if (!this.phone?.trim()) {
      errors.push("Phone number is required");
    } else if (!FormUtils.isValidPhone(this.phone)) {
      errors.push("Please enter a valid phone number");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}

// Application model (rental application)
class Application {
  constructor(data = {}) {
    this.id = data.id || null;
    this.propertyId = data.propertyId || null;
    this.applicant = new Tenant(data.applicant || {});
    this.coapplicants = (data.coapplicants || []).map((co) => new Tenant(co));
    this.desiredMoveInDate = data.desiredMoveInDate || "";
    this.desiredLeaseTerm = data.desiredLeaseTerm || "";
    this.pets = data.pets || [];
    this.vehicleInfo = data.vehicleInfo || [];
    this.status = data.status || "pending";
    this.submittedAt = data.submittedAt || null;
    this.reviewedAt = data.reviewedAt || null;
    this.reviewNotes = data.reviewNotes || "";
  }

  get statusLabel() {
    const statusLabels = {
      pending: "Pending Review",
      approved: "Approved",
      rejected: "Rejected",
      withdrawn: "Withdrawn",
    };
    return statusLabels[this.status] || this.status;
  }

  // Validate application
  validate() {
    const errors = [];

    if (!this.propertyId) {
      errors.push("Property is required");
    }

    if (!this.desiredMoveInDate) {
      errors.push("Desired move-in date is required");
    }

    // Validate main applicant
    const applicantValidation = this.applicant.validate();
    if (!applicantValidation.isValid) {
      errors.push(
        ...applicantValidation.errors.map((err) => `Main applicant: ${err}`)
      );
    }

    // Validate co-applicants
    this.coapplicants.forEach((coapplicant, index) => {
      const coValidation = coapplicant.validate();
      if (!coValidation.isValid) {
        errors.push(
          ...coValidation.errors.map(
            (err) => `Co-applicant ${index + 1}: ${err}`
          )
        );
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}

// Property Finance model
class PropertyFinance {
  constructor(data = {}) {
    this.propertyId = data.propertyId || null;
    this.ownershipType = data.ownershipType || null; // individual, joint, llc, corporation, partnership
    this.ownershipStatus = data.ownershipStatus || null; // owned, financed, leased
    this.purchaseInfo = new PurchaseInfo(data.purchaseInfo || {});
    this.loans = (data.loans || []).map((loan) => new PropertyLoan(loan));
    this.createdAt = data.createdAt || null;
    this.updatedAt = data.updatedAt || null;
  }

  get ownershipTypeLabel() {
    if (!this.ownershipType) return "Not available";

    const types = {
      individual: "Individual",
      joint: "Joint Ownership",
      llc: "LLC",
      corporation: "Corporation",
      partnership: "Partnership",
      trust: "Trust",
    };
    return (
      types[this.ownershipType] || StringUtils.capitalize(this.ownershipType)
    );
  }

  get ownershipStatusLabel() {
    if (!this.ownershipStatus) return "Not available";

    const statuses = {
      owned: "Owned Outright",
      financed: "Financed",
      leased: "Leased",
      contract: "Contract for Deed",
    };
    return (
      statuses[this.ownershipStatus] ||
      StringUtils.capitalize(this.ownershipStatus)
    );
  }

  get activeLoans() {
    return this.loans.filter((loan) => loan.isActive);
  }

  get totalLoanBalance() {
    return this.activeLoans.reduce(
      (total, loan) => total + loan.currentBalance,
      0
    );
  }

  validate() {
    const errors = [];

    if (!this.ownershipType) {
      errors.push("Ownership type is required");
    }

    if (!this.ownershipStatus) {
      errors.push("Ownership status is required");
    }

    // Validate purchase info
    const purchaseValidation = this.purchaseInfo.validate();
    if (!purchaseValidation.isValid) {
      errors.push(...purchaseValidation.errors);
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  toApiFormat() {
    return {
      propertyId: this.propertyId,
      ownershipType: this.ownershipType,
      ownershipStatus: this.ownershipStatus,
      purchaseInfo: this.purchaseInfo.toApiFormat(),
      loans: this.loans.map((loan) => loan.toApiFormat()),
    };
  }

  static fromApiResponse(data) {
    return new PropertyFinance(data);
  }
}

// Purchase Information model
class PurchaseInfo {
  constructor(data = {}) {
    this.purchasePrice = data.purchasePrice || 0;
    this.purchaseDate = data.purchaseDate || "";
    this.builder = data.builder || "";
    this.seller = data.seller || "";
    this.buyerAgent = data.buyerAgent || "";
    this.sellerAgent = data.sellerAgent || "";
    this.titleCompany = data.titleCompany || "";
    this.closingCosts = data.closingCosts || 0;
    this.downPayment = data.downPayment || 0;
  }

  get formattedPurchasePrice() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.purchasePrice);
  }

  get formattedClosingCosts() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.closingCosts);
  }

  get formattedDownPayment() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.downPayment);
  }

  validate() {
    const errors = [];

    if (this.purchasePrice && this.purchasePrice <= 0) {
      errors.push("Purchase price must be greater than 0");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  toApiFormat() {
    return {
      purchasePrice: this.purchasePrice,
      purchaseDate: this.purchaseDate,
      builder: this.builder,
      seller: this.seller,
      buyerAgent: this.buyerAgent,
      sellerAgent: this.sellerAgent,
      titleCompany: this.titleCompany,
      closingCosts: this.closingCosts,
      downPayment: this.downPayment,
    };
  }
}

// Property Loan model
class PropertyLoan {
  constructor(data = {}) {
    this.id = data.id || null;
    this.propertyId = data.propertyId || null;
    this.lender = data.lender || "";
    this.loanType = data.loanType || ""; // conventional, fha, va, usda, portfolio, hard-money
    this.originalAmount = data.originalAmount || 0;
    this.currentBalance = data.currentBalance || 0;
    this.interestRate = data.interestRate || 0;
    this.termYears = data.termYears || 30;
    this.monthlyPayment = data.monthlyPayment || 0;
    this.startDate = data.startDate || "";
    this.maturityDate = data.maturityDate || "";
    this.isActive = data.isActive !== undefined ? data.isActive : true;
    this.createdAt = data.createdAt || null;
    this.updatedAt = data.updatedAt || null;
  }

  get loanTypeLabel() {
    const types = {
      conventional: "Conventional",
      fha: "FHA",
      va: "VA",
      usda: "USDA",
      portfolio: "Portfolio",
      "hard-money": "Hard Money",
      heloc: "HELOC",
      other: "Other",
    };
    return types[this.loanType] || StringUtils.capitalize(this.loanType);
  }

  get formattedOriginalAmount() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.originalAmount);
  }

  get formattedCurrentBalance() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.currentBalance);
  }

  get formattedMonthlyPayment() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.monthlyPayment);
  }

  get formattedInterestRate() {
    return `${this.interestRate.toFixed(2)}%`;
  }

  get statusLabel() {
    return this.isActive ? "Active" : "Closed";
  }

  validate() {
    const errors = [];

    if (!this.lender?.trim()) {
      errors.push("Lender name is required");
    }

    if (!this.loanType) {
      errors.push("Loan type is required");
    }

    if (!this.originalAmount || this.originalAmount <= 0) {
      errors.push("Original loan amount must be greater than 0");
    }

    if (this.currentBalance < 0) {
      errors.push("Current balance cannot be negative");
    }

    if (!this.interestRate || this.interestRate <= 0) {
      errors.push("Interest rate must be greater than 0");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  toApiFormat() {
    return {
      id: this.id,
      propertyId: this.propertyId,
      lender: this.lender,
      loanType: this.loanType,
      originalAmount: this.originalAmount,
      currentBalance: this.currentBalance,
      interestRate: this.interestRate,
      termYears: this.termYears,
      monthlyPayment: this.monthlyPayment,
      startDate: this.startDate,
      maturityDate: this.maturityDate,
      isActive: this.isActive,
    };
  }

  static fromApiResponse(data) {
    return new PropertyLoan(data);
  }
}

// Export models for global use
window.User = User;
window.Address = Address;
window.Property = Property;
window.Tenant = Tenant;
window.Application = Application;
window.PropertyFinance = PropertyFinance;
window.PurchaseInfo = PurchaseInfo;
window.PropertyLoan = PropertyLoan;
