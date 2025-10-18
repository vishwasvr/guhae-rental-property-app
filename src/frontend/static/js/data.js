// Data module for reusable data structures used across the application

// US States data
const US_STATES = [
  { code: "AL", name: "Alabama" },
  { code: "AK", name: "Alaska" },
  { code: "AZ", name: "Arizona" },
  { code: "AR", name: "Arkansas" },
  { code: "CA", name: "California" },
  { code: "CO", name: "Colorado" },
  { code: "CT", name: "Connecticut" },
  { code: "DE", name: "Delaware" },
  { code: "FL", name: "Florida" },
  { code: "GA", name: "Georgia" },
  { code: "HI", name: "Hawaii" },
  { code: "ID", name: "Idaho" },
  { code: "IL", name: "Illinois" },
  { code: "IN", name: "Indiana" },
  { code: "IA", name: "Iowa" },
  { code: "KS", name: "Kansas" },
  { code: "KY", name: "Kentucky" },
  { code: "LA", name: "Louisiana" },
  { code: "ME", name: "Maine" },
  { code: "MD", name: "Maryland" },
  { code: "MA", name: "Massachusetts" },
  { code: "MI", name: "Michigan" },
  { code: "MN", name: "Minnesota" },
  { code: "MS", name: "Mississippi" },
  { code: "MO", name: "Missouri" },
  { code: "MT", name: "Montana" },
  { code: "NE", name: "Nebraska" },
  { code: "NV", name: "Nevada" },
  { code: "NH", name: "New Hampshire" },
  { code: "NJ", name: "New Jersey" },
  { code: "NM", name: "New Mexico" },
  { code: "NY", name: "New York" },
  { code: "NC", name: "North Carolina" },
  { code: "ND", name: "North Dakota" },
  { code: "OH", name: "Ohio" },
  { code: "OK", name: "Oklahoma" },
  { code: "OR", name: "Oregon" },
  { code: "PA", name: "Pennsylvania" },
  { code: "RI", name: "Rhode Island" },
  { code: "SC", name: "South Carolina" },
  { code: "SD", name: "South Dakota" },
  { code: "TN", name: "Tennessee" },
  { code: "TX", name: "Texas" },
  { code: "UT", name: "Utah" },
  { code: "VT", name: "Vermont" },
  { code: "VA", name: "Virginia" },
  { code: "WA", name: "Washington" },
  { code: "WV", name: "West Virginia" },
  { code: "WI", name: "Wisconsin" },
  { code: "WY", name: "Wyoming" },
  { code: "DC", name: "District of Columbia" },
];

// Property types for rental listings
const PROPERTY_TYPES = [
  {
    value: "apartment",
    label: "Apartment",
    description: "Multi-unit building",
  },
  {
    value: "house",
    label: "Single Family House",
    description: "Detached home",
  },
  { value: "condo", label: "Condominium", description: "Owner-occupied unit" },
  {
    value: "townhouse",
    label: "Townhouse",
    description: "Multi-level attached home",
  },
  { value: "studio", label: "Studio", description: "Single room living space" },
  { value: "loft", label: "Loft", description: "Open-plan living space" },
  { value: "duplex", label: "Duplex", description: "Two-unit property" },
  {
    value: "room",
    label: "Room Rental",
    description: "Single room in shared space",
  },
];

// Property amenities
const PROPERTY_AMENITIES = [
  // Basic Amenities
  { category: "basic", value: "air_conditioning", label: "Air Conditioning" },
  { category: "basic", value: "heating", label: "Heating" },
  { category: "basic", value: "furnished", label: "Furnished" },
  { category: "basic", value: "unfurnished", label: "Unfurnished" },

  // Kitchen & Appliances
  { category: "appliances", value: "dishwasher", label: "Dishwasher" },
  { category: "appliances", value: "microwave", label: "Microwave" },
  { category: "appliances", value: "refrigerator", label: "Refrigerator" },
  { category: "appliances", value: "washer_dryer", label: "Washer/Dryer" },
  { category: "appliances", value: "washer_dryer_hookup", label: "W/D Hookup" },

  // Building Features
  { category: "building", value: "elevator", label: "Elevator" },
  { category: "building", value: "doorman", label: "Doorman" },
  { category: "building", value: "gym", label: "Fitness Center" },
  { category: "building", value: "pool", label: "Swimming Pool" },
  { category: "building", value: "parking", label: "Parking" },
  { category: "building", value: "garage", label: "Garage" },

  // Pet Policy
  { category: "pets", value: "pets_allowed", label: "Pets Allowed" },
  { category: "pets", value: "cats_allowed", label: "Cats Allowed" },
  { category: "pets", value: "dogs_allowed", label: "Dogs Allowed" },
  { category: "pets", value: "no_pets", label: "No Pets" },
];

// Lease terms
const LEASE_TERMS = [
  { value: "month_to_month", label: "Month-to-Month", months: 0 },
  { value: "3_months", label: "3 Months", months: 3 },
  { value: "6_months", label: "6 Months", months: 6 },
  { value: "12_months", label: "12 Months", months: 12 },
  { value: "18_months", label: "18 Months", months: 18 },
  { value: "24_months", label: "24 Months", months: 24 },
];

// Data utility functions
const DataUtils = {
  // Get state name by code
  getStateName(stateCode) {
    const state = US_STATES.find((s) => s.code === stateCode);
    return state ? state.name : stateCode;
  },

  // Get state code by name
  getStateCode(stateName) {
    const state = US_STATES.find((s) => s.name === stateName);
    return state ? state.code : stateName;
  },

  // Get property type label
  getPropertyTypeLabel(propertyType) {
    const type = PROPERTY_TYPES.find((t) => t.value === propertyType);
    return type ? type.label : propertyType;
  },

  // Get amenities by category
  getAmenitiesByCategory(category) {
    return PROPERTY_AMENITIES.filter(
      (amenity) => amenity.category === category
    );
  },

  // Format lease term
  formatLeaseTerm(termValue) {
    const term = LEASE_TERMS.find((t) => t.value === termValue);
    return term ? term.label : termValue;
  },

  // Validate state code
  isValidState(stateCode) {
    return US_STATES.some((s) => s.code === stateCode);
  },

  // Search states by name or code
  searchStates(query) {
    const searchTerm = query.toLowerCase();
    return US_STATES.filter(
      (state) =>
        state.name.toLowerCase().includes(searchTerm) ||
        state.code.toLowerCase().includes(searchTerm)
    );
  },
};

// Export data for global use
window.US_STATES = US_STATES;
window.PROPERTY_TYPES = PROPERTY_TYPES;
window.PROPERTY_AMENITIES = PROPERTY_AMENITIES;
window.LEASE_TERMS = LEASE_TERMS;
window.DataUtils = DataUtils;
