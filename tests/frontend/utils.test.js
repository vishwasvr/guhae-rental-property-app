// Load the utils.js file
const fs = require("fs");
const path = require("path");
const utilsScript = fs.readFileSync(
  path.join(__dirname, "../../src/frontend/static/js/utils.js"),
  "utf8"
);
eval(utilsScript);

describe("AuthUtils", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe("isAuthenticated", () => {
    test("should return true when access token exists", () => {
      localStorage.setItem("accessToken", "test-token");
      expect(AuthUtils.isAuthenticated()).toBe(true);
    });

    test("should return false when access token does not exist", () => {
      expect(AuthUtils.isAuthenticated()).toBe(false);
    });
  });

  describe("getCurrentUser", () => {
    test("should return parsed user info when it exists", () => {
      const userInfo = { id: 1, email: "test@example.com", name: "Test User" };
      localStorage.setItem("userInfo", JSON.stringify(userInfo));
      expect(AuthUtils.getCurrentUser()).toEqual(userInfo);
    });

    test("should return null when user info does not exist", () => {
      expect(AuthUtils.getCurrentUser()).toBeNull();
    });

    test("should return null when user info is invalid JSON", () => {
      localStorage.setItem("userInfo", "invalid-json");
      expect(AuthUtils.getCurrentUser()).toBeNull();
    });
  });

  describe("getAuthHeaders", () => {
    test("should return authorization header when token exists", () => {
      localStorage.setItem("accessToken", "test-token");
      expect(AuthUtils.getAuthHeaders()).toEqual({
        Authorization: "Bearer test-token",
      });
    });

    test("should return empty object when token does not exist", () => {
      expect(AuthUtils.getAuthHeaders()).toEqual({});
    });
  });

  describe("getToken", () => {
    test("should return access token when it exists", () => {
      localStorage.setItem("accessToken", "test-token");
      expect(AuthUtils.getToken()).toBe("test-token");
    });

    test("should return null when access token does not exist", () => {
      expect(AuthUtils.getToken()).toBeNull();
    });
  });

  describe("logout", () => {
    test("should clear all authentication data and redirect", () => {
      // Setup
      localStorage.setItem("accessToken", "token");
      localStorage.setItem("idToken", "id-token");
      localStorage.setItem("refreshToken", "refresh-token");
      localStorage.setItem("userInfo", JSON.stringify({ id: 1 }));

      // Mock window.location
      delete window.location;
      window.location = { href: "" };

      // Execute
      AuthUtils.logout();

      // Verify
      expect(localStorage.getItem("accessToken")).toBeNull();
      expect(localStorage.getItem("idToken")).toBeNull();
      expect(localStorage.getItem("refreshToken")).toBeNull();
      expect(localStorage.getItem("userInfo")).toBeNull();
      expect(window.location.href).toBe("index.html");
    });
  });
});

describe("CONFIG", () => {
  describe("API_BASE_URL", () => {
    test("should use localhost URL for local development", () => {
      // Mock localhost
      delete window.location;
      window.location = { hostname: "localhost" };

      // Re-evaluate the config
      const configScript = fs.readFileSync(
        path.join(__dirname, "../../src/frontend/static/js/utils.js"),
        "utf8"
      );
      eval(configScript);

      expect(CONFIG.API_BASE_URL).toBe("http://localhost:3000/api");
    });

    test("should use relative path for production", () => {
      // Mock production domain
      delete window.location;
      window.location = { hostname: "myapp.com" };

      // Re-evaluate the config
      const configScript = fs.readFileSync(
        path.join(__dirname, "../../src/frontend/static/js/utils.js"),
        "utf8"
      );
      eval(configScript);

      expect(CONFIG.API_BASE_URL).toBe("/api");
    });
  });

  test("should have correct storage keys", () => {
    expect(CONFIG.STORAGE_KEYS).toEqual({
      ACCESS_TOKEN: "accessToken",
      ID_TOKEN: "idToken",
      REFRESH_TOKEN: "refreshToken",
      USER_INFO: "userInfo",
    });
  });
});
