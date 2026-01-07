// HTR Character Sheet JavaScript - Alpine.js Component
// Hunter: The Reckoning 5e Character Sheet

// Creed to Drive-Boosted Skills mapping
const CREED_BOOSTS = {
    faithful: ['insight', 'medicine', 'occult'],
    inquisitive: ['academics', 'investigation', 'science'],
    martial: ['athletics', 'brawl', 'firearms'],
    entrepreneurial: ['finance', 'persuasion', 'streetwise'],
    underground: ['larceny', 'stealth', 'survival']
};

// Main HTR character sheet component
function htrCharacterSheet(characterId) {
    return {
        characterId: characterId,
        saveStatus: '', // '', 'saving', 'saved', 'error'
        isLoading: true,
        loadError: null,
        allEdges: [],  // All available edges from JSON
        characterEdges: [],  // Edges selected for this character
        characterPerks: [],  // Perks selected for this character
        data: {
            // Header
            name: '',
            cell: '',
            chronicle: '',
            creed: '',
            drive: '',
            desire: '',
            ambition: '',

            // Identity
            age: '',
            blood_type: '',
            pronouns: '',
            origin: '',

            // Portraits
            portrait_face: '',
            portrait_body: '',
            portrait_hobby_1: '',
            portrait_hobby_2: '',
            portrait_hobby_3: '',
            portrait_hobby_4: '',
            alias: '',

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

            // Skills (0-5) - Note: drive_skill in DB, but we use 'drive_skill' in data
            athletics: 0,
            brawl: 0,
            craft: 0,
            drive_skill: 0,
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

            // Skill specialties
            skill_specialties: '',

            // Trackers
            danger_current: 0,
            desperation_current: 0,
            health_max: 6,
            health_superficial: 0,
            health_aggravated: 0,
            willpower_max: 5,
            willpower_superficial: 0,
            willpower_aggravated: 0,
            in_despair: false,

            // Edges & Perks
            edge_config: '1e2p',
            edge_1_id: '',
            edge_2_id: '',
            selected_perks: '',

            // Equipment
            equipment_weapon: '',
            equipment_weapon_damage: 0,
            equipment_armor_rating: 0,
            equipment_notes: '',

            // Experience
            exp_total: 0,
            exp_available: 0,
            exp_spent: 0,

            // History
            first_encounter: '',
            history: '',
            notes: '',
            current_mission: ''
        },

        // Arrays for relationships
        touchstones: [],
        advantages: [],
        flaws: [],
        equipment: [],
        xpLog: [],
        // characterEdges now contains: [{ edge_id: 'arsenal', perks: [{ perk_id: 'well-armed' }] }]

        // Skill lists
        physicalSkills: ['athletics', 'brawl', 'craft', 'drive_skill', 'firearms', 'larceny', 'melee', 'stealth', 'survival'],
        socialSkills: ['animal_ken', 'etiquette', 'insight', 'intimidation', 'leadership', 'performance', 'persuasion', 'streetwise', 'subterfuge'],
        mentalSkills: ['academics', 'awareness', 'finance', 'investigation', 'medicine', 'occult', 'politics', 'science', 'technology'],

        // Initialize
        async init() {
            // Load edges data
            await this.loadEdgesData();

            if (this.characterId) {
                await this.loadCharacter();
            } else {
                this.isLoading = false;
            }

            // Setup auto-resize for textareas after a short delay to ensure DOM is ready
            setTimeout(() => this.setupTextareaAutoResize(), 100);

            // Auto-calculate Willpower base (Composure + Resolve)
            // Only update if calculated base is higher than current (preserves manual increases from Edges/Perks)
            this.$watch('data.composure', () => {
                const calculatedBase = this.data.composure + this.data.resolve;
                if (this.data.willpower_max < calculatedBase) {
                    this.data.willpower_max = calculatedBase;
                    if (!this.isLoading) this.autoSave();
                }
            });
            this.$watch('data.resolve', () => {
                const calculatedBase = this.data.composure + this.data.resolve;
                if (this.data.willpower_max < calculatedBase) {
                    this.data.willpower_max = calculatedBase;
                    if (!this.isLoading) this.autoSave();
                }
            });

            // Auto-calculate Health max (Stamina + 3)
            this.$watch('data.stamina', () => {
                this.data.health_max = this.data.stamina + 3;
                if (!this.isLoading) this.autoSave();
            });

            // Watch for changes in edges/perks and auto-save with debounce
            let edgesSaveTimeout;
            this.$watch('characterEdges', () => {
                if (!this.isLoading) {
                    console.log('Edges/Perks changed, scheduling save...', JSON.parse(JSON.stringify(this.characterEdges)));
                    clearTimeout(edgesSaveTimeout);
                    edgesSaveTimeout = setTimeout(() => {
                        console.log('Executing debounced save for edges/perks...');
                        this.autoSave();
                    }, 500);
                }
            }, { deep: true });
        },

        async loadEdgesData() {
            try {
                const response = await fetch('/static/data/htr_edges.json');
                const data = await response.json();
                this.allEdges = data.edges || [];
                console.log('Loaded allEdges from JSON:', this.allEdges.length, 'edges');
                console.log('Sample edge IDs:', this.allEdges.slice(0, 3).map(e => e.id));
            } catch (error) {
                console.error('Failed to load edges data:', error);
                this.allEdges = [];
            }
        },

        async loadCharacter() {
            try {
                // Use storyteller API endpoint if in storyteller mode
                const apiPath = window.STORYTELLER_MODE
                    ? `/storyteller/htr/api/character/${this.characterId}`
                    : `/htr/api/character/${this.characterId}`;
                const response = await fetch(apiPath);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const char = await response.json();

                // Populate data
                for (let key in this.data) {
                    if (char[key] !== undefined && char[key] !== null) {
                        this.data[key] = char[key];
                    }
                }

                // Load relationships
                this.touchstones = char.touchstones || [];
                this.advantages = char.advantages || [];
                this.flaws = char.flaws || [];
                this.equipment = char.equipment || [];
                this.xpLog = char.xp_log || [];

                // Load edges and nest perks under them
                const edges = char.edges || [];
                const perks = char.perks || [];

                console.log('Loading edges from backend:', edges);
                console.log('Loading perks from backend:', perks);

                // Transform: nest perks under their parent edges
                this.characterEdges = edges.map(edge => {
                    console.log(`Processing edge: ${edge.edge_id}`);
                    const edgePerks = perks.filter(perk => perk.edge_id === edge.edge_id)
                                          .map(perk => ({ perk_id: perk.perk_id }));
                    console.log(`  Found ${edgePerks.length} perks for this edge`);
                    return {
                        edge_id: edge.edge_id,
                        perks: edgePerks
                    };
                });

                console.log('Transformed to nested structure:', JSON.parse(JSON.stringify(this.characterEdges)));
                console.log('allEdges available for dropdowns:', this.allEdges.length, 'edges');

                // Force Alpine to re-render by waiting a tick
                await this.$nextTick();

                this.isLoading = false;
            } catch (error) {
                console.error('Failed to load character:', error);
                this.loadError = 'Failed to load character data. Please try again.';
                this.isLoading = false;
            }
        },

        async autoSave() {
            if (!this.characterId) {
                // Creating new character
                await this.createCharacter();
                return;
            }

            this.saveStatus = 'saving';

            try {
                // Flatten edges and perks for backend
                const edges = this.characterEdges
                    .filter(e => e.edge_id)  // Only include edges with an ID
                    .map(e => ({ edge_id: e.edge_id }));

                const perks = this.characterEdges
                    .filter(e => e.edge_id && e.perks && e.perks.length > 0)  // Only edges with perks
                    .flatMap(e => e.perks
                        .filter(p => p.perk_id)  // Only perks with an ID
                        .map(p => ({ edge_id: e.edge_id, perk_id: p.perk_id }))
                    );

                console.log('Saving edges:', edges);
                console.log('Saving perks:', perks);

                const payload = {
                    ...this.data,
                    touchstones: this.touchstones,
                    advantages: this.advantages,
                    flaws: this.flaws,
                    edges: edges,
                    perks: perks,
                    equipment: this.equipment,
                    xp_log: this.xpLog
                };

                const response = await fetch(`/htr/character/${this.characterId}/update`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error('Save failed');
                }

                this.saveStatus = 'saved';
                setTimeout(() => { this.saveStatus = ''; }, 2000);
            } catch (error) {
                console.error('Save error:', error);
                this.saveStatus = 'error';
                setTimeout(() => { this.saveStatus = ''; }, 3000);
            }
        },

        async createCharacter() {
            try {
                // Flatten edges and perks for backend
                const edges = this.characterEdges
                    .filter(e => e.edge_id)
                    .map(e => ({ edge_id: e.edge_id }));

                const perks = this.characterEdges
                    .filter(e => e.edge_id && e.perks && e.perks.length > 0)
                    .flatMap(e => e.perks
                        .filter(p => p.perk_id)
                        .map(p => ({ edge_id: e.edge_id, perk_id: p.perk_id }))
                    );

                const payload = {
                    ...this.data,
                    touchstones: this.touchstones,
                    advantages: this.advantages,
                    flaws: this.flaws,
                    edges: edges,
                    perks: perks,
                    equipment: this.equipment,
                    xp_log: this.xpLog
                };

                const response = await fetch('/htr/character/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error('Create failed');
                }

                const result = await response.json();
                if (result.id) {
                    // Redirect to edit page
                    window.location.href = `/htr/character/${result.id}/edit`;
                }
            } catch (error) {
                console.error('Create error:', error);
                alert('Failed to create character. Please try again.');
            }
        },

        // Dot tracker click handler
        clickDot(field, value, min, max) {
            if (value < min) value = min;
            if (value > max) value = max;

            // If clicking the currently filled box, reduce by 1 (allows going back to 0)
            if (this.data[field] === value) {
                this.data[field] = Math.max(min, value - 1);
            } else {
                this.data[field] = value;
            }

            this.autoSave();
        },

        // Health tracker
        getHealthState(index) {
            if (index > this.data.health_max) return 'hidden';
            if (index <= this.data.health_aggravated) return 'aggravated';
            if (index <= (this.data.health_aggravated + this.data.health_superficial)) return 'superficial';
            return 'empty';
        },

        cycleHealth(index) {
            if (index > this.data.health_max) return;

            const state = this.getHealthState(index);
            if (state === 'empty') {
                // Mark as superficial
                this.data.health_superficial++;
            } else if (state === 'superficial') {
                // Convert to aggravated
                this.data.health_superficial--;
                this.data.health_aggravated++;
            } else if (state === 'aggravated') {
                // Clear
                this.data.health_aggravated--;
            }
            this.autoSave();
        },

        // Willpower tracker
        getWillpowerState(index) {
            if (index > this.data.willpower_max) return 'hidden';
            if (index <= this.data.willpower_aggravated) return 'aggravated';
            if (index <= (this.data.willpower_aggravated + this.data.willpower_superficial)) return 'superficial';
            return 'empty';
        },

        cycleWillpower(index) {
            const state = this.getWillpowerState(index);
            const max = this.data.willpower_max || 5;

            // Allow clicking empty boxes beyond current max to extend it (for Edges/Perks bonuses)
            if (state === 'hidden' && index <= 10) {
                // Extend max (useful for Edges/Perks that boost Willpower)
                this.data.willpower_max = index;
            } else if (state === 'empty') {
                // Add superficial damage
                if ((this.data.willpower_superficial + this.data.willpower_aggravated) < max) {
                    this.data.willpower_superficial++;
                }
            } else if (state === 'superficial') {
                // Convert superficial to aggravated
                this.data.willpower_superficial--;
                this.data.willpower_aggravated++;
            } else if (state === 'aggravated') {
                // Clear aggravated damage and reduce max (allows resetting manual increases)
                this.data.willpower_aggravated--;
                this.data.willpower_max--;
            }
            this.autoSave();
        },

        // Danger color coding
        getDangerColor(value) {
            if (value <= 10) return 'safe';
            if (value <= 15) return 'warning';
            return 'danger';
        },

        // Drive-boosted skills
        isDriveBoosted(skill) {
            if (!this.data.creed) return false;
            const boostedSkills = CREED_BOOSTS[this.data.creed] || [];
            // Handle drive_skill -> drive mapping
            const skillName = skill === 'drive_skill' ? 'drive' : skill;
            return boostedSkills.includes(skillName);
        },

        // Skill specialties
        getSpecialties(skill) {
            try {
                const specs = JSON.parse(this.data.skill_specialties || '{}');
                return specs[skill] || [];
            } catch {
                return [];
            }
        },

        addSpecialty(skill) {
            const name = prompt('Enter specialty name:');
            if (!name) return;

            try {
                const specs = JSON.parse(this.data.skill_specialties || '{}');
                if (!specs[skill]) specs[skill] = [];
                if (!specs[skill].includes(name)) {
                    specs[skill].push(name);
                    this.data.skill_specialties = JSON.stringify(specs);
                    this.autoSave();
                }
            } catch (error) {
                console.error('Failed to add specialty:', error);
            }
        },

        removeSpecialty(skill, name) {
            try {
                const specs = JSON.parse(this.data.skill_specialties || '{}');
                if (specs[skill]) {
                    specs[skill] = specs[skill].filter(s => s !== name);
                    if (specs[skill].length === 0) delete specs[skill];
                    this.data.skill_specialties = JSON.stringify(specs);
                    this.autoSave();
                }
            } catch (error) {
                console.error('Failed to remove specialty:', error);
            }
        },

        // Edges & Perks (NESTED SYSTEM)
        addEdge() {
            this.characterEdges.push({ edge_id: '', perks: [] });
        },

        removeEdge(index) {
            this.characterEdges.splice(index, 1);
        },

        addPerkToEdge(edgeIndex) {
            if (!this.characterEdges[edgeIndex].perks) {
                this.characterEdges[edgeIndex].perks = [];
            }
            this.characterEdges[edgeIndex].perks.push({ perk_id: '' });
        },

        removePerkFromEdge(edgeIndex, perkIndex) {
            this.characterEdges[edgeIndex].perks.splice(perkIndex, 1);
        },

        getEdgeName(edgeId) {
            const edge = this.allEdges.find(e => e.id === edgeId);
            return edge ? edge.name : '';
        },

        getEdgeDescription(edgeId) {
            const edge = this.allEdges.find(e => e.id === edgeId);
            return edge ? edge.description : '';
        },

        getPerksForEdge(edgeId) {
            const edge = this.allEdges.find(e => e.id === edgeId);
            return edge && edge.perks ? edge.perks : [];
        },

        getPerkDescription(edgeId, perkId) {
            const edge = this.allEdges.find(e => e.id === edgeId);
            if (!edge || !edge.perks) return '';
            const perk = edge.perks.find(p => p.id === perkId);
            return perk ? perk.description : '';
        },

        // Touchstones
        addTouchstone() {
            if (this.touchstones.length >= 3) return;
            this.touchstones.push({ name: '', description: '' });
            this.autoSave();
        },

        removeTouchstone(index) {
            this.touchstones.splice(index, 1);
            this.autoSave();
        },

        // Equipment
        addEquipment() {
            this.equipment.push({ name: '', description: '' });
            this.autoSave();
        },

        removeEquipment(index) {
            this.equipment.splice(index, 1);
            this.autoSave();
        },

        // Advantages
        addAdvantage() {
            this.advantages.push({ type: '', description: '', dots: 1 });
            this.autoSave();
        },

        removeAdvantage(index) {
            this.advantages.splice(index, 1);
            this.autoSave();
        },

        getAdvantageTotalDots() {
            return this.advantages.reduce((sum, adv) => sum + (adv.dots || 0), 0);
        },

        // Flaws
        addFlaw() {
            this.flaws.push({ type: '', description: '', dots: 1 });
            this.autoSave();
        },

        removeFlaw(index) {
            this.flaws.splice(index, 1);
            this.autoSave();
        },

        getFlawTotalDots() {
            return this.flaws.reduce((sum, flaw) => sum + (flaw.dots || 0), 0);
        },

        // Experience
        addXP() {
            const amount = parseInt(prompt('How much XP to add?'));
            if (!amount || amount <= 0) return;

            const reason = prompt('Reason for XP gain:') || 'Session reward';
            const date = new Date().toISOString().split('T')[0];

            this.xpLog.push({ date, type: 'add', amount, reason });
            this.data.exp_total += amount;
            this.data.exp_available += amount;
            this.autoSave();
        },

        spendXP() {
            const amount = parseInt(prompt('How much XP to spend?'));
            if (!amount || amount <= 0) return;
            if (amount > this.data.exp_available) {
                alert('Not enough available XP!');
                return;
            }

            const reason = prompt('What did you spend XP on?') || 'Character improvement';
            const date = new Date().toISOString().split('T')[0];

            this.xpLog.push({ date, type: 'spend', amount, reason });
            this.data.exp_spent += amount;
            this.data.exp_available -= amount;
            this.autoSave();
        },

        // Portrait upload
        async uploadPortrait(event, boxType) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('box_type', boxType);

            try {
                const response = await fetch(`/htr/character/${this.characterId}/upload-portrait`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Upload failed');
                }

                const result = await response.json();
                if (result.portrait_url) {
                    this.data[`portrait_${boxType}`] = result.portrait_url + `?v=${Date.now()}`;
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Failed to upload portrait. Please try again.');
            }
        },

        // Blood type warning
        isRareBloodType() {
            const rareTypes = ['AB-', 'B-', 'A-', 'O-'];
            return rareTypes.includes(this.data.blood_type);
        },

        // Utility
        capitalize(str) {
            if (str === 'drive_skill') return 'Drive';
            if (str === 'animal_ken') return 'Animal Ken';
            return str.split('_').map(word =>
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        },

        // Auto-resize textareas
        setupTextareaAutoResize() {
            // Create auto-resize function
            const autoResize = (textarea) => {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            };

            // Get all textareas in the document
            const resizeAllTextareas = () => {
                const textareas = document.querySelectorAll('textarea');
                textareas.forEach(textarea => {
                    // Skip textareas that shouldn't auto-resize (if any)
                    // For now, resize all textareas

                    // Remove old listener if it exists to avoid duplicates
                    textarea.removeEventListener('input', textarea._autoResizeHandler);

                    // Create bound handler
                    textarea._autoResizeHandler = () => autoResize(textarea);

                    // Initial resize
                    autoResize(textarea);

                    // Add input listener
                    textarea.addEventListener('input', textarea._autoResizeHandler);
                });
            };

            // Initial resize
            resizeAllTextareas();

            // Watch for changes in arrays that might add/remove textareas
            this.$watch('advantages', () => setTimeout(resizeAllTextareas, 50), { deep: true });
            this.$watch('flaws', () => setTimeout(resizeAllTextareas, 50), { deep: true });
            this.$watch('touchstones', () => setTimeout(resizeAllTextareas, 50), { deep: true });
            this.$watch('equipment', () => setTimeout(resizeAllTextareas, 50), { deep: true });

            // Watch for data changes that update textarea content
            this.$watch('data', () => setTimeout(resizeAllTextareas, 50), { deep: true });
        }
    };
}
