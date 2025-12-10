// Character Sheet JavaScript - Alpine.js Components
// REFACTORED VERSION - Works with new backend schemas

// Main character sheet component
function characterSheet(characterId) {
    return {
        characterId: characterId,
        characterName: '',
        saveStatus: '', // '', 'saving', 'saved', 'error'
        isLoading: true, // Track initial loading state
        loadError: null, // Track loading errors
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
            
            // Resonance
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
            bane_custom: '',
            compulsion: '',
            compulsion_custom: '',
            
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
            
            // History
            history_in_life: '',
            after_death: '',
            notes: ''
        },
        
        // NEW: Touchstones as array (not individual fields)
        touchstones: [],
        
        // NEW: Backgrounds as array (not individual fields)
        backgrounds: [],
        
        // XP Log
        xpLog: [],
        
        // NEW: User preferences (separate from character data)
        preferences: {
            column_widths_above: '40,30,30',
            column_widths_below: '33,33,34'
        },
        
        // Blood Potency calculated values
        bloodPotencyValues: {
            surge: 1,
            mend: 1,
            powerBonus: 0,
            rouseReroll: 0,
            feedingPenalty: 'No penalty',
            baneSeverity: 0
        },

        // PERFORMANCE OPTIMIZATIONS
        // Track changed fields for delta saves
        changedFields: new Set(),
        // Save queue for batching
        saveQueue: null,
        saveTimeout: null,
        // Track if we're currently saving
        isSaving: false,

        // Initialize component
        async init() {
            console.log('Character sheet initializing, ID:', this.characterId);
            if (this.characterId) {
                await this.loadCharacter();
                await this.loadUserPreferences();
            } else {
                // New character - initialize with one empty touchstone
                this.touchstones.push({
                    name: '',
                    description: '',
                    conviction: ''
                });

                // Initialize with 3 empty backgrounds
                for (let i = 0; i < 3; i++) {
                    this.backgrounds.push({
                        category: 'Background',
                        type: '',
                        description: '',
                        dots: 0,
                        description_height: 60
                    });
                }

                // No loading needed for new character
                this.isLoading = false;
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
            this.isLoading = true;
            this.loadError = null;

            try {
                // Use storyteller API endpoint if in storyteller mode
                const apiPath = window.STORYTELLER_MODE
                    ? `/storyteller/vtm/api/character/${this.characterId}`
                    : `/vtm/api/character/${this.characterId}`;
                const response = await fetch(apiPath);

                if (!response.ok) {
                    const errorData = await response.json();
                    this.loadError = errorData.error || 'Failed to load character';
                    this.handleError(errorData);
                    return;
                }
                
                const character = await response.json();
                
                // Update all data fields
                Object.keys(this.data).forEach(key => {
                    if (character[key] !== undefined && character[key] !== null) {
                        this.data[key] = character[key];
                    }
                });
                
                this.characterName = character.name || 'Unnamed';
                
                // NEW: Load touchstones from array
                if (character.touchstones && Array.isArray(character.touchstones)) {
                    this.touchstones = character.touchstones.map(ts => ({
                        name: ts.name || '',
                        description: ts.description || '',
                        conviction: ts.conviction || ''
                    }));
                } else {
                    // Fallback: Load from old individual fields (backwards compatibility)
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
                }
                
                // If no touchstones, add one empty
                if (this.touchstones.length === 0) {
                    this.touchstones.push({ name: '', description: '', conviction: '' });
                }
                
                // NEW: Load backgrounds from array
                if (character.backgrounds && Array.isArray(character.backgrounds)) {
                    this.backgrounds = character.backgrounds.map(bg => ({
                        category: bg.category || 'Background',
                        type: bg.type || '',
                        description: bg.description || '',
                        dots: bg.dots || 0,
                        description_height: bg.description_height || 60
                    }));
                } else {
                    // Fallback: Load from old individual fields (backwards compatibility)
                    this.backgrounds = [];
                    for (let i = 1; i <= 10; i++) {
                        const type = character[`background_type_${i}`];
                        if (type) {
                            this.backgrounds.push({
                                category: 'Background',
                                type: type,
                                description: character[`background_description_${i}`] || '',
                                dots: character[`background_dots_${i}`] || 0,
                                description_height: 60
                            });
                        }
                    }
                }

                // If no backgrounds, add 3 empty ones
                if (this.backgrounds.length === 0) {
                    for (let i = 0; i < 3; i++) {
                        this.backgrounds.push({ category: 'Background', type: '', description: '', dots: 0, description_height: 60 });
                    }
                }
                
                // Load XP log
                if (character.xp_log) {
                    try {
                        if (typeof character.xp_log === 'string') {
                            this.xpLog = JSON.parse(character.xp_log);
                        } else if (Array.isArray(character.xp_log)) {
                            this.xpLog = character.xp_log;
                        }
                    } catch (e) {
                        console.error('Error parsing XP log:', e);
                        this.xpLog = [];
                    }
                }

                // Update Blood Potency calculated values after loading
                this.updateBloodPotency(this.data.blood_potency || 0);

                console.log('Character loaded:', this.data);

            } catch (error) {
                console.error('Error loading character:', error);
                this.loadError = 'Failed to load character. Please check your connection.';
                this.showError(this.loadError);
            } finally {
                this.isLoading = false;
            }
        },
        
        // NEW: Load user preferences separately
        async loadUserPreferences() {
            console.log('Loading user preferences...');
            try {
                const response = await fetch('/vtm/api/preferences');
                console.log('Preferences response status:', response.status);

                if (response.ok) {
                    const prefs = await response.json();
                    this.preferences = prefs;
                    console.log('Loaded user preferences:', prefs);

                    // Apply saved column widths
                    if (prefs.column_widths_above) {
                        const widthsAbove = prefs.column_widths_above.split(',').map(w => parseInt(w));
                        this.applyColumnWidths('above', widthsAbove);
                        console.log('Applied above column widths:', widthsAbove);
                    }
                    if (prefs.column_widths_below) {
                        const widthsBelow = prefs.column_widths_below.split(',').map(w => parseInt(w));
                        this.applyColumnWidths('below', widthsBelow);
                        console.log('Applied below column widths:', widthsBelow);
                    }
                } else {
                    const errorText = await response.text();
                    console.warn('Preferences response not OK:', response.status, errorText);
                    // Use defaults from character data (fallback)
                    if (this.data.column_widths_above) {
                        const widthsAbove = this.data.column_widths_above.split(',').map(w => parseInt(w));
                        this.applyColumnWidths('above', widthsAbove);
                    }
                    if (this.data.column_widths_below) {
                        const widthsBelow = this.data.column_widths_below.split(',').map(w => parseInt(w));
                        this.applyColumnWidths('below', widthsBelow);
                    }
                }
            } catch (error) {
                console.error('Error loading preferences:', error);
                // Not critical - just use defaults
            }
        },
        
        // NEW: Save user preferences separately
        async saveUserPreferences() {
            try {
                console.log('Saving user preferences:', this.preferences);
                const response = await fetch('/vtm/api/preferences', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.preferences)
                });

                if (response.ok) {
                    console.log('Preferences saved successfully');
                } else {
                    console.error('Failed to save preferences:', response.status);
                }
            } catch (error) {
                console.error('Error saving preferences:', error);
                // Not critical - don't show error to user
            }
        },
        
        // Track field changes for delta saves
        trackChange(field) {
            this.changedFields.add(field);
        },

        // Improved auto-save with batching, delta saves, and optimistic updates
        async autoSave(changedField = null) {
            if (!this.characterId) {
                await this.createCharacter();
                return;
            }

            // Track which field changed
            if (changedField) {
                this.trackChange(changedField);
            }

            // Optimistic UI update - show saving immediately
            this.saveStatus = 'saving';

            // Clear existing timeout and set new one for batching
            if (this.saveTimeout) {
                clearTimeout(this.saveTimeout);
            }

            // Batch multiple rapid changes with 500ms debounce (reduced from 2s)
            this.saveTimeout = setTimeout(async () => {
                // Skip if already saving
                if (this.isSaving) {
                    // Re-queue the save
                    this.autoSave();
                    return;
                }

                this.isSaving = true;

                try {
                    // Build save data - use delta if we have tracked changes
                    let saveData;

                    if (this.changedFields.size > 0 && this.changedFields.size < 10) {
                        // Delta save - only send changed fields
                        saveData = {};
                        this.changedFields.forEach(field => {
                            if (this.data[field] !== undefined) {
                                saveData[field] = this.data[field];
                            }
                        });
                        // Always include arrays if they might have changed
                        if (this.changedFields.has('touchstones')) {
                            saveData.touchstones = this.touchstones;
                        }
                        if (this.changedFields.has('backgrounds')) {
                            saveData.backgrounds = this.backgrounds;
                        }
                        if (this.changedFields.has('xp_log')) {
                            saveData.xp_log = JSON.stringify(this.xpLog);
                        }
                        console.log('Delta save:', Array.from(this.changedFields));
                    } else {
                        // Full save - for initial saves or many changes
                        saveData = {
                            ...this.data,
                            touchstones: this.touchstones,
                            backgrounds: this.backgrounds,
                            xp_log: JSON.stringify(this.xpLog)
                        };
                        console.log('Full save');
                    }

                    const response = await fetch(`/vtm/character/${this.characterId}/update`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(saveData)
                    });

                    if (response.ok) {
                        // Success - update UI
                        this.saveStatus = 'saved';
                        this.characterName = this.data.name || 'Unnamed';
                        this.changedFields.clear();
                        setTimeout(() => {
                            if (this.saveStatus === 'saved') {
                                this.saveStatus = '';
                            }
                        }, 2000);
                    } else {
                        const errorData = await response.json();
                        this.saveStatus = 'error';
                        this.handleError(errorData);
                    }

                } catch (error) {
                    console.error('Save error:', error);
                    this.saveStatus = 'error';
                    this.showError('Failed to save character. Please check your connection.');
                } finally {
                    this.isSaving = false;
                }
            }, 500); // Reduced from 2000ms to 500ms for better responsiveness
        },
        
        // Create new character
        async createCharacter() {
            try {
                const createData = {
                    ...this.data,
                    touchstones: this.touchstones,
                    backgrounds: this.backgrounds
                };
                
                const response = await fetch('/vtm/character/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(createData)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    window.location.href = `/vtm/character/${result.id}/edit`;
                } else {
                    const errorData = await response.json();
                    this.handleError(errorData);
                }
            } catch (error) {
                console.error('Create error:', error);
                this.showError('Failed to create character. Please try again.');
            }
        },
        
        // NEW: Enhanced error handling
        handleError(errorData) {
            console.error('API Error:', errorData);
            
            // Check for validation errors with field details
            if (errorData.details && Array.isArray(errorData.details)) {
                const fieldErrors = errorData.details.map(detail => {
                    return `${detail.field}: ${detail.message}`;
                }).join('\n');
                
                this.showError(`Validation Error:\n${fieldErrors}`);
            } 
            // Check for general error message
            else if (errorData.error) {
                this.showError(errorData.error);
            }
            // Fallback
            else {
                this.showError('An error occurred. Please try again.');
            }
        },
        
        // NEW: User-friendly error display
        showError(message) {
            // Could be enhanced with a modal or toast notification
            alert(message);
            
            // Log to console for debugging
            console.error('User-facing error:', message);
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
                // Make empty (remove aggravated and reduce max)
                this.data.health_aggravated--;
                this.data.health_max--;
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
                // Make empty (remove aggravated and reduce max)
                this.data.willpower_aggravated--;
                this.data.willpower_max--;
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

        cycleHumanity(index) {
            const state = this.getHumanityState(index);
            const current = this.data.humanity_current || 7;
            const stained = this.data.humanity_stained || 0;
            const lastFilled = current - stained;

            if (index === lastFilled && state === 'filled') {
                // Clicking the last filled box - make it stained
                this.data.humanity_stained++;
            } else if (index === lastFilled + 1 && state === 'stained') {
                // Clicking the first stained box - make it empty
                this.data.humanity_current--;
                this.data.humanity_stained--;
            } else if (index === current + 1 && state === 'empty' && index <= 10) {
                // Clicking the first empty box - make it filled
                this.data.humanity_current = index;
            } else if (state === 'empty' && index <= 10) {
                // Clicking any empty box - extend current to that box
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
            
            // Format discipline name for display (capitalize, replace hyphens with spaces)
            const formatDisciplineName = (disc) => {
                return disc.split('-')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            };
            
            return disciplines.map(disc =>
                `<div class="discipline-icon-item">
                    <img src="/static/images/disciplines/${disc}.png?v=${window.STATIC_VERSION || ''}"
                         alt="${formatDisciplineName(disc)}"
                         title="${formatDisciplineName(disc)}"
                         class="discipline-icon">
                    <div class="discipline-label">${formatDisciplineName(disc)}</div>
                </div>`
            ).join('');
        },

        // Get selected discipline icons (dynamic based on what's actually chosen)
        getSelectedDisciplineIcons() {
            // Collect all selected disciplines from the 5 slots
            const selectedDisciplines = [];
            for (let i = 1; i <= 5; i++) {
                const discName = this.data[`discipline_${i}_name`];
                if (discName && discName.trim() !== '') {
                    selectedDisciplines.push(discName);
                }
            }

            // If no disciplines selected, fall back to clan disciplines
            if (selectedDisciplines.length === 0) {
                return this.getClanDisciplineIcons();
            }

            // Format discipline name for display (capitalize, replace hyphens with spaces)
            const formatDisciplineName = (disc) => {
                return disc.split('-')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            };

            // Return HTML for selected disciplines
            return selectedDisciplines.map(disc =>
                `<div class="discipline-icon-item">
                    <img src="/static/images/disciplines/${disc}.png?v=${window.STATIC_VERSION || ''}"
                         alt="${formatDisciplineName(disc)}"
                         title="${formatDisciplineName(disc)}"
                         class="discipline-icon">
                    <div class="discipline-label">${formatDisciplineName(disc)}</div>
                </div>`
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
        
        // BACKGROUND MANAGEMENT
        addBackground() {
            if (this.backgrounds.length < 10) {
                this.backgrounds.push({ category: 'Background', type: '', description: '', dots: 0, description_height: 60 });
            }
        },
        
        removeBackground(index) {
            this.backgrounds.splice(index, 1);
            this.autoSave();
        },

        // Auto-resize textarea and save height
        autoResizeTextarea(event, index) {
            const textarea = event.target;
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
            this.backgrounds[index].description_height = textarea.scrollHeight;
            this.autoSave();
        },

        // Apply saved textarea height
        applyTextareaHeight(index) {
            this.$nextTick(() => {
                const textarea = this.$refs[`bgDesc${index}`];
                if (textarea && textarea[0]) {
                    const height = this.backgrounds[index].description_height || 60;
                    textarea[0].style.height = height + 'px';
                }
            });
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
                } else {
                    const errorData = await response.json();
                    this.handleError(errorData);
                }
            } catch (error) {
                console.error('Portrait upload error:', error);
                this.showError('Failed to upload portrait. Please try again.');
            }
        },

        // Helper method to trigger hobby portrait upload
        triggerHobbyUpload(event) {
            // Find the file input within the same parent container
            const container = event.currentTarget.parentElement;
            const fileInput = container.querySelector('input[type="file"]');
            if (fileInput) {
                console.log('Triggering hobby upload');
                fileInput.click();
            } else {
                console.error('File input not found for hobby upload');
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
            // Apply saved widths from preferences or fallback to defaults
            const widthsAbove = this.preferences.column_widths_above 
                ? this.preferences.column_widths_above.split(',').map(w => parseInt(w))
                : [40, 30, 30];
            const widthsBelow = this.preferences.column_widths_below
                ? this.preferences.column_widths_below.split(',').map(w => parseInt(w))
                : [33, 33, 34];
            
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
            
            // Get current widths from preferences with safety checks
            const defaultWidths = section === 'above' ? [40, 30, 30] : [33, 33, 34];
            let currentWidths;

            try {
                const widthString = section === 'above'
                    ? this.preferences.column_widths_above
                    : this.preferences.column_widths_below;

                if (widthString && typeof widthString === 'string') {
                    currentWidths = widthString.split(',').map(w => parseInt(w));
                    // Validate we got 3 valid numbers
                    if (currentWidths.length !== 3 || currentWidths.some(w => isNaN(w))) {
                        console.warn('Invalid column widths, using defaults');
                        currentWidths = defaultWidths;
                    }
                } else {
                    currentWidths = defaultWidths;
                }
            } catch (error) {
                console.error('Error parsing column widths:', error);
                currentWidths = defaultWidths;
            }

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
                
                // Save to preferences
                if (section === 'above') {
                    this.preferences.column_widths_above = widthsPercent.join(',');
                } else {
                    this.preferences.column_widths_below = widthsPercent.join(',');
                }

                console.log(`Saving ${section} column widths:`, widthsPercent.join(','));
                this.saveUserPreferences();
            };
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        }
    }
}

// Make component globally available
window.characterSheet = characterSheet;
