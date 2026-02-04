// REGISTER
async function register() {
    const username = document.getElementById("regUsername").value;
    const password = document.getElementById("regPassword").value;
    const email = document.getElementById("regEmail").value;

    const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email })
    });

    const data = await res.json();
    alert(JSON.stringify(data));
}

// LOGIN
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    alert(JSON.stringify(data));
}

// SEND OTP
async function sendOtp() {
    const res = await fetch("/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
    });

    const data = await res.json();
    alert(JSON.stringify(data));
}

// VERIFY OTP
let TOKEN = "";

async function verifyOtp() {
    const otp = document.getElementById("otp").value;
    const username = document.getElementById("username").value;

    const res = await fetch("/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, otp })
    });

    const data = await res.json();
    if (data.dynamic_id) {
        TOKEN = data.dynamic_id;
        alert("OTP Verified!");
        loadFiles();
    } else {
        alert(JSON.stringify(data));
    }
}

// ACCESS SECURE
async function accessSecure() {
    const res = await fetch("/secure", {
        headers: { "Authorization": TOKEN }
    });

    const data = await res.json();
    alert(JSON.stringify(data));
}

// UPLOAD FILE
async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/upload", {
        method: "POST",
        headers: { "Authorization": TOKEN },
        body: formData
    });

    const data = await res.json();
    if (data.status === "uploaded") {
        alert("Upload successful!");
        loadFiles();
    } else {
        alert("Upload failed: " + JSON.stringify(data));
    }
}

// LOAD FILES
async function loadFiles() {
    const res = await fetch("/files", {
        headers: { "Authorization": TOKEN }
    });

    const data = await res.json();
    const list = document.getElementById("fileList");
    list.innerHTML = "";

    if (data.files) {
        data.files.forEach(filename => {
            const li = document.createElement("li");
            // Use session cookie for download link or fetch blob if strict header needed.
            // Since we have session fallback in auth.py, href works.
            li.innerHTML = `${filename} <a href="/download/${filename}" target="_blank">[Download]</a>`;
            list.appendChild(li);
        });
    }
}
