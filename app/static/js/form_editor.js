// Form Editor JavaScript for KrckRP World Editing

class FormEditor {
    constructor() {
        this.worldData = null;
        this.currentView = 'overview';
        this.init();
    }

    init() {
        // Load initial data if available
        this.loadWorldDataFromStorage();
        
        // Set up event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
            this.renderForm();
        });
    }

    loadWorldDataFromStorage() {
        const savedData = localStorage.getItem('worldEditorData');
        if (savedData) {
            try {
                this.worldData = JSON.parse(savedData);
            } catch (e) {
                console.error('Failed to parse world data:', e);
                this.worldData = null;
            }
        }
        
        // If no saved data, initialize with defaults
        if (!this.worldData) {
            this.worldData = {
                name: '',
                description: '',
                tone: { genre: '', mood: '', language_style: '' },
                factions: [],
                locations: [],
                characters: [],
                abilities: [],
                rules: {}
            };
        }
    }

    setupEventListeners() {
        // Save button
        const saveButton = document.getElementById('saveWorldBtn');
        if (saveButton) {
            saveButton.addEventListener('click', () => this.saveWorld());
        }

        // Add new entity buttons
        document.querySelectorAll('[data-add-entity]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const entityType = e.target.dataset.addEntity;
                this.addNewEntity(entityType);
            });
        });

        // Form field changes
        document.getElementById('worldForm').addEventListener('input', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                this.updateField(e.target.name, e.target.value);
            }
        });

        // Tabs navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                if (tab) {
                    this.switchTab(tab);
                }
            });
        });
    }

    updateField(fieldName, value) {
        // Split field name to handle nested objects
        const parts = fieldName.split('.');
        let current = this.worldData;
        
        for (let i = 0; i < parts.length - 1; i++) {
            if (!current[parts[i]]) {
                current[parts[i]] = {};
            }
            current = current[parts[i]];
        }
        
        // Set the final value
        current[parts[parts.length - 1]] = value;
        
        this.saveToStorage();
    }

    addNewEntity(entityType) {
        const entity = {
            id: Date.now().toString(), 
            name: '',
            description: ''
        };
        
        switch (entityType) {
            case 'faction':
                Object.assign(entity, { relations: [], alignment: '' });
                this.worldData.factions.push(entity);
                break;
            case 'location':
                Object.assign(entity, { connections: [], size: '' });
                this.worldData.locations.push(entity);
                break;
            case 'character':
                Object.assign(entity, { role: '', faction: '' });
                this.worldData.characters.push(entity);
                break;
            case 'ability':
                Object.assign(entity, { skinned_name: '' });
                this.worldData.abilities.push(entity);
                break;
        }
        
        this.renderForm();
        this.saveToStorage();
    }

    saveWorld() {
        // Save to localStorage or send to backend
        if (this.worldData) {
            this.saveToStorage();
            
            // Show success message
            const status = document.getElementById('statusMessage');
            if (status) {
                status.textContent = 'World saved successfully!';
                status.className = 'success';
                
                setTimeout(() => {
                    status.textContent = '';
                    status.className = '';
                }, 3000);
            }
        }
    }

    saveToStorage() {
        localStorage.setItem('worldEditorData', JSON.stringify(this.worldData));
    }

    switchTab(tabName) {
        this.currentView = tabName;
        
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Update visible content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = content.id === `tab-${tabName}` ? 'block' : 'none';
        });
    }

    renderForm() {
        const formContainer = document.getElementById('formEditor');
        if (!formContainer) return;

        // Render the overall world info
        const overviewHTML = `
            <div class="form-section">
                <h3>World Overview</h3>
                <div class="form-group">
                    <label for="name">World Name:</label>
                    <input type="text" id="name" name="name" value="${this.worldData.name || ''}">
                </div>
                <div class="form-group">
                    <label for="description">Description:</label>
                    <textarea id="description" name="description">${this.worldData.description || ''}</textarea>
                </div>
            </div>

            <div class="form-section">
                <h3>World Tone</h3>
                <div class="form-group">
                    <label for="tone.genre">Genre:</label>
                    <input type="text" id="tone.genre" name="tone.genre" value="${this.worldData.tone?.genre || ''}">
                </div>
                <div class="form-group">
                    <label for="tone.mood">Mood:</label>
                    <input type="text" id="tone.mood" name="tone.mood" value="${this.worldData.tone?.mood || ''}">
                </div>
                <div class="form-group">
                    <label for="tone.language_style">Language Style:</label>
                    <input type="text" id="tone.language_style" name="tone.language_style" value="${this.worldData.tone?.language_style || ''}">
                </div>
            </div>

            <div class="form-section">
                <h3>World Rules</h3>
                <!-- Add rules form fields as needed -->
            </div>
        `;

        // Render entities
        const renderEntities = (entities, type) => {
            return `
                ${entities.map((entity, index) => `
                    <div class="entity-item" data-entity-id="${entity.id}">
                        <h4>${type.charAt(0).toUpperCase() + type.slice(1)}: ${entity.name || 'Unnamed'}</h4>
                        <div class="form-group">
                            <label for="${type}_${index}_name">Name:</label>
                            <input type="text" id="${type}_${index}_name" name="${type}[${index}].name" value="${entity.name || ''}">
                        </div>
                        <div class="form-group">
                            <label for="${type}_${index}_description">Description:</label>
                            <textarea id="${type}_${index}_description" name="${type}[${index}].description">${entity.description || ''}</textarea>
                        </div>
                        ${type === 'faction' ? `
                            <div class="form-group">
                                <label for="${type}_${index}_relations">Relations (comma-separated):</label>
                                <input type="text" id="${type}_${index}_relations" name="${type}[${index}].relations" value="${entity.relations?.join(', ') || ''}">
                            </div>
                            <div class="form-group">
                                <label for="${type}_${index}_alignment">Alignment:</label>
                                <input type="text" id="${type}_${index}_alignment" name="${type}[${index}].alignment" value="${entity.alignment || ''}">
                            </div>
                        ` : ''}
                        ${type === 'location' ? `
                            <div class="form-group">
                                <label for="${type}_${index}_connections">Connections (comma-separated):</label>
                                <input type="text" id="${type}_${index}_connections" name="${type}[${index}].connections" value="${entity.connections?.join(', ') || ''}">
                            </div>
                            <div class="form-group">
                                <label for="${type}_${index}_size">Size:</label>
                                <select id="${type}_${index}_size" name="${type}[${index}].size">
                                    <option value="">Select...</option>
                                    <option value="small" ${entity.size === 'small' ? 'selected' : ''}>Small</option>
                                    <option value="medium" ${entity.size === 'medium' ? 'selected' : ''}>Medium</option>
                                    <option value="large" ${entity.size === 'large' ? 'selected' : ''}>Large</option>
                                </select>
                            </div>
                        ` : ''}
                        ${type === 'character' ? `
                            <div class="form-group">
                                <label for="${type}_${index}_role">Role:</label>
                                <input type="text" id="${type}_${index}_role" name="${type}[${index}].role" value="${entity.role || ''}">
                            </div>
                            <div class="form-group">
                                <label for="${type}_${index}_faction">Faction:</label>
                                <input type="text" id="${type}_${index}_faction" name="${type}[${index}].faction" value="${entity.faction || ''}">
                            </div>
                        ` : ''}
                        ${type === 'ability' ? `
                            <div class="form-group">
                                <label for="${type}_${index}_skinned_name">Skinned Name:</label>
                                <input type="text" id="${type}_${index}_skinned_name" name="${type}[${index}].skinned_name" value="${entity.skinned_name || ''}">
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            `;
        };

        const factionsHTML = renderEntities(this.worldData.factions, 'faction');
        const locationsHTML = renderEntities(this.worldData.locations, 'location');
        const charactersHTML = renderEntities(this.worldData.characters, 'character');
        const abilitiesHTML = renderEntities(this.worldData.abilities, 'ability');

        formContainer.innerHTML = `
            <div class="form-container">
                ${overviewHTML}
                
                <div class="tab-section">
                    <h3>Factions</h3>
                    <button type="button" data-add-entity="faction" class="btn btn-primary">Add Faction</button>
                    ${factionsHTML}
                </div>

                <div class="tab-section">
                    <h3>Locations</h3>
                    <button type="button" data-add-entity="location" class="btn btn-primary">Add Location</button>
                    ${locationsHTML}
                </div>

                <div class="tab-section">
                    <h3>Characters</h3>
                    <button type="button" data-add-entity="character" class="btn btn-primary">Add Character</button>
                    ${charactersHTML}
                </div>

                <div class="tab-section">
                    <h3>Abilities</h3>
                    <button type="button" data-add-entity="ability" class="btn btn-primary">Add Ability</button>
                    ${abilitiesHTML}
                </div>
                
                <div id="statusMessage"></div>
                <button id="saveWorldBtn" class="btn btn-success">Save World</button>
            </div>
        `;
    }
}

// Initialize the form editor when page loads
document.addEventListener('DOMContentLoaded', () => {
    const formEditor = new FormEditor();
});