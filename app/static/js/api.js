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
            throw new Error(data.detail || 'Erro na requisição');
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
    }
};
