// Main game UI logic

class KrckRPGame {
    constructor() {
        this.currentCampaignId = null;
        this.eventSource = null;
        this.initializeElements();
        this.bindEvents();
        this.loadCampaigns();
    }

    initializeElements() {
        // Screen elements
        this.campaignScreen = document.getElementById('campaign-selection-screen');
        this.gameUi = document.getElementById('game-ui');
        this.loadingOverlay = document.getElementById('loading-overlay');

        // Campaign elements
        this.campaignList = document.getElementById('campaign-list');
        this.newCampaignBtn = document.getElementById('new-campaign-btn');

        // Game UI elements
        this.sidebar = document.getElementById('sidebar');
        this.backToMenuBtn = document.getElementById('back-to-menu-btn');
        this.campaignState = document.getElementById('campaign-state');
        this.messagesContainer = document.getElementById('messages-container');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');

        // State
        this.isTyping = false;
    }

    bindEvents() {
        // Campaign events
        this.newCampaignBtn.addEventListener('click', () => this.createNewCampaign());

        // Game UI events
        this.backToMenuBtn.addEventListener('click', () => this.showCampaignScreen());
        this.sendBtn.addEventListener('click', () => this.handleSend());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });
    }

    showLoading(show = true) {
        this.loadingOverlay.classList.toggle('hidden', !show);
    }

    async loadCampaigns() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/campaigns');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const campaigns = await response.json();
            this.renderCampaignList(campaigns);
        } catch (error) {
            console.error('Error loading campaigns:', error);
            // In a real app, we might show an error message
        } finally {
            this.showLoading(false);
        }
    }

    renderCampaignList(campaigns) {
        if (!campaigns || campaigns.length === 0) {
            this.campaignList.innerHTML = '<p>No campaigns found. Create one to get started!</p>';
            return;
        }

        this.campaignList.innerHTML = campaigns.map(campaign => `
            <div class="campaign-card" data-id="${campaign.id}">
                <h3>${campaign.name}</h3>
                <p>${campaign.description}</p>
                <div class="campaign-meta">
                    <span>Created: ${new Date(campaign.created_at).toLocaleDateString()}</span>
                    <span>Turns: ${campaign.turn_count || 0}</span>
                </div>
            </div>
        `).join('');

        // Add click handlers to campaign cards
        document.querySelectorAll('.campaign-card').forEach(card => {
            card.addEventListener('click', () => this.selectCampaign(card.dataset.id));
        });
    }

    async selectCampaign(campaignId) {
        this.currentCampaignId = campaignId;
        
        try {
            this.showLoading(true);
            
            // Load campaign state
            await this.loadCampaignState();
            
            // Show game UI and hide campaign screen
            this.campaignScreen.classList.add('hidden');
            this.gameUi.classList.remove('hidden');
            
            // Start listening to SSE for updates
            this.startSSE();
        } catch (error) {
            console.error('Error selecting campaign:', error);
            this.showLoading(false);
        }
    }

    async loadCampaignState() {
        try {
            const response = await fetch(`/api/campaign/${this.currentCampaignId}/state`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const stateData = await response.json();
            this.renderCampaignState(stateData);
        } catch (error) {
            console.error('Error loading campaign state:', error);
            // In a real app, we might show an error message
        }
    }

    renderCampaignState(stateData) {
        if (!stateData) return;

        const location = stateData.location || { name: 'Unknown Location', description: '' };
        const characters = stateData.characters || [];
        const quests = stateData.quests || [];

        this.campaignState.innerHTML = `
            <div class="campaign-info">
                <h3>${stateData.name}</h3>
                <p><strong>Location:</strong> ${location.name}</p>
                <p>${location.description}</p>
                
                <h4>Stats</h4>
                <ul>
                    ${Object.entries(stateData.stats || {}).map(([key, value]) => 
                        `<li><strong>${this.formatStatName(key)}:</strong> ${value}</li>`
                    ).join('')}
                </ul>

                <h4>Inventory</h4>
                <ul>
                    ${stateData.inventory?.length ? stateData.inventory.map(item => 
                        `<li>${item.name}${item.description ? ` - ${item.description}` : ''}</li>`
                    ).join('') : '<li>No items</li>'}
                </ul>

                <h4>Active Quests (${quests.length})</h4>
                <ul>
                    ${quests.map(quest => 
                        `<li><strong>${quest.name}</strong>: ${quest.description}</li>`
                    ).join('')}
                </ul>

                <h4>Nearby Characters (${characters.length})</h4>
                <ul>
                    ${characters.map(char => 
                        `<li>${char.name}${char.description ? ` - ${char.description}` : ''}</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }

    formatStatName(statKey) {
        // Convert camelCase to title case for display
        return statKey.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    }

    async createNewCampaign() {
        try {
            const name = prompt('Enter campaign name:');
            if (!name) return;

            const response = await fetch('/api/campaigns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name, description: `Campaign created on ${new Date().toLocaleDateString()}` })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const campaign = await response.json();
            this.selectCampaign(campaign.id);
        } catch (error) {
            console.error('Error creating campaign:', error);
            alert('Failed to create campaign');
        }
    }

    startSSE() {
        // Close existing connection if any
        if (this.eventSource) {
            this.eventSource.close();
        }

        const eventSourceUrl = `/api/turn/stream`;
        
        this.eventSource = new EventSource(eventSourceUrl);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                switch(data.type) {
                    case 'narration':
                        this.addMessage('narrator', data.chunk);
                        break;
                    case 'extraction':
                        // This is where we would process extracted data
                        console.log('Extracted data:', data.data);
                        break;
                    case 'commit':
                        // Turn committed successfully 
                        console.log('Turn committed');
                        break;
                }
            } catch (error) {
                console.error('Error parsing SSE message:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE Error:', error);
            this.eventSource.close();
        };
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = text;
        
        // Remove typing indicator if it exists
        const existingIndicator = this.typingIndicator;
        if (!existingIndicator.classList.contains('hidden')) {
            existingIndicator.classList.add('hidden');
        }
        
        // Add the new message to container
        this.messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async handleSend() {
        const message = this.userInput.value.trim();
        if (!message || !this.currentCampaignId) return;

        try {
            // Add user message immediately
            this.addMessage('player', message);
            
            // Clear input and show typing indicator
            this.userInput.value = '';
            this.typingIndicator.classList.remove('hidden');
            
            const response = await fetch('/api/turn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: message,
                    campaign_id: this.currentCampaignId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Turn processed:', result);
        } catch (error) {
            console.error('Error sending message:', error);
            this.typingIndicator.classList.add('hidden');
            alert('Failed to process action. Please try again.');
        }
    }

    showCampaignScreen() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        this.gameUi.classList.add('hidden');
        this.campaignScreen.classList.remove('hidden');
        this.currentCampaignId = null;
    }
}

// Initialize the game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.game = new KrckRPGame();
});