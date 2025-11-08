// Character Sheet JavaScript - Alpine.js Components

// Main character sheet component
function characterSheet(characterId) {
    return {
        characterId: characterId,
        characterName: '',
        saveStatus: '', // '', 'saving', 'saved', 'error'
        data: {
            // Chronicle Information
            name: '',
            chronicle: '',
            concept: '',
            predator: '',
            ambition: '',
            desire: '',
            
            // Appearance & Identity
            apparent_age: '',
            true_age: '',
            date_of_birth: '',
            date_of_death: '',
            appearance: '',
            distinguishing_features: '',
            pronouns: '',
            ethnicity: '',
            languages: '',
            birthplace: '',
            
            // Attributes (1-5)
            strength: 1,
            dexterity: 1,
            stamina: 1,
            charisma: 1,
            manipulation: 1,
            composure: 1,
            intelligence: 1,
            wits: 1,
            resolve: 1,
            
            // Identity
            clan: '',
            sire: '',
            generation: 13,
            bane_type: '',
            compulsion: '',
            
            // Portrait
            portrait_url: '',
            
            // Experience
            exp_total: 0,
            exp_spent: 0,
            exp_available: 0,
            
            // Chronicle Tenets
            chronicle_tenets: '',
            
            // History
            history_in_life: '',
            after_death: '',
            notes: ''
        },
        
        // Touchstones (1-3)
        touchstones: [],
        
        // Initialize component
        init() {
            if (this.characterId) {
                this.loadCharacter();
            } else {
                // New character - initialize with one empty touchstone
                this.touchstones.push({
                    name: '',
                    description: '',
                    conviction: ''
                });
            }
        },
        
        // Load character data from server
        async loadCharacter() {
            try {
                const response = await fetch(`/vtm/api/character/${this.characterId}`);
                if (response.ok) {
                    const character = await response.json();
                    this.data = { ...this.data, ...character };
                    this.characterName = character.name || 'Unnamed';
                    
                    // Load touchstones
                    this.touchstones = [];
                    for (let i = 1; i <= 3; i++) {
                        const name = character[`touchstone_${i}_name`];
                        if (name) {
                            this.touchstones.push({
                                name: name,
                                description: character[`touchstone_${i}_description`] || '',
                                conviction: character[`touchstone_${i}_conviction`] || ''
                            });
                        }
                    }
                    
                    // If no touchstones, add one empty
                    if (this.touchstones.length === 0) {
                        this.touchstones.push({ name: '', description: '', conviction: '' });
                    }
                }
            } catch (error) {
                console.error('Error loading character:', error);
            }
        },
        
        // Auto-save function with debouncing handled by Alpine @input.debounce
        async autoSave() {
            if (!this.characterId) {
                // New character - need to create first
                await this.createCharacter();
                return;
            }
            
            this.saveStatus = 'saving';
            
            try {
                // Prepare data with touchstones
                const saveData = { ...this.data };
                
                // Add touchstones to save data
                for (let i = 0; i < 3; i++) {
                    const index = i + 1;
                    if (i < this.touchstones.length) {
                        saveData[`touchstone_${index}_name`] = this.touchstones[i].name;
                        saveData[`touchstone_${index}_description`] = this.touchstones[i].description;
                        saveData[`touchstone_${index}_conviction`] = this.touchstones[i].conviction;
                    } else {
                        saveData[`touchstone_${index}_name`] = '';
                        saveData[`touchstone_${index}_description`] = '';
                        saveData[`touchstone_${index}_conviction`] = '';
                    }
                }
                
                const response = await fetch(`/vtm/character/${this.characterId}/update`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(saveData)
                });
                
                if (response.ok) {
                    this.saveStatus = 'saved';
                    this.characterName = this.data.name || 'Unnamed';
                    setTimeout(() => this.saveStatus = '', 2000);
                } else {
                    this.saveStatus = 'error';
                }
            } catch (error) {
                console.error('Save error:', error);
                this.saveStatus = 'error';
            }
        },
        
        // Create new character
        async createCharacter() {
            try {
                const response = await fetch('/vtm/character/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.data)
                });
                
                if (response.ok) {
                    // Get the new character ID and redirect
                    const result = await response.json();
                    window.location.href = `/vtm/character/${result.id}/edit`;
                } else {
                    const error = await response.json();
                    alert(error.error || 'Failed to create character');
                }
            } catch (error) {
                console.error('Create error:', error);
                alert('Failed to create character');
            }
        },
        
        // Update clan badge when clan changes
        updateClanBadge() {
            // Badge updates automatically via Alpine binding
            // This function exists for future enhancements
        },
        
        // Get clan discipline icons
        getClanDisciplineIcons() {
            const clanDisciplines = {
                'brujah': ['potence', 'presence', 'celerity'],
                'gangrel': ['animalism', 'fortitude', 'protean'],
                'malkavian': ['auspex', 'dominate', 'obfuscate'],
                'nosferatu': ['animalism', 'obfuscate', 'potence'],
                'toreador': ['auspex', 'celerity', 'presence'],
                'tremere': ['auspex', 'blood-sorcery', 'dominate'],
                'ventrue': ['dominate', 'fortitude', 'presence'],
                'banu-haqim': ['blood-sorcery', 'celerity', 'obfuscate'],
                'hecata': ['auspex', 'fortitude', 'oblivion'],
                'lasombra': ['dominate', 'oblivion', 'potence'],
                'ministry': ['obfuscate', 'presence', 'protean'],
                'ravnos': ['animalism', 'obfuscate', 'presence'],
                'salubri': ['auspex', 'dominate', 'fortitude'],
                'tzimisce': ['animalism', 'dominate', 'protean'],
                'caitiff': [], // No clan disciplines
                'thin-blood': [] // No clan disciplines
            };
            
            const disciplines = clanDisciplines[this.data.clan] || [];
            if (disciplines.length === 0) return '<span class="no-disciplines">No clan disciplines</span>';
            
            return disciplines.map(disc => 
                `<img src="/static/images/disciplines/${disc}.png" 
                      alt="${disc}" 
                      title="${disc.replace('-', ' ')}"
                      class="discipline-icon">`
            ).join('');
        },
        
        // Touchstone management
        addTouchstone() {
            if (this.touchstones.length < 3) {
                this.touchstones.push({
                    name: '',
                    description: '',
                    conviction: ''
                });
            }
        },
        
        removeTouchstone(index) {
            this.touchstones.splice(index, 1);
            // Ensure at least 1 touchstone
            if (this.touchstones.length === 0) {
                this.touchstones.push({ name: '', description: '', conviction: '' });
            }
            this.autoSave();
        },
        
        // Portrait upload
        async uploadPortrait(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch(`/vtm/character/${this.characterId}/upload-portrait`, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.data.portrait_url = data.portrait_url;
                }
            } catch (error) {
                console.error('Portrait upload error:', error);
            }
        },
        
        // XP Management
        addXP() {
            const amount = prompt('How much XP to add?');
            if (amount && !isNaN(amount)) {
                this.data.exp_total += parseInt(amount);
                this.data.exp_available = this.data.exp_total - this.data.exp_spent;
                this.autoSave();
            }
        },
        
        spendXP() {
            const amount = prompt('How much XP to spend?');
            if (amount && !isNaN(amount)) {
                const spend = parseInt(amount);
                if (spend <= this.data.exp_available) {
                    this.data.exp_spent += spend;
                    this.data.exp_available = this.data.exp_total - this.data.exp_spent;
                    this.autoSave();
                } else {
                    alert('Not enough available XP!');
                }
            }
        }
    }
}

// Dot tracker component (reusable for attributes, skills, disciplines)
function dotTracker(field, initialValue = 0, min = 0, max = 5) {
    return {
        field: field,
        value: initialValue,
        min: min,
        max: max,
        
        init() {
            // Watch for changes from parent component
            this.$watch(`$parent.data.${field}`, value => {
                this.value = value;
            });
        },
        
        handleClick(event) {
            // Get clicked dot index (1-based)
            const dots = event.currentTarget.querySelectorAll('.dot');
            const clickedDot = event.target.closest('.dot');
            if (!clickedDot) return;
            
            const clickedIndex = Array.from(dots).indexOf(clickedDot) + 1;
            
            // If clicking on filled dot, decrease
            // If clicking on empty dot, increase to that level
            if (clickedIndex <= this.value) {
                // Clicking filled dot - decrease (but not below min)
                this.value = Math.max(clickedIndex - 1, this.min);
            } else {
                // Clicking empty dot - increase to that level
                this.value = clickedIndex;
            }
            
            // Update parent data
            this.$parent.data[this.field] = this.value;
            
            // Trigger auto-save
            this.$parent.autoSave();
        }
    }
}

// Make components globally available
window.characterSheet = characterSheet;
window.dotTracker = dotTracker;
