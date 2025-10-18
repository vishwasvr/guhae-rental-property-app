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

  // All users can access all resources
  canAccess(resourceType, action = "read") {
    return true; // All users are owners with full access
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

// Address model
class Address {
  constructor(data = {}) {
    this.streetAddress = data.street || data.streetAddress || "";
    this.city = data.city || "";
    this.state = data.state || "";
    this.zipCode = data.zipCode || data.zip || "";
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
      street: this.streetAddress,
      city: this.city,
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
      state: formData[`${prefix}state`] || "",
      zipCode: formData[`${prefix}zipCode`] || "",
    });
  }
}

// Property model
class Property {
  constructor(data = {}) {
    this.id = data.id || null;
    this.title = data.title || "";
    this.description = data.description || "";
    // Handle both API format (property_type) and frontend format (propertyType)
    this.propertyType = data.propertyType || data.property_type || "";
    this.address = new Address(data.address || {});
    this.bedrooms = data.bedrooms || 0;
    this.bathrooms = data.bathrooms || 0;
    this.squareFootage = data.squareFootage || null;
    // Handle both API format (price) and frontend format (rent)
    this.rent = data.rent || data.price || 0;
    this.deposit = data.deposit || 0;
    this.availableDate = data.availableDate || "";
    this.leaseTerm = data.leaseTerm || "";
    this.amenities = data.amenities || [];
    this.images = data.images || [];
    this.landlordId = data.landlordId || null;
    // Handle both API format (status === 'active') and frontend format (isActive)
    this.isActive =
      data.isActive !== undefined ? data.isActive : data.status === "active";
    // Handle both API format (created_at) and frontend format (createdAt)
    this.createdAt = data.createdAt || data.created_at || null;
    this.updatedAt = data.updatedAt || data.updated_at || null;
  }

  get formattedRent() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.rent);
  }

  get formattedDeposit() {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(this.deposit);
  }

  get propertyTypeLabel() {
    return DataUtils.getPropertyTypeLabel(this.propertyType);
  }

  get leaseTermLabel() {
    return DataUtils.formatLeaseTerm(this.leaseTerm);
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

  // Convert to API format
  toApiFormat() {
    return {
      title: this.title,
      description: this.description,
      propertyType: this.propertyType,
      address: this.address.toApiFormat(),
      bedrooms: this.bedrooms,
      bathrooms: this.bathrooms,
      squareFootage: this.squareFootage,
      rent: this.rent,
      deposit: this.deposit,
      availableDate: this.availableDate,
      leaseTerm: this.leaseTerm,
      amenities: this.amenities,
      images: this.images,
      isActive: this.isActive,
    };
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

// Export models for global use
window.User = User;
window.Address = Address;
window.Property = Property;
window.Tenant = Tenant;
window.Application = Application;
