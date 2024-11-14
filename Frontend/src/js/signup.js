// Validation and Registration Logic
const form = document.getElementById("register-form");
const usernameErrorMessage = document.getElementById("username-error-message");
const emailErrorMessage = document.getElementById("email-error-message");
const passwordStrength = document.getElementById("password-strength-message");
const showPasswordButton = document.getElementById("show-password");
const passwordInput = document.getElementById("password");

const usernameRegex = /^[a-zA-Z0-9_]{5,15}$/;
const emailRegex = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,})+$/;
const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

showPasswordButton.addEventListener("click", (event) => {
  event.preventDefault();
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    showPasswordButton.innerHTML = '<span class="far fa-eye"></span>';
  } else {
    passwordInput.type = "password";
    showPasswordButton.innerHTML = '<span class="far fa-eye-slash"></span>';
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  let hasErrors = false;
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = passwordInput.value;

  if (!usernameRegex.test(username)) {
    usernameErrorMessage.style.display = "block";
    hasErrors = true;
  } else {
    usernameErrorMessage.style.display = "none";
  }

  if (!emailRegex.test(email)) {
    emailErrorMessage.style.display = "block";
    hasErrors = true;
  } else {
    emailErrorMessage.style.display = "none";
  }

  if (!passwordRegex.test(password)) {
    passwordStrength.textContent = "Weak password";
    passwordStrength.style.color = "red";
    passwordStrength.style.display = "block";
    hasErrors = true;
  } else {
    passwordStrength.style.display = "none";
  }

  if (!hasErrors) {
    try {
      const response = await fetch("http://localhost:5000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      if (response.status === 200) {
        alert("Registration Successful!");
        window.location.href = "login.html";
      } else if (response.status === 400) {
        alert("User Already Exists");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }
});
