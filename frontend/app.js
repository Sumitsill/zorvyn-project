const API_BASE = "http://127.0.0.1:8000/api";
let categoryChartInstance = null;

// State
let appState = {
    token: localStorage.getItem("token"),
    role: null,
    currentPage: 1
};

// DOM Elements
const authView = document.getElementById("auth-view");
const mainView = document.getElementById("main-view");
const loginForm = document.getElementById("login-form");
const logoutBtn = document.getElementById("logout-btn");
const pageTitle = document.getElementById("page-title");
const roleBadge = document.getElementById("user-role-badge");

// Initialize
function init() {
    if (appState.token) {
        // Very basic validation (should use an endpoint to check usually)
        let payload;
        try {
            payload = JSON.parse(atob(appState.token.split('.')[1]));
            appState.role = payload.role;
            showMainView();
        } catch (e) {
            logout();
        }
    } else {
        showAuthView();
    }
    document.getElementById("rec-date").valueAsDate = new Date();
}

function showAuthView() {
    authView.classList.add("active");
    mainView.classList.remove("active");
}

function showMainView() {
    authView.classList.remove("active");
    mainView.classList.add("active");
    
    // UI logic based on role
    roleBadge.textContent = appState.role;
    
    document.getElementById("nav-records").style.display = "none";
    document.getElementById("nav-users").style.display = "none";
    document.getElementById("new-record-btn").classList.add("hidden");
    document.getElementById("new-user-btn").classList.add("hidden");
    
    if (appState.role === "ADMIN" || appState.role === "ANALYST") {
        document.getElementById("nav-records").style.display = "block";
    }
    
    if (appState.role === "ADMIN") {
        document.getElementById("nav-users").style.display = "block";
        document.getElementById("new-record-btn").classList.remove("hidden");
        document.getElementById("new-user-btn").classList.remove("hidden");
    }

    loadDashboard();
}

