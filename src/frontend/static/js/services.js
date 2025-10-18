// Data services for the Guhae application
// Centralized API communication and data transformation

/**
 * Property Service - handles all property-related API operations
 */
class PropertyService {
  /**
   * Get all properties for the authenticated user
   */
  static async getAllProperties() {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      const response = await APIUtils.makeRequest("/properties", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.properties || !Array.isArray(response.properties)) {
        throw new Error("Invalid API response format");
      }

      // Convert API response to Property instances
      return response.properties.map((propertyData) =>
        Property.fromApiResponse(propertyData)
      );
    } catch (error) {
      console.error("Failed to fetch properties:", error);
      throw new Error(`Failed to load properties: ${error.message}`);
    }
  }

  /**
   * Get a single property by ID
   */
  static async getPropertyById(propertyId) {
    try {
      const properties = await this.getAllProperties();
      const property = properties.find((p) => p.id === propertyId);

      if (!property) {
        throw new Error("Property not found");
      }

      return property;
    } catch (error) {
      console.error("Failed to fetch property:", error);
      throw new Error(`Failed to load property: ${error.message}`);
    }
  }

  /**
   * Create a new property
   */
  static async createProperty(propertyData) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Validate property data using Property class
      const property = new Property(propertyData);
      const validation = property.validate();
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(", ")}`);
      }

      // Transform to API format
      const apiData = this._transformToApiFormat(propertyData);
      console.log("Sending property data to API:", apiData);

      const response = await APIUtils.makeRequest("/properties", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(apiData),
      });

      if (!response.property) {
        throw new Error("Invalid API response format");
      }

      return Property.fromApiResponse(response.property);
    } catch (error) {
      console.error("Failed to create property:", error);
      throw new Error(`Failed to create property: ${error.message}`);
    }
  }

  /**
   * Update an existing property
   */
  static async updateProperty(propertyId, propertyData) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Validate property data using Property class
      const property = new Property(propertyData);
      const validation = property.validate();
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(", ")}`);
      }

      // Transform to API format
      const apiData = this._transformToApiFormat(propertyData);
      apiData.id = propertyId; // Ensure ID is included

      console.log("Updating property with data:", apiData);

      const response = await APIUtils.makeRequest(`/properties/${propertyId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(apiData),
      });

      if (!response.property) {
        throw new Error("Invalid API response format");
      }

      return Property.fromApiResponse(response.property);
    } catch (error) {
      console.error("Failed to update property:", error);
      throw new Error(`Failed to update property: ${error.message}`);
    }
  }

  /**
   * Delete a property
   */
  static async deleteProperty(propertyId) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      await APIUtils.makeRequest(`/properties/${propertyId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      return true;
    } catch (error) {
      console.error("Failed to delete property:", error);
      throw new Error(`Failed to delete property: ${error.message}`);
    }
  }

  /**
   * Transform frontend data to API format
   * Handles field mapping and data normalization
   */
  static _transformToApiFormat(data) {
    const transformed = {
      title: data.title?.trim() || "",
      description: data.description?.trim() || "",
      propertyType: data.propertyType || data.property_type || "",
      rent: parseFloat(data.rent || data.price || 0),
      bedrooms: parseInt(data.bedrooms || 0),
      bathrooms: parseFloat(data.bathrooms || 0),
      squareFeet: data.squareFeet ? parseInt(data.squareFeet) : null,
      garageType: data.garageType || "",
      garageCars: parseInt(data.garageCars || 0),
    };

    // Handle address data
    if (data.address && typeof data.address === "object") {
      // Address is already structured
      transformed.streetAddress = data.address.streetAddress || "";
      transformed.city = data.address.city || "";
      transformed.county = data.address.county || "";
      transformed.state = data.address.state || "";
      transformed.zipCode = data.address.zipCode || "";
      transformed.country = data.address.country || "US";
    } else {
      // Address fields are at root level (from forms)
      transformed.streetAddress = data.streetAddress || "";
      transformed.city = data.city || "";
      transformed.county = data.county || "";
      transformed.state = data.state || "";
      transformed.zipCode = data.zipCode || "";
      transformed.country = data.country || "US";
    }

    return transformed;
  }

  /**
   * Transform form data to standardized format
   */
  static transformFormData(formData) {
    return {
      title: formData.get("title")?.trim() || "",
      propertyType:
        formData.get("property_type") || formData.get("propertyType") || "",
      description: formData.get("description")?.trim() || "",
      rent: parseFloat(formData.get("price") || formData.get("rent") || 0),
      bedrooms: parseInt(formData.get("bedrooms") || 0),
      bathrooms: parseFloat(formData.get("bathrooms") || 0),
      squareFeet: formData.get("squareFeet")
        ? parseInt(formData.get("squareFeet"))
        : null,
      garageType: formData.get("garageType") || "",
      garageCars: parseInt(formData.get("garageCars") || 0),
      address: {
        streetAddress: formData.get("streetAddress")?.trim() || "",
        city: formData.get("city")?.trim() || "",
        county: formData.get("county")?.trim() || "",
        state: formData.get("state") || "",
        zipCode: formData.get("zipCode")?.trim() || "",
        country: formData.get("country") || "US",
      },
    };
  }
}

