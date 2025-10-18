// Reusable UI components for the Guhae application

const Components = {
  // Create a state dropdown select element
  createStateSelect(options = {}) {
    const {
      id = "state",
      name = "state",
      required = true,
      disabled = false,
      selectedValue = "",
      placeholder = "Select State",
      className = "form-select",
    } = options;

    const select = document.createElement("select");
    select.id = id;
    select.name = name;
    select.className = className;
    select.required = required;
    select.disabled = disabled;

    // Add placeholder option
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;
    select.appendChild(placeholderOption);

    // Add state options
    US_STATES.forEach((state) => {
      const option = document.createElement("option");
      option.value = state.code;
      option.textContent = state.name;
      if (state.code === selectedValue) {
        option.selected = true;
      }
      select.appendChild(option);
    });

    return select;
  },

  // Create property type select element
  createPropertyTypeSelect(options = {}) {
    const {
      id = "propertyType",
      name = "propertyType",
      required = true,
      disabled = false,
      selectedValue = "",
      placeholder = "Select Property Type",
      className = "form-select",
    } = options;

    const select = document.createElement("select");
    select.id = id;
    select.name = name;
    select.className = className;
    select.required = required;
    select.disabled = disabled;

    // Add placeholder option
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;
    select.appendChild(placeholderOption);

    // Add property type options
    PROPERTY_TYPES.forEach((type) => {
      const option = document.createElement("option");
      option.value = type.value;
      option.textContent = type.label;
      if (type.value === selectedValue) {
        option.selected = true;
      }
      select.appendChild(option);
    });

    return select;
  },

  // Create address form group
  createAddressFormGroup(options = {}) {
    const {
      prefix = "",
      disabled = false,
      values = {},
      showLabels = true,
      required = true,
    } = options;

    const container = document.createElement("div");
    container.className = "address-form-group";

    // Street Address
    if (showLabels) {
      const streetLabel = document.createElement("label");
      streetLabel.setAttribute("for", `${prefix}streetAddress`);
      streetLabel.textContent = "Street Address:";
      if (required)
        streetLabel.innerHTML += ' <span class="text-danger">*</span>';
      container.appendChild(streetLabel);
    }

    const streetInput = document.createElement("input");
    streetInput.type = "text";
    streetInput.id = `${prefix}streetAddress`;
    streetInput.name = `${prefix}streetAddress`;
    streetInput.className = "form-control mb-3";
    streetInput.placeholder = "Enter street address";
    streetInput.required = required;
    streetInput.disabled = disabled;
    streetInput.value = values.streetAddress || "";
    container.appendChild(streetInput);

    // City and State Row
    const cityStateRow = document.createElement("div");
    cityStateRow.className = "row mb-3";

    // City
    const cityCol = document.createElement("div");
    cityCol.className = "col-md-6";

    if (showLabels) {
      const cityLabel = document.createElement("label");
      cityLabel.setAttribute("for", `${prefix}city`);
      cityLabel.textContent = "City:";
      if (required)
        cityLabel.innerHTML += ' <span class="text-danger">*</span>';
      cityCol.appendChild(cityLabel);
    }

    const cityInput = document.createElement("input");
    cityInput.type = "text";
    cityInput.id = `${prefix}city`;
    cityInput.name = `${prefix}city`;
    cityInput.className = "form-control";
    cityInput.placeholder = "Enter city";
    cityInput.required = required;
    cityInput.disabled = disabled;
    cityInput.value = values.city || "";
    cityCol.appendChild(cityInput);

    // State
    const stateCol = document.createElement("div");
    stateCol.className = "col-md-6";

    if (showLabels) {
      const stateLabel = document.createElement("label");
      stateLabel.setAttribute("for", `${prefix}state`);
      stateLabel.textContent = "State:";
      if (required)
        stateLabel.innerHTML += ' <span class="text-danger">*</span>';
      stateCol.appendChild(stateLabel);
    }

    const stateSelect = this.createStateSelect({
      id: `${prefix}state`,
      name: `${prefix}state`,
      required,
      disabled,
      selectedValue: values.state || "",
    });
    stateCol.appendChild(stateSelect);

    cityStateRow.appendChild(cityCol);
    cityStateRow.appendChild(stateCol);
    container.appendChild(cityStateRow);

    // ZIP Code
    if (showLabels) {
      const zipLabel = document.createElement("label");
      zipLabel.setAttribute("for", `${prefix}zipCode`);
      zipLabel.textContent = "ZIP Code:";
      if (required) zipLabel.innerHTML += ' <span class="text-danger">*</span>';
      container.appendChild(zipLabel);
    }

    const zipInput = document.createElement("input");
    zipInput.type = "text";
    zipInput.id = `${prefix}zipCode`;
    zipInput.name = `${prefix}zipCode`;
    zipInput.className = "form-control";
    zipInput.placeholder = "Enter ZIP code";
    zipInput.required = required;
    zipInput.disabled = disabled;
    zipInput.value = values.zipCode || "";
    zipInput.pattern = "\\d{5}(-\\d{4})?";
    zipInput.title =
      "Please enter a valid ZIP code (e.g., 12345 or 12345-6789)";
    container.appendChild(zipInput);

    return container;
  },

  // Create contact info form group
  createContactFormGroup(options = {}) {
    const {
      prefix = "",
      disabled = false,
      values = {},
      showLabels = true,
      required = true,
      includeEmail = true,
      includePhone = true,
      includeDateOfBirth = false,
    } = options;

    const container = document.createElement("div");
    container.className = "contact-form-group";

    // Email
    if (includeEmail) {
      if (showLabels) {
        const emailLabel = document.createElement("label");
        emailLabel.setAttribute("for", `${prefix}email`);
        emailLabel.textContent = "Email:";
        if (required)
          emailLabel.innerHTML += ' <span class="text-danger">*</span>';
        container.appendChild(emailLabel);
      }

      const emailInput = document.createElement("input");
      emailInput.type = "email";
      emailInput.id = `${prefix}email`;
      emailInput.name = `${prefix}email`;
      emailInput.className = "form-control mb-3";
      emailInput.placeholder = "Enter email address";
      emailInput.required = required;
      emailInput.disabled = disabled;
      emailInput.value = values.email || "";
      container.appendChild(emailInput);
    }

    // Phone
    if (includePhone) {
      if (showLabels) {
        const phoneLabel = document.createElement("label");
        phoneLabel.setAttribute("for", `${prefix}phone`);
        phoneLabel.textContent = "Phone:";
        if (required)
          phoneLabel.innerHTML += ' <span class="text-danger">*</span>';
        container.appendChild(phoneLabel);
      }

      const phoneInput = document.createElement("input");
      phoneInput.type = "tel";
      phoneInput.id = `${prefix}phone`;
      phoneInput.name = `${prefix}phone`;
      phoneInput.className = "form-control mb-3";
      phoneInput.placeholder = "Enter phone number";
      phoneInput.required = required;
      phoneInput.disabled = disabled;
      phoneInput.value = values.phone || "";
      phoneInput.pattern = "\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})";
      phoneInput.title = "Please enter a valid phone number";
      container.appendChild(phoneInput);
    }

    // Date of Birth
    if (includeDateOfBirth) {
      if (showLabels) {
        const dobLabel = document.createElement("label");
        dobLabel.setAttribute("for", `${prefix}dateOfBirth`);
        dobLabel.textContent = "Date of Birth:";
        if (required)
          dobLabel.innerHTML += ' <span class="text-danger">*</span>';
        container.appendChild(dobLabel);
      }

      const dobInput = document.createElement("input");
      dobInput.type = "date";
      dobInput.id = `${prefix}dateOfBirth`;
      dobInput.name = `${prefix}dateOfBirth`;
      dobInput.className = "form-control mb-3";
      dobInput.required = required;
      dobInput.disabled = disabled;
      dobInput.value = values.dateOfBirth || "";
      container.appendChild(dobInput);
    }

    return container;
  },

  // Replace existing state select with new one
  replaceStateSelect(selectElementOrId, options = {}) {
    let selectElement;

    if (typeof selectElementOrId === "string") {
      selectElement = document.getElementById(selectElementOrId);
    } else {
      selectElement = selectElementOrId;
    }

    if (!selectElement) {
      console.warn("State select element not found");
      return;
    }

    // Get current configuration from existing element
    const currentOptions = {
      id: selectElement.id,
      name: selectElement.name,
      required: selectElement.required,
      disabled: selectElement.disabled,
      selectedValue: selectElement.value,
      className: selectElement.className,
      ...options,
    };

    // Create new select and replace
    const newSelect = this.createStateSelect(currentOptions);
    selectElement.parentNode.replaceChild(newSelect, selectElement);

    return newSelect;
  },

  // Populate existing state select
  populateStateSelect(selectElementOrId, selectedValue = "") {
    let selectElement;

    if (typeof selectElementOrId === "string") {
      selectElement = document.getElementById(selectElementOrId);
    } else {
      selectElement = selectElementOrId;
    }

    if (!selectElement) {
      console.warn("State select element not found");
      return;
    }

    // Clear existing options
    selectElement.innerHTML = "";

    // Add placeholder
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Select State";
    selectElement.appendChild(placeholderOption);

    // Add state options
    US_STATES.forEach((state) => {
      const option = document.createElement("option");
      option.value = state.code;
      option.textContent = state.name;
      if (state.code === selectedValue) {
        option.selected = true;
      }
      selectElement.appendChild(option);
    });
  },
};

