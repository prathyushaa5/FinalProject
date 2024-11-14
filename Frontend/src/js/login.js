const form = document.querySelector("#login-form");
const errorMessage = document.querySelector("#error-message");

const passwordInput = document.getElementById("password");
const showPasswordButton = document.getElementById("show-password");
showPasswordButton.addEventListener("click", () => {
  event.preventDefault();
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    showPasswordButton.innerHTML = '<span class="far fa-eye"></span>';
  } else {
    passwordInput.type = "password";
    showPasswordButton.innerHTML =
      '<span class="far fa-eye-slash"></span>';
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const username = form.elements.username.value;
  const password = form.elements.password.value;

  localStorage.setItem("uid", username);

  const response = await fetch("http://localhost:5000/api/login2", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.token) {
        const settings = {
          currWorkout: "squat",
          currDuration: "3 Minutes",
          isAccessCamera: true,
          isAudioEffect: true,
          isDeveloperMode: false,
          isDirectionSign: true,
          isFlipCamera: false,
          isFullscreen: false,
        };

        localStorage.setItem("DBWOSettings", JSON.stringify(settings));

        // Token received, store it in localStorage or a secure cookie
        localStorage.setItem("token", data.token);
        // Redirect the user to the dashboard or perform any other necessary actions
        window.location.href = "http://localhost:8080/dashboard.html";
      } else {
        // Handle invalid credentials or other login errors
        errorMessage.style.display = "block";
        console.error("Invalid credentials");
      }
    })
    .catch((error) => {
      console.error("Error logging in:", error);
      // Handle error if necessary
    });

  // if (response.status === 200) {
  // 	window.location.href = 'http://18.191.166.16:8080/dashboard.html';
  // } else {
  // 	errorMessage.style.display = 'block';
  // }
});