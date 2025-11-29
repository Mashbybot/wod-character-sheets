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
        edges: [],
        data: {
            // Header
            name: '',
            cell: '',
            chronicle: '',
            creed: '',
            drive: '',

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
            selected_edges: '',  // JSON array of edge IDs
            selected_perks: '',  // JSON array of perk IDs

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
        xpLog: [],

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
        },

        async loadEdgesData() {
            try {
                const response = await fetch('/static/data/htr_edges.json');
                const data = await response.json();
                this.edges = data.edges || [];
            } catch (error) {
                console.error('Failed to load edges data:', error);
                this.edges = [];
            }
        },

        async loadCharacter() {
            try {
                const response = await fetch(`/htr/api/character/${this.characterId}`);
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
                this.xpLog = char.xp_log || [];

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
                const payload = {
                    ...this.data,
                    touchstones: this.touchstones,
                    advantages: this.advantages,
                    flaws: this.flaws,
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
                const payload = {
                    ...this.data,
                    touchstones: this.touchstones,
                    advantages: this.advantages,
                    flaws: this.flaws,
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
            this.data[field] = value;
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
            if (index > this.data.willpower_max) return;

            const state = this.getWillpowerState(index);
            if (state === 'empty') {
                this.data.willpower_superficial++;
            } else if (state === 'superficial') {
                this.data.willpower_superficial--;
                this.data.willpower_aggravated++;
            } else if (state === 'aggravated') {
                this.data.willpower_aggravated--;
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

        // Edges & Perks
        get selectedEdgesArray() {
            try {
                return JSON.parse(this.data.selected_edges || '[]');
            } catch {
                return [];
            }
        },

        get selectedPerksArray() {
            try {
                return JSON.parse(this.data.selected_perks || '[]');
            } catch {
                return [];
            }
        },

        getEdgesByCategory(category) {
            return this.edges.filter(edge => edge.category === category);
        },

        isEdgeSelected(edgeId) {
            return this.selectedEdgesArray.includes(edgeId);
        },

        toggleEdge(edgeId) {
            let edges = this.selectedEdgesArray;

            if (edges.includes(edgeId)) {
                // Remove edge and all its perks
                edges = edges.filter(e => e !== edgeId);

                // Remove all perks associated with this edge
                const edge = this.edges.find(e => e.id === edgeId);
                if (edge && edge.perks) {
                    let perks = this.selectedPerksArray;
                    const perkIds = edge.perks.map(p => p.id);
                    perks = perks.filter(p => !perkIds.includes(p));
                    this.data.selected_perks = JSON.stringify(perks);
                }
            } else {
                edges.push(edgeId);
            }

            this.data.selected_edges = JSON.stringify(edges);
            this.autoSave();
        },

        isPerkSelected(perkId) {
            return this.selectedPerksArray.includes(perkId);
        },

        togglePerk(perkId) {
            let perks = this.selectedPerksArray;

            if (perks.includes(perkId)) {
                perks = perks.filter(p => p !== perkId);
            } else {
                perks.push(perkId);
            }

            this.data.selected_perks = JSON.stringify(perks);
            this.autoSave();
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
        }
    };
}