// Address validation utilities
const AddressUtils = {
  // Validate a complete address object
  validateAddress(address) {
    const errors = [];

    if (!address.streetAddress?.trim()) {
      errors.push("Street address is required");
    }

    if (!address.city?.trim()) {
      errors.push("City is required");
    }

    if (!address.state?.trim()) {
      errors.push("State is required");
    } else if (!DataUtils.isValidState(address.state)) {
      errors.push("Please select a valid state");
    }

    if (!address.zipCode?.trim()) {
      errors.push("ZIP code is required");
    } else if (!FormUtils.isValidZipCode(address.zipCode)) {
      errors.push("Please enter a valid ZIP code");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  },

  // Format address for display
  formatAddress(address, options = {}) {
    const {
      includeState = true,
      includeZip = true,
      includeCounty = false,
      separator = ", ",
      multiline = false,
    } = options;

    let parts = [];

    if (address.streetAddress) {
      parts.push(address.streetAddress);
    }

    let cityStateZip = [];
    if (address.city) {
      cityStateZip.push(address.city);
    }

    if (includeCounty && address.county) {
      cityStateZip.push(`${address.county} County`);
    }

    if (includeState && address.state) {
      cityStateZip.push(DataUtils.getStateName(address.state));
    }

    if (includeZip && address.zipCode) {
      cityStateZip.push(address.zipCode);
    }

    if (cityStateZip.length > 0) {
      parts.push(cityStateZip.join(" "));
    }

    return multiline ? parts.join("\n") : parts.join(separator);
  },

  // Extract address from form data
  extractAddressFromForm(formData, prefix = "") {
    return {
      streetAddress: formData[`${prefix}streetAddress`] || "",
      city: formData[`${prefix}city`] || "",
      county: formData[`${prefix}county`] || "",
      state: formData[`${prefix}state`] || "",
      zipCode: formData[`${prefix}zipCode`] || "",
    };
  },
};

// Export components for global use
window.Components = Components;
window.AddressUtils = AddressUtils;
