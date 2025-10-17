// Role-Based Access Control (RBAC) System for Guhae Rental Property App

// Define user roles and their hierarchical relationships
const USER_ROLES = {
  // System Administrator - Full access
  ADMIN: {
    name: "admin",
    label: "System Administrator",
    level: 100,
    description: "Full system access and management",
  },

  // Property Owner - Owns properties
  OWNER: {
    name: "owner",
    label: "Property Owner",
    level: 80,
    description: "Property owner with management rights",
  },

  // Property Manager - Manages properties on behalf of owners
  PROPERTY_MANAGER: {
    name: "property_manager",
    label: "Property Manager",
    level: 70,
    description: "Manages properties and tenant relationships",
  },

  // Tenant - Rents properties
  TENANT: {
    name: "tenant",
    label: "Tenant",
    level: 50,
    description: "Rents and occupies properties",
  },

  // Prospective Tenant - Looking for properties
  PROSPECT: {
    name: "prospect",
    label: "Prospective Tenant",
    level: 30,
    description: "Looking for rental properties",
  },

  // Guest - Limited access
  GUEST: {
    name: "guest",
    label: "Guest User",
    level: 10,
    description: "Limited browsing access",
  },
};

// Define permissions for different actions
const PERMISSIONS = {
  // Property Management
  "property.create": "Create new properties",
  "property.read": "View property details",
  "property.read.public": "View publicly listed properties",
  "property.read.own": "View own properties",
  "property.read.managed": "View managed properties",
  "property.update": "Edit property information",
  "property.update.own": "Edit own properties",
  "property.update.managed": "Edit managed properties",
  "property.delete": "Delete properties",
  "property.delete.own": "Delete own properties",
  "property.publish": "Publish/unpublish properties",
  "property.photos.manage": "Manage property photos",

  // Tenant Management
  "tenant.create": "Add new tenants",
  "tenant.read": "View tenant information",
  "tenant.read.own": "View own tenant profile",
  "tenant.update": "Edit tenant information",
  "tenant.update.own": "Edit own tenant profile",
  "tenant.delete": "Remove tenants",
  "tenant.applications.manage": "Manage rental applications",

  // Lease Management
  "lease.create": "Create lease agreements",
  "lease.read": "View lease details",
  "lease.read.own": "View own lease",
  "lease.update": "Modify lease terms",
  "lease.update.own": "Update own lease info",
  "lease.terminate": "Terminate leases",
  "lease.renew": "Renew leases",

  // Financial Management
  "finance.rent.collect": "Collect rent payments",
  "finance.rent.pay": "Make rent payments",
  "finance.expenses.manage": "Manage property expenses",
  "finance.reports.view": "View financial reports",
  "finance.reports.generate": "Generate financial reports",

  // Maintenance Management
  "maintenance.request": "Submit maintenance requests",
  "maintenance.manage": "Manage maintenance requests",
  "maintenance.assign": "Assign maintenance tasks",
  "maintenance.complete": "Mark maintenance as complete",

  // Communication
  "communication.tenant": "Communicate with tenants",
  "communication.owner": "Communicate with property owners",
  "communication.manager": "Communicate with property managers",
  "communication.broadcast": "Send broadcast messages",

  // Application Management
  "application.submit": "Submit rental applications",
  "application.review": "Review rental applications",
  "application.approve": "Approve rental applications",
  "application.reject": "Reject rental applications",

  // System Administration
  "admin.users.manage": "Manage user accounts",
  "admin.system.configure": "Configure system settings",
  "admin.reports.all": "Access all system reports",
  "admin.audit.view": "View system audit logs",
};

