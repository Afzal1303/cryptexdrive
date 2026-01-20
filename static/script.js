async function login() {
  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: username.value,
      password: password.value
    })
  });

  alert(res.ok ? "Password OK" : "Login failed");
}

async function sendOTP() {
  const res = await fetch("/send-otp", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email: email.value })
  });

  alert(res.ok ? "OTP sent" : "Wait before retry");
}

async function verifyOTP() {
  const res = await fetch("/verify-otp", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: username.value,
      otp: otp.value
    })
  });

  const data = await res.json();

  if (data.dynamic_id) {
    localStorage.setItem("token", data.dynamic_id);
    alert("Login successful");
  } else {
    alert("OTP invalid");
  }
}

async function accessSecure() {
  const res = await fetch("/secure", {
    headers: {
      "Authorization": localStorage.getItem("token")
    }
  });

  const data = await res.json();
  alert(JSON.stringify(data));
}
