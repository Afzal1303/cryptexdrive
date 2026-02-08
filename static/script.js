let TOKEN = "";

function addLog(msg) {
    const ticker = document.getElementById("logTicker");
    if (ticker) {
        ticker.innerText = `> ${msg}`;
    }
}

function toggleAuth(isRegister) {
    document.getElementById("registerForm").style.display = isRegister ? "block" : "none";
    document.getElementById("loginForm").style.display = isRegister ? "none" : "block";
    addLog(isRegister ? "Switching to Registration..." : "Switching to Login...");
}

function initUI() {
    // Check if we have a token in session (fallback)
    const fileSection = document.getElementById("fileSection");
    const authSection = document.getElementById("authSection");
    
    TOKEN = sessionStorage.getItem("dynamic_id") || "";
    const isAdmin = sessionStorage.getItem("is_admin") === "true";

    if (TOKEN) {
        // Verify token validity before showing the file section
        fetch("/secure", {
            headers: { "Authorization": TOKEN }
        }).then(res => {
            if (res.ok) {
                fileSection.style.display = "block";
                authSection.style.display = "none";
                
                if (isAdmin) {
                    document.getElementById("adminLink").style.display = "block";
                }
                loadFiles();
            } else {
                // Token invalid or expired
                logout();
            }
        }).catch(() => {
            logout();
        });
    }
}

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
    alert(data.status || data.error);
}

// LOGIN
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    addLog(`Attempting login for: ${username}`);
    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (res.ok) {
        document.getElementById("otpSection").style.display = "block";
        alert("Password OK. Please request OTP.");
    } else {
        alert(data.error);
    }
}

// SEND OTP
async function sendOtp() {
    const res = await fetch("/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
    });

    const data = await res.json();
    alert(data.status || data.error);
}

// VERIFY OTP
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
            sessionStorage.setItem("dynamic_id", TOKEN); 
            sessionStorage.setItem("is_admin", data.is_admin ? "true" : "false");
            
            document.getElementById("displayUser").innerText = username;
            document.getElementById("authSection").style.display = "none";
            document.getElementById("fileSection").style.display = "block";
            
            if (data.is_admin) {
                document.getElementById("adminLink").style.display = "block";
            }
    
            loadFiles();
        }
     else {
        alert(data.error);
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
    if (res.status === 401) {
        logout();
        return;
    }

    if (data.status === "uploaded") {
        alert("Upload successful! AI Risk Score: " + data.ai_analysis.risk_score);
        loadFiles();
    } else {
        alert("Upload failed: " + JSON.stringify(data));
    }
}

// LOGOUT
async function logout() {
    await fetch("/logout", { method: "POST" });
    TOKEN = "";
    sessionStorage.removeItem("dynamic_id");
    sessionStorage.removeItem("is_admin");
    document.getElementById("authSection").style.display = "block";
    document.getElementById("fileSection").style.display = "none";
    document.getElementById("otpSection").style.display = "none";
    location.reload();
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

            li.className = "file-item";

            li.innerHTML = `

                <span class="file-name">${filename}</span>

                <button onclick="downloadFile('${filename}')" class="btn-small">Download</button>

            `;

            list.appendChild(li);

        });

    }

}



async function downloadFile(filename) {

    addLog(`Downloading ${filename}...`);

    try {

        const res = await fetch(`/download/${filename}`, {

            headers: { "Authorization": TOKEN }

        });



        if (!res.ok) {

            const errorData = await res.json();

            alert("Download failed: " + errorData.error);

            return;

        }



        const blob = await res.blob();

        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');

        a.href = url;

        a.download = filename;

        document.body.appendChild(a);

        a.click();

        window.URL.revokeObjectURL(url);

        document.body.removeChild(a);

        addLog(`Download complete: ${filename}`);

    } catch (err) {

        console.error("Download Error:", err);

        alert("Download failed due to a network error.");

    }

}
