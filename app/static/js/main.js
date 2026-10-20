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
        this.messagesContainer = document.getElementById('messages-container');
        this.sendBtn = document.getElementById('send-btn');
        this.messageInput = document.getElementById('message-input');
    }

    bindEvents() {
        this.newCampaignBtn.addEventListener('click', () => this.createCampaign());
        this.backToMenuBtn.addEventListener('click', () => this.showCampaignScreen());
        this.sendBtn.addEventListener('click', () => this.handleSend());
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
            console.log("Received campaign data:", campaigns);
            this.renderCampaignList(campaigns);
        } catch (error) {
            console.error('Error loading campaigns:', error);
            // Show user-friendly error message
            this.campaignList.innerHTML = '<p class="error">Failed to load campaigns. Please try again later.</p>';
        } finally {
            // Explicitly ensure the loading spinner is hidden
            setTimeout(() => this.showLoading(false), 0);
        }
    }

    renderCampaignList(campaigns) {
        if (!campaigns || campaigns.length === 0) {
            this.campaignList.innerHTML = '<p>No campaigns found. Create one to get started!</p>';
            // Even in empty case, ensure loading spinner is hidden
            setTimeout(() => this.showLoading(false), 0);
            return;
        }

        try {
            const htmlContent = campaigns.map(campaign => {
                // Safely handle missing or null fields with defaults
                const name = campaign.name || "Unnamed Campaign";
                const description = campaign.description || "No description available";
                
                return `
                    <div class="campaign-card" data-id="${campaign.id}">
                        <h3>${name}</h3>
                        <p>${description}</p>
                        <div class="campaign-meta">
                            <span>Created: ${new Date(campaign.created_at || new Date()).toLocaleDateString()}</span>
                            <span>Turns: 0</span>
                        </div>
                    </div>
                `;
            }).join('');
            
            this.campaignList.innerHTML = htmlContent;
            
            // Add click handlers to campaign cards
            document.querySelectorAll('.campaign-card').forEach(card => {
                card.addEventListener('click', () => this.selectCampaign(card.dataset.id));
            });
        } catch (error) {
            console.error('Error in renderCampaignList:', error);
            this.campaignList.innerHTML = '<p class="error">Failed to render campaigns. Please try again later.</p>';
            // Ensure loading spinner is hidden even if rendering fails
            setTimeout(() => this.showLoading(false), 0);
        }
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
            // If there's an error, we still want to hide the loader
            throw error; 
        }
    }

    renderCampaignState(stateData) {
        if (!stateData) return;
        
        this.sidebar.innerHTML = `
            <div class="campaign-info">
                <h2>${stateData.campaign_name || 'Unnamed Campaign'}</h2>
                <p>Turn: ${stateData.turn_count || 0}</p>
            </div>
        `;
    }

    async createCampaign() {
        const name = prompt('Enter campaign name:');
        if (!name) return;
        
        try {
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

    async handleSend() {
        if (!this.currentCampaignId || !this.messageInput.value.trim()) return;
        
        try {
            const response = await fetch(`/api/campaign/${this.currentCampaignId}/turn`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: this.messageInput.value,
                    context: "Game turn"
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.messagesContainer.innerHTML += `<div class="message">${data.response}</div>`;
            this.messageInput.value = '';
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    showCampaignScreen() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        this.campaignScreen.classList.remove('hidden');
        this.gameUi.classList.add('hidden');
        this.currentCampaignId = null;
        this.loadCampaigns(); // Reload campaigns when returning to menu
    }

    startSSE() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        this.eventSource = new EventSource(`/api/campaign/${this.currentCampaignId}/stream`);
        
        this.eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'error') {
                console.error('SSE Error:', data.message);
                return;
            }
            
            // Update UI with new state
            this.renderCampaignState(data.state);
        };
        
        this.eventSource.onerror = (error) => {
            console.error('SSE Connection error:', error);
            this.eventSource.close();
        };
    }
}