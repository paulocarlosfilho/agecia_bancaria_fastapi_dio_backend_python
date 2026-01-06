const API = {
    token: localStorage.getItem('token'),

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`/api/v1${endpoint}`, { ...options, headers });
        
        if (response.status === 401) {
            this.logout();
            return null;
        }

        const data = await response.json();
        if (!response.ok) {
            const message = data.error?.message || data.detail || 'Erro na requisição';
            throw new Error(message);
        }
        return data;
    },

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    },

    logout() {
        this.token = null;
        localStorage.removeItem('token');
        window.location.href = '/login';
    },

    isAuthenticated() {
        return !!this.token;
    },

    showToast(message, type = 'error') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-600' : 'bg-red-600';
        const icon = type === 'success' ? 'check-circle' : 'alert-circle';

        toast.className = `${bgColor} text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-3 transform transition-all duration-300 translate-y-10 opacity-0`;
        toast.innerHTML = `
            <i data-lucide="${icon}" class="w-5 h-5"></i>
            <span class="text-sm font-semibold">${message}</span>
        `;

        container.appendChild(toast);
        lucide.createIcons();

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
        }, 10);

        // Remove after 5s
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
};
