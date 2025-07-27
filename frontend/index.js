
/**
 * Child Dashboard Application
 * Modular architecture for task management and timer functionality
 */

// ====== CONFIGURATION ======
const CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:8000',
    TIMER_INTERVAL_MS: 1000,
    NETWORKING_CHECK_INTERVAL_MS: 10000,
    REWARD_LOAD_DELAY_MS: 1000
};

// ====== STATE MANAGEMENT ======
const AppState = {
    timer: {
        interval: null,
        seconds: 0,
        isRunning() { return this.interval !== null; }
    },
    networking: {
        checkInterval: null
    }
};

// ====== API SERVICE ======
const ApiService = {
    async get(endpoint) {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return response.json();
    },

    async put(endpoint, data = null) {
        const options = {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        };
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, options);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return response;
    },

    async post(endpoint, data) {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return response;
    }
};

// ====== UTILITY FUNCTIONS ======
const Utils = {
    formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    },

    getElementById(id) {
        const element = document.getElementById(id);
        if (!element) throw new Error(`Element with id '${id}' not found`);
        return element;
    }
};

// ====== UI MANAGER ======
const UIManager = {
    updateTimerDisplay() {
        Utils.getElementById('timerDisplay').textContent = Utils.formatTime(AppState.timer.seconds);
    },

    updateBackgroundColor() {
        document.body.style.backgroundColor = AppState.timer.isRunning() ? 'green' : 'red';
    },

    setTimerButtonStates(isRunning) {
        Utils.getElementById('startTimerBtn').disabled = isRunning;
        Utils.getElementById('stopTimerBtn').disabled = !isRunning;
    },

    renderTasks(tasks) {
        const tbody = Utils.getElementById('tasksBody');
        tbody.innerHTML = '';
        
        tasks.forEach(task => {
            const row = tbody.insertRow();
            const actionContent = this._getTaskActionContent(task);
            
            row.innerHTML = `
                <td class="zyx-table-cell">${task.title}</td>
                <td class="zyx-table-cell">${task.reward} min</td>
                <td class="zyx-table-cell">${task.status}</td>
                <td class="zyx-table-cell">${actionContent}</td>
            `;
        });
    },

    _getTaskActionContent(task) {
        if (task.status === 'pending') {
            return `<button class="zyx-btn zyx-btn-start" onclick="TaskManager.startTask(${task.id})">Start</button>`;
        } else if (task.status === 'working') {
            return '<span class="zyx-working-message">Tell parent when you are done.</span>';
        }
        return '';
    }
};

// ====== TASK MANAGER ======
const TaskManager = {
    async loadTasks() {
        try {
            const tasks = await ApiService.get('/tasks/');
            const activeTasks = tasks.filter(task => 
                task.status === 'pending' || task.status === 'working'
            );
            UIManager.renderTasks(activeTasks);
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    },

    async startTask(taskId) {
        try {
            await ApiService.put(`/tasks/${taskId}/status`, { action: 'start' });
            await this.loadTasks();
        } catch (error) {
            console.error('Error starting task:', error);
        }
    }
};

// ====== TIMER MANAGER ======
const TimerManager = {
    async loadFromReward() {
        try {
            const rewardData = await ApiService.get('/reward');
            const reward = rewardData.total_reward || 0;
            AppState.timer.seconds = reward * 60;
            UIManager.updateTimerDisplay();
        } catch (error) {
            console.error('Error loading reward for timer:', error);
        }
    },

    start() {
        if (AppState.timer.seconds <= 0) return;
        
        UIManager.setTimerButtonStates(true);
        
        AppState.timer.interval = setInterval(() => {
            AppState.timer.seconds--;
            UIManager.updateTimerDisplay();
            
            if (AppState.timer.seconds <= 0) {
                this.stop();
            }
        }, CONFIG.TIMER_INTERVAL_MS);
        
        UIManager.updateBackgroundColor();
    },

    stop() {
        if (AppState.timer.interval) {
            clearInterval(AppState.timer.interval);
            AppState.timer.interval = null;
        }
        
        UIManager.setTimerButtonStates(false);
        UIManager.updateBackgroundColor();
        
        this._syncToDatabase();
    },

    async _syncToDatabase() {
        try {
            const remainingMinutes = Math.ceil(AppState.timer.seconds / 60);
            await ApiService.put(`/reward?new_value=${remainingMinutes}`);
        } catch (error) {
            console.error('Error syncing to database:', error);
        }
    }
};

// ====== NETWORKING MANAGER ======
const NetworkingManager = {
    async checkStatus() {
        try {
            const state = AppState.timer.isRunning() ? "on" : "off";
            await ApiService.post('/networking', { state });
        } catch (error) {
            console.error('Error checking networking status:', error);
        }
    },

    startPeriodicCheck() {
        AppState.networking.checkInterval = setInterval(
            () => this.checkStatus(),
            CONFIG.NETWORKING_CHECK_INTERVAL_MS
        );
    }
};

// ====== APPLICATION INITIALIZATION ======
const App = {
    async init() {
        await TaskManager.loadTasks();
        
        // Load timer after delay to ensure DOM is ready
        setTimeout(() => {
            TimerManager.loadFromReward();
        }, CONFIG.REWARD_LOAD_DELAY_MS);
        
        NetworkingManager.startPeriodicCheck();
        UIManager.updateBackgroundColor();
    }
};

// ====== GLOBAL FUNCTIONS (for HTML onclick handlers) ======
window.startTimer = () => TimerManager.start();
window.stopTimer = () => TimerManager.stop();

// ====== APPLICATION STARTUP ======
window.addEventListener('load', () => App.init());