/**
 * Finance Service - handles property finance operations
 */
class FinanceService {
  /**
   * Get finance data for a property
   */
  static async getPropertyFinance(propertyId) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      const response = await APIUtils.makeRequest(
        `/properties/${propertyId}/finance`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.finance) {
        // Return empty finance data if none exists
        return new PropertyFinance({ propertyId });
      }

      return PropertyFinance.fromApiResponse(response.finance);
    } catch (error) {
      console.error("Failed to fetch property finance:", error);
      // Return empty finance data on error
      return new PropertyFinance({ propertyId });
    }
  }

  /**
   * Update finance data for a property
   */
  static async updatePropertyFinance(propertyId, financeData) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Validate finance data
      const finance = new PropertyFinance(financeData);
      const validation = finance.validate();
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(", ")}`);
      }

      // Transform to API format
      const apiData = finance.toApiFormat();
      apiData.propertyId = propertyId;

      console.log("Updating property finance with data:", apiData);

      const response = await APIUtils.makeRequest(
        `/properties/${propertyId}/finance`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(apiData),
        }
      );

      if (!response.finance) {
        throw new Error("Invalid API response format");
      }

      return PropertyFinance.fromApiResponse(response.finance);
    } catch (error) {
      console.error("Failed to update property finance:", error);
      throw new Error(`Failed to update finance data: ${error.message}`);
    }
  }

  /**
   * Add a loan to a property
   */
  static async addPropertyLoan(propertyId, loanData) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Validate loan data
      const loan = new PropertyLoan(loanData);
      const validation = loan.validate();
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(", ")}`);
      }

      // Transform to API format
      const apiData = loan.toApiFormat();
      apiData.propertyId = propertyId;

      const response = await APIUtils.makeRequest(
        `/properties/${propertyId}/loans`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(apiData),
        }
      );

      if (!response.loan) {
        throw new Error("Invalid API response format");
      }

      return PropertyLoan.fromApiResponse(response.loan);
    } catch (error) {
      console.error("Failed to add property loan:", error);
      throw new Error(`Failed to add loan: ${error.message}`);
    }
  }

  /**
   * Update a property loan
   */
  static async updatePropertyLoan(propertyId, loanId, loanData) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Validate loan data
      const loan = new PropertyLoan(loanData);
      const validation = loan.validate();
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(", ")}`);
      }

      // Transform to API format
      const apiData = loan.toApiFormat();
      apiData.id = loanId;
      apiData.propertyId = propertyId;

      const response = await APIUtils.makeRequest(
        `/properties/${propertyId}/loans/${loanId}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(apiData),
        }
      );

      if (!response.loan) {
        throw new Error("Invalid API response format");
      }

      return PropertyLoan.fromApiResponse(response.loan);
    } catch (error) {
      console.error("Failed to update property loan:", error);
      throw new Error(`Failed to update loan: ${error.message}`);
    }
  }

  /**
   * Delete a property loan
   */
  static async deletePropertyLoan(propertyId, loanId) {
    try {
      const token = AuthUtils.getToken();
      if (!token) {
        throw new Error("Authentication token not found");
      }

      await APIUtils.makeRequest(`/properties/${propertyId}/loans/${loanId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      return true;
    } catch (error) {
      console.error("Failed to delete property loan:", error);
      throw new Error(`Failed to delete loan: ${error.message}`);
    }
  }
}

// Export globally
window.PropertyService = PropertyService;
window.FinanceService = FinanceService;