// Role-Permission Matrix
const ROLE_PERMISSIONS = {
  [USER_ROLES.ADMIN.name]: [
    // Admin has all permissions
    ...Object.keys(PERMISSIONS),
  ],

  [USER_ROLES.OWNER.name]: [
    // Property Management
    "property.create",
    "property.read",
    "property.read.public",
    "property.read.own",
    "property.update.own",
    "property.delete.own",
    "property.publish",
    "property.photos.manage",

    // Tenant Management
    "tenant.create",
    "tenant.read",
    "tenant.update",
    "tenant.applications.manage",

    // Lease Management
    "lease.create",
    "lease.read",
    "lease.update",
    "lease.terminate",
    "lease.renew",

    // Financial Management
    "finance.rent.collect",
    "finance.expenses.manage",
    "finance.reports.view",
    "finance.reports.generate",

    // Maintenance Management
    "maintenance.manage",
    "maintenance.assign",
    "maintenance.complete",

    // Communication
    "communication.tenant",
    "communication.manager",
    "communication.broadcast",
  ],

  [USER_ROLES.PROPERTY_MANAGER.name]: [
    // Property Management (for managed properties)
    "property.read",
    "property.read.public",
    "property.read.managed",
    "property.update.managed",
    "property.photos.manage",

    // Tenant Management
    "tenant.create",
    "tenant.read",
    "tenant.update",
    "tenant.applications.manage",

    // Lease Management
    "lease.create",
    "lease.read",
    "lease.update",
    "lease.renew",

    // Financial Management
    "finance.rent.collect",
    "finance.reports.view",

    // Maintenance Management
    "maintenance.manage",
    "maintenance.assign",
    "maintenance.complete",

    // Communication
    "communication.tenant",
    "communication.owner",
  ],

  [USER_ROLES.TENANT.name]: [
    // Property Viewing
    "property.read.public",

    // Own Profile Management
    "tenant.read.own",
    "tenant.update.own",

    // Own Lease Management
    "lease.read.own",
    "lease.update.own",

    // Financial
    "finance.rent.pay",

    // Maintenance
    "maintenance.request",

    // Communication
    "communication.owner",
    "communication.manager",
  ],

  [USER_ROLES.PROSPECT.name]: [
    // Property Browsing
    "property.read.public",

    // Application Submission
    "application.submit",

    // Basic Profile
    "tenant.read.own",
    "tenant.update.own",
  ],

  [USER_ROLES.GUEST.name]: [
    // Limited Property Viewing
    "property.read.public",
  ],
};

// RBAC Manager Class
class RBACManager {
  constructor() {
    this.currentUser = null;
    this.currentRole = null;
  }

  // Initialize with current user
  initialize(user) {
    this.currentUser = user;
    this.currentRole = this.getUserRole(user);
    this.applyUIPermissions();
  }

  // Get user role based on user data
  getUserRole(user) {
    if (!user) return USER_ROLES.GUEST;

    // Determine role from user data
    const accountType = user.accountType || user.role || "guest";

    switch (accountType.toLowerCase()) {
      case "admin":
      case "administrator":
        return USER_ROLES.ADMIN;
      case "owner":
      case "landlord":
        return USER_ROLES.OWNER;
      case "property_manager":
      case "manager":
        return USER_ROLES.PROPERTY_MANAGER;
      case "tenant":
        return USER_ROLES.TENANT;
      case "prospect":
      case "prospective_tenant":
        return USER_ROLES.PROSPECT;
      default:
        return USER_ROLES.GUEST;
    }
  }

  // Check if current user has specific permission
  hasPermission(permission) {
    if (!this.currentRole) return false;

    const rolePermissions = ROLE_PERMISSIONS[this.currentRole.name] || [];
    return rolePermissions.includes(permission);
  }

  // Check if current user has any of the specified permissions
  hasAnyPermission(permissions) {
    return permissions.some((permission) => this.hasPermission(permission));
  }

  // Check if current user has all specified permissions
  hasAllPermissions(permissions) {
    return permissions.every((permission) => this.hasPermission(permission));
  }

  // Check if user can access a specific resource
  canAccessResource(resourceType, resourceId, action = "read") {
    const permission = `${resourceType}.${action}`;

    // Check basic permission first
    if (!this.hasPermission(permission)) {
      // Check for owner-specific permission
      const ownPermission = `${permission}.own`;
      const managedPermission = `${permission}.managed`;

      if (this.hasPermission(ownPermission)) {
        return this.isResourceOwner(resourceType, resourceId);
      }

      if (this.hasPermission(managedPermission)) {
        return this.isResourceManaged(resourceType, resourceId);
      }

      return false;
    }

    return true;
  }

  // Check if current user owns the resource
  isResourceOwner(resourceType, resourceId) {
    // This would typically check against backend data
    // For now, we'll use a simple check
    if (!this.currentUser) return false;

    // You would implement actual ownership checking here
    // This is a placeholder that should be connected to your data layer
    return false;
  }

  // Check if current user manages the resource
  isResourceManaged(resourceType, resourceId) {
    // This would typically check against backend data
    // For now, we'll use a simple check
    if (!this.currentUser) return false;

    // You would implement actual management checking here
    // This is a placeholder that should be connected to your data layer
    return false;
  }

  // Apply UI permissions - show/hide elements based on permissions
  applyUIPermissions() {
    // Hide/show navigation items
    this.toggleNavItem(
      "add-property-btn",
      this.hasPermission("property.create")
    );
    this.toggleNavItem("tenant-management", this.hasPermission("tenant.read"));
    this.toggleNavItem(
      "financial-reports",
      this.hasPermission("finance.reports.view")
    );
    this.toggleNavItem(
      "maintenance-panel",
      this.hasPermission("maintenance.manage")
    );
    this.toggleNavItem(
      "admin-panel",
      this.hasAnyPermission(["admin.users.manage", "admin.system.configure"])
    );

    // Update user role display
    this.updateRoleDisplay();
  }

