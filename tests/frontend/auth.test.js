const fs = require("fs");
const path = require("path");

// Mock the DOM elements
document.body.innerHTML = `
  <div id="errorMessage"></div>
  <div id="successMessage"></div>
  <form id="loginForm">
    <input id="loginEmail" type="email" />
    <input id="loginPassword" type="password" />
    <button type="submit">Login</button>
  </form>
`;

// Mock the utility modules
global.UIUtils = {
  showMessage: jest.fn(),
  hideMessage: jest.fn(),
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
};

global.APIUtils = {
  post: jest.fn(),
};

global.AuthUtils = {
  storeAuthData: jest.fn(),
};

// Load the auth.js file
const authScript = fs.readFileSync(
  path.join(__dirname, "../../src/frontend/static/js/auth.js"),
  "utf8"
);
eval(authScript);

describe("Authentication Functions", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset form values
    document.getElementById("loginEmail").value = "";
    document.getElementById("loginPassword").value = "";
  });

  describe("handleLogin", () => {
    test("should show error for empty fields", async () => {
      const mockEvent = {
        preventDefault: jest.fn(),
        target: document.getElementById("loginForm"),
      };

      await handleLogin(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(UIUtils.showMessage).toHaveBeenCalledWith(
        "errorMessage",
        "Please enter both email and password",
        "danger"
      );
    });

    test("should handle successful login", async () => {
      const mockEvent = {
        preventDefault: jest.fn(),
        target: document.getElementById("loginForm"),
      };

      document.getElementById("loginEmail").value = "test@example.com";
      document.getElementById("loginPassword").value = "password123";

      const mockResponse = {
        tokens: { access_token: "token123" },
        user: { id: 1, email: "test@example.com" },
      };

      APIUtils.post.mockResolvedValue(mockResponse);

      // Mock window.location
      delete window.location;
      window.location = { href: "" };

      await handleLogin(mockEvent);

      expect(APIUtils.post).toHaveBeenCalledWith("/auth/login", {
        username: "test@example.com",
        password: "password123",
      });
      expect(AuthUtils.storeAuthData).toHaveBeenCalledWith(
        mockResponse.tokens,
        mockResponse.user
      );
      expect(UIUtils.showMessage).toHaveBeenCalledWith(
        "successMessage",
        "Login successful! Redirecting to dashboard...",
        "success"
      );
    });

    test("should handle login error", async () => {
      const mockEvent = {
        preventDefault: jest.fn(),
        target: document.getElementById("loginForm"),
      };

      document.getElementById("loginEmail").value = "test@example.com";
      document.getElementById("loginPassword").value = "wrongpassword";

      const mockError = new Error("Invalid credentials");
      APIUtils.post.mockRejectedValue(mockError);

      await handleLogin(mockEvent);

      expect(UIUtils.showMessage).toHaveBeenCalledWith(
        "errorMessage",
        "Connection error: Invalid credentials. Check browser console for details.",
        "danger"
      );
    });
  });

  describe("Utility Functions", () => {
    test("showError should call UIUtils.showMessage", () => {
      showError("Test error message");

      expect(UIUtils.showMessage).toHaveBeenCalledWith(
        "errorMessage",
        "Test error message",
        "danger"
      );
      expect(UIUtils.hideMessage).toHaveBeenCalledWith("successMessage");
    });

    test("showSuccess should call UIUtils.showMessage", () => {
      showSuccess("Test success message");

      expect(UIUtils.showMessage).toHaveBeenCalledWith(
        "successMessage",
        "Test success message",
        "success"
      );
      expect(UIUtils.hideMessage).toHaveBeenCalledWith("errorMessage");
    });

    test("hideMessages should hide both messages", () => {
      hideMessages();

      expect(UIUtils.hideMessage).toHaveBeenCalledWith("errorMessage");
      expect(UIUtils.hideMessage).toHaveBeenCalledWith("successMessage");
    });
  });
});