function logout() {
    localStorage.removeItem("token");
    appState.token = null;
    appState.role = null;
    loginForm.reset();
    showAuthView();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

// Interceptors / Request Helpers
async function apiRequest(endpoint, options = {}) {
    if (!options.headers) options.headers = {};
    if (appState.token) {
        options.headers["Authorization"] = `Bearer ${appState.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);
    
    if (response.status === 401) {
        logout();
        throw new Error("Unauthorized");
    } else if (response.status === 403) {
        throw new Error("Forbidden: You don't have permission for this action.");
    } else if (!response.ok) {
        let msg = "An error occurred";
        try {
            const data = await response.json();
            msg = data.detail || msg;
        } catch (e) {}
        throw new Error(msg); 
    }

    if (response.status === 204) return null;
    
    return await response.json();
}

// --- Auth ---
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const errorEl = document.getElementById("login-error");
    
    errorEl.textContent = "";

    try {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Login failed");
        }

        const data = await response.json();
        appState.token = data.access_token;
        localStorage.setItem("token", data.access_token);
        
        init();
    } catch (err) {
        errorEl.textContent = err.message;
    }
});

logoutBtn.addEventListener("click", logout);

// --- Navigation ---
document.querySelectorAll(".nav-links li").forEach(li => {
    li.addEventListener("click", (e) => {
        document.querySelectorAll(".nav-links li").forEach(el => el.classList.remove("active"));
        e.target.classList.add("active");
        
        const targetId = e.target.getAttribute("data-target");
        
        document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
        document.getElementById(targetId).classList.add("active");

        if (targetId === "dashboard-tab") {
            pageTitle.textContent = "Overview";
            loadDashboard();
        } else if (targetId === "records-tab") {
            pageTitle.textContent = "Financial Records";
            appState.currentPage = 1;
            loadRecords();
        } else if (targetId === "users-tab") {
            pageTitle.textContent = "User Management";
            loadUsers();
        }
    });
});

// --- Dashboard Logic ---
async function loadDashboard() {
    try {
        const summary = await apiRequest("/dashboard/summary");
        document.getElementById("stat-income").textContent = formatCurrency(summary.total_income);
        document.getElementById("stat-expenses").textContent = formatCurrency(summary.total_expenses);
        document.getElementById("stat-balance").textContent = formatCurrency(summary.net_balance);

        const recent = await apiRequest("/dashboard/recent-activity");
        const recentList = document.getElementById("recent-activity-list");
        recentList.innerHTML = recent.map(r => `
            <li class="activity-item">
                <div>
                    <strong>${r.category}</strong><br>
                    <small style="color: var(--text-secondary)">${r.date}</small>
                </div>
                <div class="stat-value ${r.transaction_type === 'INCOME' ? 'text-success' : 'text-danger'}" style="font-size: 1.2rem">
                    ${r.transaction_type === 'INCOME' ? '+' : '-'}${formatCurrency(r.amount)}
                </div>
            </li>
        `).join('');

        // Update Chart
        const catTotals = await apiRequest("/dashboard/category-totals");
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        const labels = catTotals.map(c => c.category);
        const data = catTotals.map(c => c.total);
        const colors = [
            'rgb(59, 130, 246)', 
            'rgb(16, 185, 129)', 
            'rgb(245, 158, 11)', 
            'rgb(239, 68, 68)', 
            'rgb(139, 92, 246)'
        ];

        if(categoryChartInstance) {
            categoryChartInstance.data.labels = labels;
            categoryChartInstance.data.datasets[0].data = data;
            categoryChartInstance.update();
        } else {
            Chart.defaults.color = '#94a3b8';
            categoryChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Dashboard error:", e);
    }
}

// --- Records Logic ---
async function loadRecords() {
    try {
        const data = await apiRequest(`/records/?page=${appState.currentPage}&limit=10`);
        const tbody = document.getElementById("records-tbody");
        
        if (appState.role === "ADMIN") {
            document.querySelector(".actions-header").classList.remove("hidden");
        } else {
            document.querySelector(".actions-header").classList.add("hidden");
        }
        
        tbody.innerHTML = data.data.map(r => `
            <tr>
                <td>${r.date}</td>
                <td>${r.category}</td>
                <td style="color:var(--text-secondary)">${r.description || '-'}</td>
                <td style="font-weight:600">${formatCurrency(r.amount)}</td>
                <td><span class="type-badge ${r.transaction_type.toLowerCase()}">${r.transaction_type}</span></td>
                ${appState.role === "ADMIN" ? `<td><button onclick="deleteRecord('${r.id}')" class="icon-btn text-danger">✕</button></td>` : ''}
            </tr>
        `).join('');

        document.getElementById("page-indicator").textContent = `Page ${data.page}`;
    } catch (e) {
        console.error("Records error:", e);
    }
}

async function deleteRecord(id) {
    if(!confirm("Delete this financial record permanently?")) return;
    try {
        await apiRequest(`/records/${id}`, { method: "DELETE" });
        loadRecords();
        loadDashboard();
    } catch(e) {
        alert(e.message);
    }
}

// --- Users Logic ---
async function loadUsers() {
    try {
        const users = await apiRequest(`/users/`);
        const tbody = document.getElementById("users-tbody");
        
        tbody.innerHTML = users.map(u => `
            <tr>
                <td style="font-weight:500">${u.email}</td>
                <td>
                    <select onchange="updateUserRole('${u.id}', this.value)" style="background:var(--bg-dark); border:1px solid var(--glass-border); color:white; padding:4px; border-radius:4px;">
                        <option value="VIEWER" ${u.role === 'VIEWER' ? 'selected' : ''}>Viewer</option>
                        <option value="ANALYST" ${u.role === 'ANALYST' ? 'selected' : ''}>Analyst</option>
                        <option value="ADMIN" ${u.role === 'ADMIN' ? 'selected' : ''}>Admin</option>
                    </select>
                </td>
                <td>
                    <span class="type-badge ${u.is_active ? 'income' : 'expense'}" style="cursor:pointer;" onclick="toggleUserStatus('${u.id}')">
                        ${u.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td style="color:var(--text-secondary)">${new Date(u.created_at).toLocaleDateString()}</td>
                <td><span class="text-secondary">-</span></td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Users error:", e);
    }
}

async function updateUserRole(id, newRole) {
    try {
        await apiRequest(`/users/${id}/role?role=${newRole}`, { method: "PUT" });
        loadUsers();
    } catch(e) {
        alert(e.message);
        loadUsers(); // revert
    }
}

async function toggleUserStatus(id) {
    try {
        await apiRequest(`/users/${id}/status`, { method: "PUT" });
        loadUsers();
    } catch(e) {
        alert(e.message);
    }
}

document.getElementById("prev-page").addEventListener("click", () => {
    if (appState.currentPage > 1) {
        appState.currentPage--;
        loadRecords();
    }
});
document.getElementById("next-page").addEventListener("click", () => {
    appState.currentPage++;
    loadRecords();
});

// --- Modal Logic ---
const modal = document.getElementById("record-modal");
document.getElementById("new-record-btn").addEventListener("click", () => {
    modal.classList.add("active");
});
document.getElementById("close-modal").addEventListener("click", () => {
    modal.classList.remove("active");
    document.getElementById("record-form").reset();
    document.getElementById("rec-date").valueAsDate = new Date();
});

document.getElementById("record-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("rec-error");
    errorEl.textContent = "";

    const payload = {
        amount: parseFloat(document.getElementById("rec-amount").value),
        transaction_type: document.getElementById("rec-type").value,
        category: document.getElementById("rec-category").value,
        date: document.getElementById("rec-date").value,
        description: document.getElementById("rec-desc").value || null,
    };

    try {
        await apiRequest("/records/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        modal.classList.remove("active");
        document.getElementById("record-form").reset();
        
        if (document.getElementById("dashboard-tab").classList.contains("active")) {
            loadDashboard();
        } else if (document.getElementById("records-tab").classList.contains("active")) {
            loadRecords();
        }
    } catch (e) {
        errorEl.textContent = e.message;
    }
});

init();
