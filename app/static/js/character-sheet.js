// Character Sheet JavaScript - Alpine.js Components
// SIMPLIFIED VERSION - All logic in main component

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
            
            // Skills (0-5)
            athletics: 0,
            brawl: 0,
            craft: 0,
            drive: 0,
            firearms: 0,
            larceny: 0,
            melee: 0,
            stealth: 0,
            survival: 0,
            animal_ken: 0,
            etiquette: 0,
            insight: 0,
            intimidation: 0,
            leadership: 0,
            performance: 0,
            persuasion: 0,
            streetwise: 0,
            subterfuge: 0,
            academics: 0,
            awareness: 0,
            finance: 0,
            investigation: 0,
            medicine: 0,
            occult: 0,
            politics: 0,
            science: 0,
            technology: 0,
            
            // Skill specialties (stored as string)
            skill_specialties: '',
            
            // Hunger (0-5)
            hunger: 1,
            resonance: '',
            
            // Blood Potency (0-10)
            blood_potency: 0,
            
            // Attributes
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
            
            // Portraits (6 slots)
            portrait_face: '',
            portrait_body: '',
            portrait_hobby_1: '',
            portrait_hobby_2: '',
            portrait_hobby_3: '',
            portrait_hobby_4: '',
            alias: 'Alias',
            
            // Keep old portrait_url for backwards compatibility
            portrait_url: '',
            
            // Experience
            exp_total: 0,
            exp_spent: 0,
            exp_available: 0,
            
            // Health & Willpower tracking
            health_max: 6,
            health_superficial: 0,
            health_aggravated: 0,
            willpower_max: 5,
            willpower_superficial: 0,
            willpower_aggravated: 0,
            humanity_current: 7,
            humanity_stained: 0,
            
            // Disciplines (5 slots)
            discipline_1_name: '',
            discipline_1_level: 0,
            discipline_1_powers: '',
            discipline_1_description: '',
            discipline_2_name: '',
            discipline_2_level: 0,
            discipline_2_powers: '',
            discipline_2_description: '',
            discipline_3_name: '',
            discipline_3_level: 0,
            discipline_3_powers: '',
            discipline_3_description: '',
            discipline_4_name: '',
            discipline_4_level: 0,
            discipline_4_powers: '',
            discipline_4_description: '',
            discipline_5_name: '',
            discipline_5_level: 0,
            discipline_5_powers: '',
            discipline_5_description: '',
            
            // Chronicle Tenets (5 individual fields)
            chronicle_tenet_1: '',
            chronicle_tenet_2: '',
            chronicle_tenet_3: '',
            chronicle_tenet_4: '',
            chronicle_tenet_5: '',
            
            // Keep old chronicle_tenets for backwards compatibility
            chronicle_tenets: '',
            
            // Column width preferences (percentages)
            column_widths_above: '30,35,35', // column1,column2,column3 percentages
            column_widths_below: '33,33,34', // default equal split
            
            // History
            history_in_life: '',
            after_death: '',
            notes: ''
        },
        
        // Touchstones (1-3)
        touchstones: [],
        
        // XP Log
        xpLog: [],
        
        // Blood Potency calculated values
        bloodPotencyValues: {
            surge: 1,
            mend: 1,
            powerBonus: 0,
            rouseReroll: 0,
            feedingPenalty: 'No penalty',
            baneSeverity: 0
        },
        
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
            
            // Initialize Blood Potency values
            this.updateBloodPotency(this.data.blood_potency || 0);
            
            // Wait for DOM to be ready, then initialize resizable dividers
            this.$nextTick(() => {
                this.initResizableDividers();
            });
        },
        
        // Load character data from server
        async loadCharacter() {
            try {
                const response = await fetch(`/vtm/api/character/${this.characterId}`);
                if (response.ok) {
                    const character = await response.json();
                    
                    // Update all data fields
                    Object.keys(this.data).forEach(key => {
                        if (character[key] !== undefined && character[key] !== null) {
                            this.data[key] = character[key];
                        }
                    });
                    
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
                    
                    console.log('Character loaded:', this.data);
                }
            } catch (error) {
                console.error('Error loading character:', error);
            }
        },
        
        // Auto-save function
        async autoSave() {
            if (!this.characterId) {
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
                
                console.log('Saving data:', saveData);
                
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
                    console.error('Save failed:', await response.text());
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
            this.autoSave();
        },
        
        // Update Blood Potency calculated values
        updateBloodPotency(bp) {
            const bpTable = {
                0: { surge: 1, mend: 1, powerBonus: 0, rouseReroll: 0, feedingPenalty: 'No penalty', baneSeverity: 0 },
                1: { surge: 2, mend: 1, powerBonus: 0, rouseReroll: 0, feedingPenalty: 'Animal/Bagged', baneSeverity: 1 },
                2: { surge: 2, mend: 2, powerBonus: 1, rouseReroll: 0, feedingPenalty: 'Animal/Bagged', baneSeverity: 1 },
                3: { surge: 3, mend: 2, powerBonus: 1, rouseReroll: 1, feedingPenalty: 'Cold blood', baneSeverity: 2 },
                4: { surge: 3, mend: 3, powerBonus: 2, rouseReroll: 1, feedingPenalty: 'Cold blood', baneSeverity: 2 },
                5: { surge: 4, mend: 3, powerBonus: 2, rouseReroll: 2, feedingPenalty: 'Resonance only', baneSeverity: 3 },
                6: { surge: 4, mend: 3, powerBonus: 3, rouseReroll: 2, feedingPenalty: 'Resonance only', baneSeverity: 3 },
                7: { surge: 5, mend: 3, powerBonus: 3, rouseReroll: 3, feedingPenalty: 'Slake 1 only', baneSeverity: 4 },
                8: { surge: 5, mend: 4, powerBonus: 4, rouseReroll: 3, feedingPenalty: 'Slake 1 only', baneSeverity: 4 },
                9: { surge: 6, mend: 4, powerBonus: 4, rouseReroll: 4, feedingPenalty: 'Slake 1 only', baneSeverity: 5 },
                10: { surge: 6, mend: 5, powerBonus: 5, rouseReroll: 4, feedingPenalty: 'Slake 0 only', baneSeverity: 5 }
            };
            this.bloodPotencyValues = bpTable[bp] || bpTable[0];
        },
        
        // DOT TRACKER METHODS
        clickDot(field, clickedValue, min = 0, max = 5) {
            const currentValue = this.data[field] || min;
            
            if (clickedValue <= currentValue) {
                // Clicking filled dot - decrease (but not below min)
                this.data[field] = Math.max(clickedValue - 1, min);
            } else {
                // Clicking empty dot - increase to that level
                this.data[field] = clickedValue;
            }
            
            // Special handling for Blood Potency
            if (field === 'blood_potency') {
                this.updateBloodPotency(this.data[field]);
            }
            
            this.autoSave();
        },
        
        // HEALTH/WILLPOWER/HUMANITY METHODS
        getHealthState(index) {
            const max = this.data.health_max || 6;
            const superficial = this.data.health_superficial || 0;
            const aggravated = this.data.health_aggravated || 0;
            
            if (index > 10) return 'empty';
            
            const usableBoxes = max - superficial - aggravated;
            
            if (index <= usableBoxes) return 'filled';
            if (index <= max - aggravated) return 'superficial';
            if (index <= max) return 'aggravated';
            return 'empty';
        },
        
        cycleHealth(index) {
            const state = this.getHealthState(index);
            const max = this.data.health_max || 6;
            
            if (state === 'empty' && index <= 10) {
                // Extend max
                this.data.health_max = index;
            } else if (state === 'filled') {
                // Add superficial
                if ((this.data.health_superficial + this.data.health_aggravated) < max) {
                    this.data.health_superficial++;
                }
            } else if (state === 'superficial') {
                // Convert to aggravated
                this.data.health_superficial--;
                this.data.health_aggravated++;
            } else if (state === 'aggravated') {
                // Remove damage
                this.data.health_aggravated--;
            }
            
            this.autoSave();
        },
        
        getWillpowerState(index) {
            const max = this.data.willpower_max || 5;
            const superficial = this.data.willpower_superficial || 0;
            const aggravated = this.data.willpower_aggravated || 0;
            
            if (index > 10) return 'empty';
            
            const usableBoxes = max - superficial - aggravated;
            
            if (index <= usableBoxes) return 'filled';
            if (index <= max - aggravated) return 'superficial';
            if (index <= max) return 'aggravated';
            return 'empty';
        },
        
        cycleWillpower(index) {
            const state = this.getWillpowerState(index);
            const max = this.data.willpower_max || 5;
            
            if (state === 'empty' && index <= 10) {
                // Extend max
                this.data.willpower_max = index;
            } else if (state === 'filled') {
                // Add superficial
                if ((this.data.willpower_superficial + this.data.willpower_aggravated) < max) {
                    this.data.willpower_superficial++;
                }
            } else if (state === 'superficial') {
                // Convert to aggravated
                this.data.willpower_superficial--;
                this.data.willpower_aggravated++;
            } else if (state === 'aggravated') {
                // Remove damage
                this.data.willpower_aggravated--;
            }
            
            this.autoSave();
        },
        
        getHumanityState(index) {
            const current = this.data.humanity_current || 7;
            const stained = this.data.humanity_stained || 0;
            
            if (index <= current - stained) return 'filled';
            if (index <= current) return 'stained';
            return 'empty';
        },
        
        clickHumanity(index) {
            const current = this.data.humanity_current || 7;
            
            if (index === current) {
                // Clicking current humanity - decrease it
                this.data.humanity_current = Math.max(index - 1, 0);
            } else if (index < current) {
                // Clicking below current - add stain
                const stainedCount = current - index;
                this.data.humanity_stained = stainedCount;
            } else {
                // Clicking above current - increase humanity
                this.data.humanity_current = index;
                this.data.humanity_stained = 0;
            }
            
            this.autoSave();
        },
        
        // SKILL SPECIALTIES
        getSpecialties(skill) {
            if (!this.data.skill_specialties) return [];
            const specs = this.data.skill_specialties.split(',').filter(s => s.trim());
            return specs.filter(s => s.startsWith(skill + ':')).map(s => s.split(':')[1]);
        },
        
        addSpecialty(skill) {
            const skillValue = this.data[skill] || 0;
            if (skillValue === 0) {
                alert('Add dots to the skill first!');
                return;
            }
            
            const currentSpecs = this.getSpecialties(skill);
            if (currentSpecs.length >= skillValue) {
                alert(`Maximum ${skillValue} specialties for this skill!`);
                return;
            }
            
            const spec = prompt(`Add specialty for ${this.capitalize(skill)}:`);
            if (spec && spec.trim()) {
                let allSpecs = [];
                if (this.data.skill_specialties) {
                    allSpecs = this.data.skill_specialties.split(',').filter(s => s.trim());
                }
                allSpecs.push(`${skill}:${spec.trim()}`);
                this.data.skill_specialties = allSpecs.join(',');
                this.autoSave();
            }
        },
        
        removeSpecialty(skill, specialty) {
            let allSpecs = this.data.skill_specialties.split(',').filter(s => s.trim());
            allSpecs = allSpecs.filter(s => s !== `${skill}:${specialty}`);
            this.data.skill_specialties = allSpecs.join(',');
            this.autoSave();
        },
        
        // HELPER METHODS
        capitalize(str) {
            return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },
        
        getGenerationOrdinal(gen) {
            const num = parseInt(gen) || 13;
            const lastDigit = num % 10;
            const lastTwoDigits = num % 100;
            
            if (lastTwoDigits >= 11 && lastTwoDigits <= 13) {
                return num + 'th';
            }
            
            switch(lastDigit) {
                case 1: return num + 'st';
                case 2: return num + 'nd';
                case 3: return num + 'rd';
                default: return num + 'th';
            }
        },
        
        getCharacterTitle() {
            const name = this.data.name || 'Unnamed';
            const gen = this.getGenerationOrdinal(this.data.generation);
            const clan = this.capitalize(this.data.clan || 'Caitiff');
            return `${name} the ${gen} Generation ${clan}`;
        },
        
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
                'caitiff': [],
                'thin-blood': []
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
        
        // TOUCHSTONE MANAGEMENT
        addTouchstone() {
            if (this.touchstones.length < 3) {
                this.touchstones.push({ name: '', description: '', conviction: '' });
            }
        },
        
        removeTouchstone(index) {
            this.touchstones.splice(index, 1);
            if (this.touchstones.length === 0) {
                this.touchstones.push({ name: '', description: '', conviction: '' });
            }
            this.autoSave();
        },
        
        // PORTRAIT UPLOAD
        async uploadPortrait(event, boxType = 'face') {
            const file = event.target.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('box_type', boxType);
            
            try {
                const response = await fetch(`/vtm/character/${this.characterId}/upload-portrait`, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.data[`portrait_${boxType}`] = data.portrait_url;
                    this.autoSave();
                }
            } catch (error) {
                console.error('Portrait upload error:', error);
            }
        },
        
        // XP MANAGEMENT
        addXP() {
            const amount = prompt('How much XP to add?');
            const reason = prompt('Reason (optional):');
            if (amount && !isNaN(amount)) {
                const xpAmount = parseInt(amount);
                this.data.exp_total += xpAmount;
                this.data.exp_available = this.data.exp_total - this.data.exp_spent;
                
                this.xpLog.push({
                    date: new Date().toLocaleDateString(),
                    type: 'add',
                    amount: xpAmount,
                    reason: reason || 'XP Award'
                });
                
                this.autoSave();
            }
        },
        
        spendXP() {
            const amount = prompt('How much XP to spend?');
            const reason = prompt('What did you buy?');
            if (amount && !isNaN(amount)) {
                const spend = parseInt(amount);
                if (spend <= this.data.exp_available) {
                    this.data.exp_spent += spend;
                    this.data.exp_available = this.data.exp_total - this.data.exp_spent;
                    
                    this.xpLog.push({
                        date: new Date().toLocaleDateString(),
                        type: 'spend',
                        amount: spend,
                        reason: reason || 'Purchase'
                    });
                    
                    this.autoSave();
                } else {
                    alert('Not enough available XP!');
                }
            }
        },
        
        // COLUMN RESIZING
        initResizableDividers() {
            // Apply saved widths or defaults
            const widthsAbove = this.data.column_widths_above.split(',').map(w => parseInt(w));
            const widthsBelow = this.data.column_widths_below.split(',').map(w => parseInt(w));
            
            this.applyColumnWidths('above', widthsAbove);
            this.applyColumnWidths('below', widthsBelow);
        },
        
        applyColumnWidths(section, widths) {
            const grid = section === 'above' 
                ? document.querySelector('.sheet-grid-above') 
                : document.querySelector('.sheet-grid-below');
            
            if (grid && widths.length === 3) {
                // Grid has 5 columns: col1, divider, col2, divider, col3
                // Dividers are 8px each (16px total)
                // Adjust percentages to account for dividers
                const col1 = `calc(${widths[0]}% - 5px)`;
                const col2 = `calc(${widths[1]}% - 6px)`;
                const col3 = `calc(${widths[2]}% - 5px)`;
                grid.style.gridTemplateColumns = `${col1} 8px ${col2} 8px ${col3}`;
            }
        },
        
        startResizing(section, dividerIndex, event) {
            event.preventDefault();
            
            const grid = section === 'above' 
                ? document.querySelector('.sheet-grid-above') 
                : document.querySelector('.sheet-grid-below');
            
            const startX = event.clientX;
            const gridRect = grid.getBoundingClientRect();
            const gridWidth = gridRect.width;
            
            // Account for dividers (16px total for both dividers)
            const availableWidth = gridWidth - 16;
            
            // Get current widths
            const currentWidths = section === 'above'
                ? this.data.column_widths_above.split(',').map(w => parseInt(w))
                : this.data.column_widths_below.split(',').map(w => parseInt(w));
            
            const startWidths = [...currentWidths];
            
            const onMouseMove = (e) => {
                const deltaX = e.clientX - startX;
                const deltaPercent = (deltaX / availableWidth) * 100;
                
                // Adjust the two columns on either side of the divider
                const newWidths = [...startWidths];
                newWidths[dividerIndex] = Math.max(15, Math.min(60, startWidths[dividerIndex] + deltaPercent));
                newWidths[dividerIndex + 1] = Math.max(15, Math.min(60, startWidths[dividerIndex + 1] - deltaPercent));
                
                // Ensure total is 100%
                const total = newWidths.reduce((sum, w) => sum + w, 0);
                if (Math.abs(total - 100) > 0.1) {
                    // Adjust third column to maintain 100%
                    const otherIndex = dividerIndex === 0 ? 2 : 0;
                    newWidths[otherIndex] = 100 - newWidths[dividerIndex] - newWidths[dividerIndex + 1];
                    newWidths[otherIndex] = Math.max(15, Math.min(60, newWidths[otherIndex]));
                }
                
                this.applyColumnWidths(section, newWidths);
            };
            
            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                
                // Calculate final widths from actual computed styles
                const grid = section === 'above' 
                    ? document.querySelector('.sheet-grid-above') 
                    : document.querySelector('.sheet-grid-below');
                
                const computedStyle = window.getComputedStyle(grid);
                const columns = computedStyle.gridTemplateColumns.split(' ');
                
                // Columns are: col1, 8px, col2, 8px, col3
                // We want indices 0, 2, 4
                const col1Width = parseFloat(columns[0]);
                const col2Width = parseFloat(columns[2]);
                const col3Width = parseFloat(columns[4]);
                
                const gridWidth = grid.getBoundingClientRect().width;
                const availableWidth = gridWidth - 16; // Account for dividers
                
                const widthsPercent = [
                    Math.round((col1Width / availableWidth) * 100),
                    Math.round((col2Width / availableWidth) * 100),
                    Math.round((col3Width / availableWidth) * 100)
                ];
                
                // Ensure they sum to 100
                const sum = widthsPercent.reduce((a, b) => a + b, 0);
                if (sum !== 100) {
                    widthsPercent[2] += (100 - sum);
                }
                
                if (section === 'above') {
                    this.data.column_widths_above = widthsPercent.join(',');
                } else {
                    this.data.column_widths_below = widthsPercent.join(',');
                }
                
                this.autoSave();
            };
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        }
    }
}

// Make component globally available
window.characterSheet = characterSheet;
