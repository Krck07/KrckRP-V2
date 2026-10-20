// Character Creator JavaScript for KrckRP

class CharacterCreator {
    constructor() {
        this.characterData = {
            name: '',
            description: '',
            stats: {},
            inventory: [],
            abilities: []
        };
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
            this.renderForm();
        });
    }

    setupEventListeners() {
        // Form submission
        const form = document.getElementById('characterForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitCharacter();
            });
        }

        // Add inventory item
        const addInventoryBtn = document.getElementById('addInventoryItem');
        if (addInventoryBtn) {
            addInventoryBtn.addEventListener('click', () => this.addInventoryItem());
        }

        // Add ability
        const addAbilityBtn = document.getElementById('addAbility');
        if (addAbilityBtn) {
            addAbilityBtn.addEventListener('click', () => this.addAbility());
        }

        // Form field changes
        document.querySelectorAll('[name]').forEach(field => {
            field.addEventListener('input', (e) => {
                this.updateField(e.target.name, e.target.value);
            });
        });

        // Stats input
        document.querySelectorAll('.stat-input').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateStat(e.target.dataset.stat, parseInt(e.target.value));
            });
        });
    }

    updateField(fieldName, value) {
        const parts = fieldName.split('.');
        let current = this.characterData;
        
        for (let i = 0; i < parts.length - 1; i++) {
            if (!current[parts[i]]) {
                current[parts[i]] = {};
            }
            current = current[parts[i]];
        }
        
        // Set the final value
        current[parts[parts.length - 1]] = value;
    }

    updateStat(statName, value) {
        this.characterData.stats[statName] = value;
    }

    addInventoryItem() {
        const itemsContainer = document.getElementById('inventoryItems');
        if (!itemsContainer) return;

        const itemIndex = this.characterData.inventory.length;
        const newItemDiv = document.createElement('div');
        newItemDiv.className = 'inventory-item';
        newItemDiv.innerHTML = `
            <h4>Item ${itemIndex + 1}</h4>
            <div class="form-group">
                <label for="inventory[${itemIndex}].name">Name:</label>
                <input type="text" id="inventory[${itemIndex}].name" name="inventory[${itemIndex}].name" required>
            </div>
            <div class="form-group">
                <label for="inventory[${itemIndex}].description">Description:</label>
                <textarea id="inventory[${itemIndex}].description" name="inventory[${itemIndex}].description"></textarea>
            </div>
        `;
        
        itemsContainer.appendChild(newItemDiv);
    }

    addAbility() {
        const abilitiesContainer = document.getElementById('abilitiesList');
        if (!abilitiesContainer) return;

        const abilityIndex = this.characterData.abilities.length;
        const newAbilityDiv = document.createElement('div');
        newAbilityDiv.className = 'ability-item';
        newAbilityDiv.innerHTML = `
            <h4>Ability ${abilityIndex + 1}</h4>
            <div class="form-group">
                <label for="abilities[${abilityIndex}].name">Name:</label>
                <input type="text" id="abilities[${abilityIndex}].name" name="abilities[${abilityIndex}].name" required>
            </div>
            <div class="form-group">
                <label for="abilities[${abilityIndex}].description">Description:</label>
                <textarea id="abilities[${abilityIndex}].description" name="abilities[${abilityIndex}].description"></textarea>
            </div>
        `;
        
        abilitiesContainer.appendChild(newAbilityDiv);
    }

    submitCharacter() {
        // Get form data
        const formData = new FormData(document.getElementById('characterForm'));
        const characterData = Object.fromEntries(formData.entries());
        
        // Process the form to extract structured data
        const processedData = this.processFormData(characterData);
        
        // Save or send to backend (in a real app, we would submit via fetch)
        console.log('Character Data:', processedData);
        
        alert('Character created successfully! In a real application, this would be sent to the server.');
    }

    processFormData(formData) {
        // This is where you'd extract structured data from form fields
        return {
            name: formData.name || '',
            description: formData.description || '',
            stats: {  // Default stats, could come from world rules
                strength: parseInt(formData.strength) || 10,
                dexterity: parseInt(formData.dexterity) || 10,
                constitution: parseInt(formData.constitution) || 10,
                intelligence: parseInt(formData.intelligence) || 10,
                wisdom: parseInt(formData.wisdom) || 10,
                charisma: parseInt(formData.charisma) || 10
            },
            inventory: this.characterData.inventory,
            abilities: this.characterData.abilities,
            campaign_id: formData.campaign_id || null  // This would be set by the UI
        };
    }

    renderForm() {
        const formContainer = document.getElementById('characterCreator');
        if (!formContainer) return;

        formContainer.innerHTML = `
            <div class="form-container">
                <h2>Create Character</h2>
                
                <form id="characterForm">
                    <div class="form-section">
                        <h3>Basic Information</h3>
                        
                        <div class="form-group">
                            <label for="name">Character Name:</label>
                            <input type="text" id="name" name="name" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="description">Description:</label>
                            <textarea id="description" name="description"></textarea>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Character Stats</h3>
                        
                        <div class="stats-container">
                            <div class="stat-group">
                                <label for="strength">Strength:</label>
                                <input type="number" id="strength" name="strength" class="stat-input" data-stat="strength" min="1" max="20" value="10">
                            </div>
                            
                            <div class="stat-group">
                                <label for="dexterity">Dexterity:</label>
                                <input type="number" id="dexterity" name="dexterity" class="stat-input" data-stat="dexterity" min="1" max="20" value="10">
                            </div>
                            
                            <div class="stat-group">
                                <label for="constitution">Constitution:</label>
                                <input type="number" id="constitution" name="constitution" class="stat-input" data-stat="constitution" min="1" max="20" value="10">
                            </div>
                            
                            <div class="stat-group">
                                <label for="intelligence">Intelligence:</label>
                                <input type="number" id="intelligence" name="intelligence" class="stat-input" data-stat="intelligence" min="1" max="20" value="10">
                            </div>
                            
                            <div class="stat-group">
                                <label for="wisdom">Wisdom:</label>
                                <input type="number" id="wisdom" name="wisdom" class="stat-input" data-stat="wisdom" min="1" max="20" value="10">
                            </div>
                            
                            <div class="stat-group">
                                <label for="charisma">Charisma:</label>
                                <input type="number" id="charisma" name="charisma" class="stat-input" data-stat="charisma" min="1" max="20" value="10">
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Inventory</h3>
                        
                        <div id="inventoryItems">
                            <!-- Inventory items will be added here dynamically -->
                        </div>
                        
                        <button type="button" id="addInventoryItem" class="btn btn-secondary">Add Item</button>
                    </div>

                    <div class="form-section">
                        <h3>Abilities</h3>
                        
                        <div id="abilitiesList">
                            <!-- Abilities will be added here dynamically -->
                        </div>
                        
                        <button type="button" id="addAbility" class="btn btn-secondary">Add Ability</button>
                    </div>

                    <input type="hidden" name="campaign_id" value="${this.getCampaignId()}">

                    <button type="submit" class="btn btn-primary">Create Character</button>
                </form>
            </div>
        `;
    }

    getCampaignId() {
        // In a real application, this would be retrieved from the URL or session
        return localStorage.getItem('currentCampaignId') || 'default-campaign';
    }
}

// Initialize the character creator when page loads
document.addEventListener('DOMContentLoaded', () => {
    const charCreator = new CharacterCreator();
});