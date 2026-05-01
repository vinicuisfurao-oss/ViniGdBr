const API_BASE = 'http://localhost:5000/api';

let currentTab = 'rankings';
let users = [];
let achievements = [];
let categories = [];

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadRankings();
});

// Tab Switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    currentTab = tabName;
    
    if (tabName === 'achievements') {
        loadAchievements();
    }
}

// Load Rankings
async function loadRankings() {
    try {
        const category = document.getElementById('categoryFilter')?.value;
        const url = category ? `${API_BASE}/rankings/category/${category}` : `${API_BASE}/rankings`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        displayRankings(data);
    } catch (error) {
        console.error('Error loading rankings:', error);
    }
}

function displayRankings(rankings) {
    const container = document.getElementById('rankingsList');
    
    container.innerHTML = rankings.map((item, idx) => {
        let badge = '🥇';
        if (idx === 1) badge = '🥈';
        if (idx === 2) badge = '🥉';
        if (idx > 2) badge = `#${idx + 1}`;
        
        const userData = item.user || item;
        const points = item.total_points || item.category_points || 0;
        
        return `
            <div class="ranking-item">
                <div class="ranking-badge">${badge}</div>
                <div class="ranking-info">
                    <h3>${userData.username}</h3>
                    <div class="ranking-stats">
                        <span>💎 ${points} points</span>
                        <span>✅ ${userData.verified_achievements} verified</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function filterRankings() {
    const searchTerm = document.getElementById('searchUser').value.toLowerCase();
    const items = document.querySelectorAll('.ranking-item');
    
    items.forEach(item => {
        const username = item.querySelector('h3').textContent.toLowerCase();
        item.style.display = username.includes(searchTerm) ? 'flex' : 'none';
    });
}

// Load Achievements
async function loadAchievements() {
    try {
        const category = document.getElementById('categorySelect')?.value;
        const verifiedOnly = document.getElementById('verifiedOnly')?.checked;
        
        let url = `${API_BASE}/achievements`;
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        if (verifiedOnly) params.append('verified', 'true');
        if (params.toString()) url += '?' + params.toString();
        
        const response = await fetch(url);
        achievements = await response.json();
        
        displayAchievements(achievements);
    } catch (error) {
        console.error('Error loading achievements:', error);
    }
}

function displayAchievements(achs) {
    const container = document.getElementById('achievementsList');
    
    if (achs.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 40px;">No achievements found</p>';
        return;
    }
    
    container.innerHTML = achs.map(ach => `
        <div class="achievement-card">
            <h3>
                ${ach.title}
                <span class="achievement-badge ${ach.verified ? 'achievement-verified' : ''}">
                    ${ach.verified ? '✓' : '⏳'}
                </span>
            </h3>
            <p>${ach.description}</p>
            <div class="achievement-meta">
                <span>📁 ${ach.category}</span>
                <span>⭐ ${ach.difficulty}</span>
                <span>💎 ${ach.points}</span>
                <span>✅ ${ach.verification_count}/3</span>
            </div>
            <p style="font-size: 0.9em; color: #666;">by <strong>${ach.author}</strong></p>
        </div>
    `).join('');
}

// Load Categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        categories = await response.json();
        
        const selects = document.querySelectorAll('#categorySelect, #categoryFilter');
        selects.forEach(select => {
            const current = select.value;
            select.innerHTML = '<option value="">All Categories</option>';
            categories.forEach(cat => {
                select.innerHTML += `<option value="${cat}">${cat}</option>`;
            });
            select.value = current;
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Submit Achievement
async function submitAchievement(event) {
    event.preventDefault();
    
    const username = document.getElementById('submitUsername').value;
    const title = document.getElementById('submitTitle').value;
    const description = document.getElementById('submitDescription').value;
    const category = document.getElementById('submitCategory').value;
    const difficulty = document.getElementById('submitDifficulty').value;
    const points = parseInt(document.getElementById('submitPoints').value);
    
    try {
        // First, find or create user
        let userId;
        const usersResp = await fetch(`${API_BASE}/users`);
        const allUsers = await usersResp.json();
        const user = allUsers.find(u => u.username === username);
        
        if (user) {
            userId = user.id;
        } else {
            const createResp = await fetch(`${API_BASE}/users`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email: `${username}@denoument.local` })
            });
            const newUser = await createResp.json();
            userId = newUser.id;
        }
        
        // Create achievement
        const resp = await fetch(`${API_BASE}/achievements`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                category,
                difficulty,
                points,
                author_id: userId
            })
        });
        
        if (resp.ok) {
            alert('🎉 Achievement submitted successfully!');
            document.getElementById('submitForm').reset();
            loadAchievements();
            loadRankings();
        } else {
            alert('Error submitting achievement');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error submitting achievement');
    }
}