  // Toggle navigation item visibility
  toggleNavItem(elementId, hasPermission) {
    const element = document.getElementById(elementId);
    if (element) {
      element.style.display = hasPermission ? "block" : "none";
    }
  }

  // Update role display in UI
  updateRoleDisplay() {
    const roleDisplay = document.getElementById("user-role-display");
    if (roleDisplay && this.currentRole) {
      roleDisplay.textContent = this.currentRole.label;
      roleDisplay.className = `badge bg-${this.getRoleColor(
        this.currentRole.name
      )}`;
    }
  }

  // Get color for role badge
  getRoleColor(roleName) {
    const colors = {
      [USER_ROLES.ADMIN.name]: "danger",
      [USER_ROLES.OWNER.name]: "success",
      [USER_ROLES.PROPERTY_MANAGER.name]: "primary",
      [USER_ROLES.TENANT.name]: "info",
      [USER_ROLES.PROSPECT.name]: "secondary",
      [USER_ROLES.GUEST.name]: "light",
    };
    return colors[roleName] || "secondary";
  }

  // Get available actions for a resource
  getAvailableActions(resourceType, resourceId = null) {
    const actions = [];
    const baseActions = ["read", "update", "delete"];

    baseActions.forEach((action) => {
      if (this.canAccessResource(resourceType, resourceId, action)) {
        actions.push(action);
      }
    });

    return actions;
  }

  // Generate permission-based menu items
  generateMenuItems() {
    const menuItems = [];

    if (this.hasPermission("property.read")) {
      menuItems.push({
        id: "properties",
        label: "Properties",
        icon: "fas fa-home",
        url: "dashboard.html",
      });
    }

    if (this.hasPermission("tenant.read")) {
      menuItems.push({
        id: "tenants",
        label: "Tenants",
        icon: "fas fa-users",
        url: "tenants.html",
      });
    }

    if (this.hasPermission("finance.reports.view")) {
      menuItems.push({
        id: "finances",
        label: "Finances",
        icon: "fas fa-dollar-sign",
        url: "finances.html",
      });
    }

    if (this.hasPermission("maintenance.manage")) {
      menuItems.push({
        id: "maintenance",
        label: "Maintenance",
        icon: "fas fa-wrench",
        url: "maintenance.html",
      });
    }

    return menuItems;
  }

  // Check if user can perform bulk operations
  canPerformBulkOperation(operation, resourceType) {
    const bulkPermissions = {
      delete: ["property.delete", "tenant.delete"],
      update: ["property.update", "tenant.update"],
      publish: ["property.publish"],
    };

    const requiredPermissions = bulkPermissions[operation] || [];
    return this.hasAnyPermission(requiredPermissions);
  }
}

// Global RBAC instance
const rbacManager = new RBACManager();

// Export for use in other modules
if (typeof window !== "undefined") {
  window.RBACManager = RBACManager;
  window.rbacManager = rbacManager;
  window.USER_ROLES = USER_ROLES;
  window.PERMISSIONS = PERMISSIONS;
}

// Role-specific dashboard configurations
const ROLE_DASHBOARDS = {
  [USER_ROLES.ADMIN.name]: {
    widgets: [
      "system_health",
      "user_stats",
      "property_stats",
      "financial_overview",
      "maintenance_alerts",
    ],
    quickActions: [
      "manage_users",
      "system_settings",
      "view_reports",
      "backup_data",
    ],
  },

  [USER_ROLES.OWNER.name]: {
    widgets: [
      "my_properties",
      "rental_income",
      "maintenance_requests",
      "tenant_overview",
    ],
    quickActions: [
      "add_property",
      "collect_rent",
      "view_reports",
      "manage_tenants",
    ],
  },

  [USER_ROLES.PROPERTY_MANAGER.name]: {
    widgets: [
      "managed_properties",
      "tenant_applications",
      "maintenance_queue",
      "rent_collection",
    ],
    quickActions: [
      "schedule_showing",
      "process_application",
      "assign_maintenance",
      "generate_report",
    ],
  },

  [USER_ROLES.TENANT.name]: {
    widgets: [
      "my_lease",
      "rent_status",
      "maintenance_requests",
      "announcements",
    ],
    quickActions: [
      "pay_rent",
      "request_maintenance",
      "contact_manager",
      "view_lease",
    ],
  },

  [USER_ROLES.PROSPECT.name]: {
    widgets: [
      "property_search",
      "my_applications",
      "saved_properties",
      "application_status",
    ],
    quickActions: [
      "search_properties",
      "submit_application",
      "schedule_viewing",
      "save_property",
    ],
  },

  [USER_ROLES.GUEST.name]: {
    widgets: ["featured_properties", "search_properties"],
    quickActions: ["register", "login", "browse_properties"],
  },
};
