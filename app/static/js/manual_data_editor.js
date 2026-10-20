// Manual Data Editor JavaScript for KrckRP

class ManualDataEditor {
    constructor() {
        this.sessionId = null;
        this.campaignId = null;
        this.init();
    }

    init() {
        // Set up event listeners when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
            this.loadSessionStatus();
        });
        
        // Try to get campaign/session IDs from URL parameters or localStorage 
        const urlParams = new URLSearchParams(window.location.search);
        this.campaignId = urlParams.get('campaign_id') || localStorage.getItem('currentCampaignId');
        this.sessionId = urlParams.get('session_id') || localStorage.getItem('currentSessionId');
    }

    setupEventListeners() {
        // Session management buttons
        const startBtn = document.getElementById('startSessionBtn');
        const endBtn = document.getElementById('endSessionBtn');
        
        if (startBtn) startBtn.addEventListener('click', () => this.startSession());
        if (endBtn) endBtn.addEventListener('click', () => this.endSession());
        
        // Tool selection
        const toolSelect = document.getElementById('toolSelect');
        if (toolSelect) {
            toolSelect.addEventListener('change', () => this.updateToolParams());
        }
        
        // Execute button
        const executeBtn = document.getElementById('executeToolBtn');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => this.executeTool());
        }
    }

    async loadSessionStatus() {
        try {
            const response = await fetch('/api/session/status');
            const status = await response.json();
            
            // Update UI with session info
            const sessionStatusDiv = document.getElementById('sessionStatus');
            if (sessionStatusDiv) {
                sessionStatusDiv.innerHTML = `
                    <p><strong>Session ID:</strong> ${status.session_id || 'None'}</p>
                    <p><strong>Campaign ID:</strong> ${status.campaign_id || 'None'}</p>
                    <p><strong>Status:</strong> ${status.active_campaign ? 'Active' : 'Inactive'}</p>
                `;
            }
            
            // Store in localStorage for later use
            if (status.session_id) {
                this.sessionId = status.session_id;
                localStorage.setItem('currentSessionId', status.session_id);
            }
            if (status.campaign_id) {
                this.campaignId = status.campaign_id;
                localStorage.setItem('currentCampaignId', status.campaign_id);
            }
            
        } catch (error) {
            console.error('Error loading session status:', error);
            const sessionStatusDiv = document.getElementById('sessionStatus');
            if (sessionStatusDiv) {
                sessionStatusDiv.innerHTML = '<p>Error loading session status</p>';
            }
        }
    }

    async startSession() {
        try {
            // Get a new session ID from API or use existing
            if (!this.sessionId) {
                const response = await fetch('/api/sessions', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        campaign_id: this.campaignId,
                        name: "Manual Session",
                        description: "Session started via Manual Data Editor"
                    })
                });
                
                if (response.ok) {
                    const sessionData = await response.json();
                    this.sessionId = sessionData.id;
                    localStorage.setItem('currentSessionId', this.sessionId);
                } else {
                    throw new Error('Failed to create session');
                }
            }
            
            // Start the session
            const startResponse = await fetch(`/api/sessions/${this.sessionId}/start`, {
                method: 'POST'
            });
            
            if (startResponse.ok) {
                this.loadSessionStatus();
                this.showMessage('Session started successfully', 'success');
            } else {
                throw new Error('Failed to start session');
            }
        } catch (error) {
            console.error('Error starting session:', error);
            this.showMessage(`Error: ${error.message}`, 'error');
        }
    }

    async endSession() {
        try {
            if (!this.sessionId) {
                throw new Error('No active session to end');
            }
            
            // End the session
            const response = await fetch(`/api/sessions/${this.sessionId}/end`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.loadSessionStatus();
                this.showMessage('Session ended successfully', 'success');
            } else {
                throw new Error('Failed to end session');
            }
        } catch (error) {
            console.error('Error ending session:', error);
            this.showMessage(`Error: ${error.message}`, 'error');
        }
    }

    updateToolParams() {
        const toolSelect = document.getElementById('toolSelect');
        const toolParamsDiv = document.getElementById('toolParams');
        
        if (!toolParamsDiv || !toolSelect) return;
        
        const selectedTool = toolSelect.value;
        let paramsHTML = '';
        
        switch (selectedTool) {
            case 'move_character':
                paramsHTML = `
                    <div class="form-group">
                        <label for="characterId">Character ID:</label>
                        <input type="text" id="characterId" name="characterId" required>
                    </div>
                    <div class="form-group">
                        <label for="newLocationId">New Location ID:</label>
                        <input type="text" id="newLocationId" name="newLocationId" required>
                    </div>
                `;
                break;
            case 'set_stat':
                paramsHTML = `
                    <div class="form-group">
                        <label for="characterId">Character ID:</label>
                        <input type="text" id="characterId" name="characterId" required>
                    </div>
                    <div class="form-group">
                        <label for="statName">Stat Name:</label>
                        <input type="text" id="statName" name="statName" required placeholder="e.g., Strength, Dexterity...">
                    </div>
                    <div class="form-group">
                        <label for="newValue">New Value:</label>
                        <input type="number" id="newValue" name="newValue" required min="1" max="30">
                    </div>
                `;
                break;
            case 'give_item':
                paramsHTML = `
                    <div class="form-group">
                        <label for="characterId">Character ID:</label>
                        <input type="text" id="characterId" name="characterId" required>
                    </div>
                    <div class="form-group">
                        <label for="itemId">Item ID:</label>
                        <input type="text" id="itemId" name="itemId" required>
                    </div>
                `;
                break;
            case 'update_quest':
                paramsHTML = `
                    <div class="form-group">
                        <label for="questId">Quest ID:</label>
                        <input type="text" id="questId" name="questId" required>
                    </div>
                    <div class="form-group">
                        <label for="status">Status (optional):</label>
                        <select id="status" name="status">
                            <option value="">-- Select status --</option>
                            <option value="proposed">Proposed</option>
                            <option value="active">Active</option>
                            <option value="completed">Completed</option>
                            <option value="failed">Failed</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="progress">Progress (optional):</label>
                        <input type="number" id="progress" name="progress" min="0" max="100">
                    </div>
                `;
                break;
            default:
                paramsHTML = '<p>Select a tool to see parameters</p>';
        }
        
        toolParamsDiv.innerHTML = paramsHTML;
    }

    async executeTool() {
        const toolSelect = document.getElementById('toolSelect');
        if (!toolSelect) return;
        
        const selectedTool = toolSelect.value;
        if (!selectedTool) {
            this.showMessage('Please select a tool', 'error');
            return;
        }
        
        try {
            // Collect form data
            let params = {};
            
            switch (selectedTool) {
                case 'move_character':
                    params = {
                        character_id: document.getElementById('characterId').value,
                        new_location_id: document.getElementById('newLocationId').value
                    };
                    break;
                case 'set_stat':
                    params = {
                        character_id: document.getElementById('characterId').value,
                        stat_name: document.getElementById('statName').value,
                        new_value: parseInt(document.getElementById('newValue').value)
                    };
                    break;
                case 'give_item':
                    params = {
                        character_id: document.getElementById('characterId').value,
                        item_id: document.getElementById('itemId').value
                    };
                    break;
                case 'update_quest':
                    params = {
                        quest_id: document.getElementById('questId').value
                    };
                    const statusInput = document.getElementById('status');
                    const progressInput = document.getElementById('progress');
                    if (statusInput && statusInput.value) {
                        params.status = statusInput.value;
                    }
                    if (progressInput && progressInput.value) {
                        params.progress = parseInt(progressInput.value);
                    }
                    break;
            }
            
            // Execute the tool
            const response = await fetch(`/api/correction/${selectedTool}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    ...params
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.displayResult(result);
                this.showMessage('Tool executed successfully', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to execute tool');
            }
        } catch (error) {
            console.error('Error executing tool:', error);
            this.showMessage(`Error: ${error.message}`, 'error');
        }
    }

    displayResult(result) {
        const resultArea = document.getElementById('resultArea');
        if (!resultArea) return;
        
        let html = '<div class="result">';
        if (result.success) {
            html += `<h4 style="color: green;">Success!</h4>`;
            // Add more detailed success info
            Object.entries(result).forEach(([key, value]) => {
                if (key !== 'success') {
                    html += `<p><strong>${key}:</strong> ${value}</p>`;
                }
            });
        } else {
            html += `<h4 style="color: red;">Error!</h4>`;
            html += `<p>Error: ${result.error || 'Unknown error'}</p>`;
        }
        html += '</div>';
        
        resultArea.innerHTML = html;
    }

    showMessage(message, type) {
        const resultArea = document.getElementById('resultArea');
        if (!resultArea) return;
        
        let color = '';
        switch (type) {
            case 'success': 
                color = 'green';
                break;
            case 'error':
                color = 'red';
                break;
            default:
                color = 'black';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `<p style="color: ${color};">${message}</p>`;
        resultArea.appendChild(messageDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }
}

// Initialize the editor when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ManualDataEditor();
});