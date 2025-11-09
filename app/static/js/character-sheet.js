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
            
            // Health & Willpower tracking
            health_superficial: 0,
            health_aggravated: 0,
            willpower_superficial: 0,
            willpower_aggravated: 0,
            humanity_current: 7,
            
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
            
            // Chronicle Tenets
            chronicle_tenets: '',
            
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
        
        // Computed values
        get healthMax() {
            return (this.data.stamina || 1) + 3;
        },
        
        get willpowerMax() {
            return (this.data.composure || 1) + (this.data.resolve || 1);
        },
        
        get clanDisciplines() {
            const clanDiscs = {
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
                'tzimisce': ['animalism', 'dominate', 'protean']
            };
            return clanDiscs[this.data.clan] || [];
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
        
        // Skill specialties management
        getSpecialties(skill) {
            if (!this.data.skill_specialties) return [];
            const specs = this.data.skill_specialties.split(',').filter(s => s.trim());
            return specs.filter(s => s.startsWith(skill + ':')).map(s => s.split(':')[1]);
        },
        
        capitalize(str) {
            return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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
            const reason = prompt('Reason (optional):');
            if (amount && !isNaN(amount)) {
                const xpAmount = parseInt(amount);
                this.data.exp_total += xpAmount;
                this.data.exp_available = this.data.exp_total - this.data.exp_spent;
                
                // Add to log
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
                    
                    // Add to log
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

// Skill tracker component (with specialties)
function skillTracker(skillName, initialValue = 0, initialSpecialties = []) {
    return {
        skillName: skillName,
        value: initialValue,
        specialties: initialSpecialties,
        
        init() {
            this.$watch(`$parent.data.${skillName}`, val => {
                this.value = val;
            });
        },
        
        handleDotClick(event) {
            const dots = event.currentTarget.querySelectorAll('.dot');
            const clickedDot = event.target.closest('.dot');
            if (!clickedDot) return;
            
            const clickedIndex = Array.from(dots).indexOf(clickedDot) + 1;
            
            if (clickedIndex <= this.value) {
                this.value = Math.max(clickedIndex - 1, 0);
            } else {
                this.value = clickedIndex;
            }
            
            this.$parent.data[this.skillName] = this.value;
            this.$parent.autoSave();
        },
        
        addSpecialty() {
            const spec = prompt(`Add specialty for ${this.capitalize(this.skillName)}:`);
            if (spec && spec.trim()) {
                if (this.specialties.length < this.value) {
                    this.specialties.push(spec.trim());
                    this.saveSpecialties();
                } else {
                    alert(`Maximum ${this.value} specialties for this skill!`);
                }
            }
        },
        
        removeSpecialty(idx) {
            this.specialties.splice(idx, 1);
            this.saveSpecialties();
        },
        
        saveSpecialties() {
            // Update parent's skill_specialties string
            let allSpecs = [];
            
            // Parse existing specialties
            if (this.$parent.data.skill_specialties) {
                allSpecs = this.$parent.data.skill_specialties.split(',').filter(s => s.trim() && !s.startsWith(this.skillName + ':'));
            }
            
            // Add current skill's specialties
            this.specialties.forEach(spec => {
                allSpecs.push(`${this.skillName}:${spec}`);
            });
            
            this.$parent.data.skill_specialties = allSpecs.join(',');
            this.$parent.autoSave();
        },
        
        capitalize(str) {
            return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    };
}

// Box tracker for Health/Willpower (4 states) - ALWAYS SHOW 10 BOXES
function boxTracker(type, maxBoxes, superficial = 0, aggravated = 0) {
    return {
        type: type,
        maxBoxes: 10,  // Always display 10 boxes
        calculatedMax: maxBoxes,  // Actual max based on attributes
        superficial: superficial,
        aggravated: aggravated,
        
        getBoxState(index) {
            // Damage fills from RIGHT (last boxes first)
            const usableBoxes = this.calculatedMax - this.superficial - this.aggravated;
            
            if (index <= usableBoxes) {
                return 'filled'; // Red - usable
            } else if (index <= this.calculatedMax - this.aggravated) {
                return 'superficial'; // Yellow - superficial damage
            } else if (index <= this.calculatedMax) {
                return 'aggravated'; // Black - aggravated damage
            }
            return 'empty'; // Beyond calculated max
        },
        
        cycleBox(index) {
            // Only cycle boxes within calculated max
            if (index > this.calculatedMax) return;
            
            const currentState = this.getBoxState(index);
            
            // Cycle: filled → superficial → aggravated → filled
            if (currentState === 'filled') {
                // Add superficial damage
                if (this.superficial + this.aggravated < this.calculatedMax) {
                    this.superficial++;
                }
            } else if (currentState === 'superficial') {
                // Convert to aggravated
                this.superficial--;
                this.aggravated++;
            } else if (currentState === 'aggravated') {
                // Remove damage (back to filled)
                this.aggravated--;
            }
            
            this.save();
        },
        
        save() {
            this.$parent.data[`${this.type}_superficial`] = this.superficial;
            this.$parent.data[`${this.type}_aggravated`] = this.aggravated;
            this.$parent.autoSave();
        }
    };
}

// Humanity tracker (3 states: empty, filled, stained)
function humanityTracker(current = 7) {
    return {
        current: current,
        stained: 0,
        
        getHumanityState(index) {
            if (index <= this.current - this.stained) {
                return 'filled'; // Red
            } else if (index <= this.current) {
                return 'stained'; // Black
            }
            return 'empty';
        },
        
        setHumanity(level) {
            // Left click: set humanity to this level
            this.current = level;
            this.stained = 0;
            this.save();
        },
        
        stainHumanity(level) {
            // Right click: stain this level
            if (level <= this.current) {
                const stainsAbove = this.current - level + 1;
                this.stained = Math.min(stainsAbove, this.current);
                this.save();
            }
        },
        
        save() {
            this.$parent.data.humanity_current = this.current;
            this.$parent.autoSave();
        }
    };
}

// Discipline slot component - NO AUTO-POPULATION
function disciplineSlot(slotNumber) {
    return {
        slotNumber: slotNumber,
        disciplineName: '',
        disciplineLevel: 0,
        powers: '',
        description: '',
        
        init() {
            // Load from parent data
            this.disciplineName = this.$parent.data[`discipline_${this.slotNumber}_name`] || '';
            this.disciplineLevel = this.$parent.data[`discipline_${this.slotNumber}_level`] || 0;
            this.powers = this.$parent.data[`discipline_${this.slotNumber}_powers`] || '';
            this.description = this.$parent.data[`discipline_${this.slotNumber}_description`] || '';
            
            // NO AUTO-POPULATION - all slots work the same
        },
        
        handleDotClick(event) {
            const dots = event.currentTarget.querySelectorAll('.dot');
            const clickedDot = event.target.closest('.dot');
            if (!clickedDot) return;
            
            const clickedIndex = Array.from(dots).indexOf(clickedDot) + 1;
            
            if (clickedIndex <= this.disciplineLevel) {
                this.disciplineLevel = Math.max(clickedIndex - 1, 0);
            } else {
                this.disciplineLevel = clickedIndex;
            }
            
            this.updateDiscipline();
        },
        
        updateDiscipline() {
            this.$parent.data[`discipline_${this.slotNumber}_name`] = this.disciplineName;
            this.$parent.data[`discipline_${this.slotNumber}_level`] = this.disciplineLevel;
            this.$parent.data[`discipline_${this.slotNumber}_powers`] = this.powers;
            this.$parent.data[`discipline_${this.slotNumber}_description`] = this.description;
            this.$parent.autoSave();
        }
    };
}

// Make all components available
window.skillTracker = skillTracker;
window.boxTracker = boxTracker;
window.humanityTracker = humanityTracker;
window.disciplineSlot = disciplineSlot;
