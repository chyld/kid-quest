console.log("Parent dashboard loaded");

let editingTaskId = null;

function editTask(taskId, title, reward) {
    editingTaskId = taskId;
    document.getElementById('taskTitle').value = title;
    document.getElementById('taskReward').value = reward;
    document.querySelector('#taskForm button[type="submit"]').textContent = 'Update Task';
}

async function createTask(event) {
    event.preventDefault();
    
    const title = document.getElementById('taskTitle').value;
    const reward = parseInt(document.getElementById('taskReward').value);
    
    try {
        if (editingTaskId) {
            // Update existing task
            const response = await fetch(`http://127.0.0.1:8000/tasks/${editingTaskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    reward: reward
                })
            });
            
            if (response.ok) {
                editingTaskId = null;
                document.querySelector('#taskForm button[type="submit"]').textContent = 'Create Task';
                document.getElementById('taskForm').reset();
                loadTasks();
            }
        } else {
            // Create new task
            const response = await fetch('http://127.0.0.1:8000/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    reward: reward
                })
            });
            
            if (response.ok) {
                document.getElementById('taskForm').reset();
                loadTasks();
            }
        }
    } catch (error) {
        console.error('Error with task:', error);
    }
}

async function loadReward() {
    try {
        const response = await fetch('http://127.0.0.1:8000/reward');
        const rewardData = await response.json();
        document.getElementById('currentReward').textContent = rewardData.total_reward || 0;
    } catch (error) {
        console.error('Error loading reward:', error);
    }
}

async function updateReward(event) {
    event.preventDefault();
    
    const newValue = parseInt(document.getElementById('newReward').value);
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/reward?new_value=${newValue}`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            document.getElementById('rewardForm').reset();
            loadReward();
        }
    } catch (error) {
        console.error('Error updating reward:', error);
    }
}

async function loadTasks() {
    try {
        const response = await fetch('http://127.0.0.1:8000/tasks/');
        const tasks = await response.json();
        displayTasks(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function displayTasks(tasks) {
    const tbody = document.getElementById('tasksBody');
    tbody.innerHTML = '';
    
    tasks.forEach(task => {
        const row = tbody.insertRow();
        
        let statusButton = '';
        if (task.status === 'pending') {
            statusButton = `<button onclick="updateTaskStatus(${task.id}, 'start')">${task.status}</button>`;
        } else if (task.status === 'working') {
            statusButton = `<button onclick="updateTaskStatus(${task.id}, 'finish')">${task.status}</button>`;
        } else {
            statusButton = `<button disabled>${task.status}</button>`;
        }
        
        row.innerHTML = `
            <td><button onclick="editTask(${task.id}, '${task.title.replace(/'/g, "\\'")}', ${task.reward})">${task.id}</button></td>
            <td>${task.title}</td>
            <td>${task.reward}</td>
            <td>${statusButton}</td>
            <td>${new Date(task.created_at).toLocaleDateString()}</td>
            <td>
                <button onclick="deleteTask(${task.id})">Delete</button>
            </td>
        `;
    });
}

async function updateTaskStatus(taskId, action) {
    try {
        await fetch(`http://127.0.0.1:8000/tasks/${taskId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: action
            })
        });
        loadTasks();
    } catch (error) {
        console.error('Error updating task status:', error);
    }
}

async function downloadCSV() {
    try {
        const response = await fetch('http://127.0.0.1:8000/tasks/dump-csv');
        const csvData = await response.text();
        
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tasks.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error downloading CSV:', error);
    }
}

async function deleteTask(taskId) {
    try {
        await fetch(`http://127.0.0.1:8000/tasks/${taskId}`, {
            method: 'DELETE'
        });
        loadTasks();
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

document.getElementById('taskForm').addEventListener('submit', createTask);
document.getElementById('rewardForm').addEventListener('submit', updateReward);
loadReward();
loadTasks();