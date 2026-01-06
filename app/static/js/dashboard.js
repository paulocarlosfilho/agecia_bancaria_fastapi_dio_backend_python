const Dashboard = {
    accounts: [],
    currentPage: 1,

    async init() {
        if (!API.isAuthenticated()) return;
        await this.loadUser();
        await this.refresh();
        this.setupEventListeners();
    },

    async loadUser() {
        try {
            const user = await API.request('/users/me');
            document.getElementById('user-name').textContent = user.full_name;
            document.getElementById('user-email').textContent = user.email;
        } catch (err) {
            console.error('Erro ao carregar usuário');
        }
    },

    async refresh() {
        await this.loadAccounts();
        await this.loadTransactions();
    },

    async loadAccounts() {
        try {
            this.accounts = await API.request('/banking/accounts');
            this.renderAccounts();
            this.updateAccountSelects();
        } catch (err) {
            console.error('Erro ao carregar contas');
        }
    },

    renderAccounts() {
        const list = document.getElementById('accounts-list');
        if (this.accounts.length === 0) {
            list.innerHTML = `<p class="text-center text-gray-400 py-8 text-sm italic">Nenhuma conta ativa</p>`;
            return;
        }

        list.innerHTML = this.accounts.map(acc => {
            const isChecking = acc.account_type.toLowerCase() === 'checking';
            return `
                <div class="account-card p-4 rounded-xl bg-gray-50 border border-gray-100 hover:border-blue-200 transition-all relative group">
                    <button onclick="Dashboard.deleteAccount(${acc.id})" class="delete-btn absolute top-2 right-2 p-1 text-gray-300 hover:text-red-500 opacity-0 transition-all">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] font-bold ${isChecking ? 'text-blue-600' : 'text-orange-600'} uppercase tracking-wider">
                            ${isChecking ? 'Conta Corrente' : 'Conta Poupança'}
                        </span>
                        <span class="text-[10px] text-gray-400 font-mono">${acc.account_number}</span>
                    </div>
                    <div class="flex justify-between items-end">
                        <div>
                            <p class="text-2xl font-bold text-gray-900">R$ ${acc.balance.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                            <p class="text-xs text-gray-400">${acc.nickname || (isChecking ? 'Corrente' : 'Poupança')}</p>
                        </div>
                        <i data-lucide="${isChecking ? 'credit-card' : 'piggy-bank'}" class="w-5 h-5 text-gray-300"></i>
                    </div>
                </div>
            `;
        }).join('');
        lucide.createIcons();
    },

    async loadTransactions() {
        const list = document.getElementById('transactions-list');
        try {
            const skip = (this.currentPage - 1) * 10;
            const data = await API.request(`/banking/transactions?skip=${skip}&limit=10`);
            
            if (data.length === 0) {
                list.innerHTML = `<div class="text-center py-20 text-gray-400"><p>Nenhuma transação encontrada</p></div>`;
                return;
            }

            list.innerHTML = data.map(t => {
                const isPositive = t.type === 'DEPOSIT' || t.type === 'TRANSFER_IN';
                return `
                    <div class="flex items-center justify-between p-4 hover:bg-gray-50 rounded-xl transition-colors">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full flex items-center justify-center ${isPositive ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}">
                                <i data-lucide="${isPositive ? 'arrow-down-left' : 'arrow-up-right'}" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <p class="text-sm font-semibold text-gray-900">${this.translateType(t.type)}</p>
                                <p class="text-xs text-gray-500">${new Date(t.created_at).toLocaleDateString()} - ${t.description || 'Sem descrição'}</p>
                            </div>
                        </div>
                        <p class="text-sm font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}">
                            ${isPositive ? '+' : '-'} R$ ${Math.abs(t.amount).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </p>
                    </div>
                `;
            }).join('');
            lucide.createIcons();
        } catch (err) {
            console.error('Erro ao carregar transações');
        }
    },

    translateType(type) {
        const types = {
            'DEPOSIT': 'Depósito',
            'WITHDRAW': 'Saque',
            'TRANSFER_OUT': 'Transferência Enviada',
            'TRANSFER_IN': 'Transferência Recebida'
        };
        return types[type] || type;
    },

    showCreateModal() {
        document.getElementById('create-account-modal').classList.remove('hidden');
    },

    hideCreateModal() {
        document.getElementById('create-account-modal').classList.add('hidden');
    },

    async createAccount(type) {
        try {
            await API.request('/banking/accounts', {
                method: 'POST',
                body: JSON.stringify({ account_type: type })
            });
            this.hideCreateModal();
            API.showToast('Conta criada com sucesso!', 'success');
            await this.refresh();
        } catch (err) {
            API.showToast(err.message);
        }
    },

    async deleteAccount(id) {
        if (!confirm('Deseja desativar esta conta?')) return;
        try {
            await API.request(`/banking/accounts/${id}`, { method: 'DELETE' });
            API.showToast('Conta desativada com sucesso', 'success');
            await this.refresh();
        } catch (err) {
            API.showToast(err.message);
        }
    },

    openModal(type) {
        const titles = { deposit: 'Realizar Depósito', withdraw: 'Realizar Saque', transfer: 'Transferência' };
        document.getElementById('modal-title').textContent = titles[type];
        document.getElementById('action-type').value = type;
        document.getElementById('target-account-field').classList.toggle('hidden', type !== 'transfer');
        document.getElementById('action-modal').classList.remove('hidden');
    },

    closeModal() {
        document.getElementById('action-modal').classList.add('hidden');
        document.getElementById('action-form').reset();
    },

    updateAccountSelects() {
        const select = document.getElementById('modal-account-id');
        select.innerHTML = this.accounts.map(acc => `
            <option value="${acc.id}">${acc.account_number} (R$ ${acc.balance.toFixed(2)})</option>
        `).join('');
    },

    setupEventListeners() {
        document.getElementById('action-form').onsubmit = async (e) => {
            e.preventDefault();
            const type = document.getElementById('action-type').value;
            const accountId = document.getElementById('modal-account-id').value;
            const amount = parseFloat(document.getElementById('modal-amount').value);
            const description = document.getElementById('modal-description').value;

            try {
                let endpoint = `/banking/accounts/${accountId}/${type}`;
                let body = { amount, description };

                if (type === 'transfer') {
                    endpoint = `/banking/accounts/${accountId}/transfer`;
                    body.target_account_number = document.getElementById('modal-target-number').value;
                }

                await API.request(endpoint, {
                    method: 'POST',
                    body: JSON.stringify(body)
                });

                API.showToast('Operação realizada com sucesso!', 'success');
                this.closeModal();
                await this.refresh();
            } catch (err) {
                API.showToast(err.message);
            }
        };
    },

    changePage(delta) {
        this.currentPage = Math.max(1, this.currentPage + delta);
        document.getElementById('current-page').textContent = this.currentPage;
        this.loadTransactions();
    }
};

Dashboard.init();
