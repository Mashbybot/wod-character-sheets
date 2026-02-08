/**
 * Shared utilities for WoD character sheet components (VTM, HTR, etc.)
 *
 * These functions are used by all game-type Alpine.js components
 * to avoid duplicating portrait upload, XP management, and UI logic.
 */

/**
 * Upload a portrait image for a character.
 * @param {string} gameType - 'vtm' or 'htr'
 * @param {number} characterId
 * @param {Event} event - file input change event
 * @param {string} boxType - 'face', 'body', 'hobby_1', etc.
 * @returns {Promise<string|null>} The new portrait URL, or null on failure
 */
async function sheetUploadPortrait(gameType, characterId, event, boxType) {
    const file = event.target.files[0];
    if (!file) return null;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('box_type', boxType);

    try {
        const response = await fetch(`/${gameType}/character/${characterId}/upload-portrait`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Portrait upload failed:', errorData);
            return null;
        }

        const result = await response.json();
        return result.portrait_url || null;
    } catch (error) {
        console.error('Portrait upload error:', error);
        return null;
    }
}

/**
 * Trigger a hidden file input click from a portrait box click.
 * Walks up to the parent container and finds the file input.
 * @param {Event} event
 */
function sheetTriggerFileUpload(event) {
    const container = event.currentTarget.parentElement;
    const fileInput = container.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.click();
    }
}

/**
 * Capitalize a snake_case field name for display.
 * Handles special cases like 'animal_ken' and 'drive_skill'.
 * @param {string} str
 * @returns {string}
 */
function sheetCapitalize(str) {
    const special = {
        'drive_skill': 'Drive',
        'animal_ken': 'Animal Ken',
    };
    if (special[str]) return special[str];
    return str.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

/**
 * Set up auto-resize behavior for all textareas in the document.
 * Watches the given Alpine.js component properties for changes that
 * might add/remove textareas.
 * @param {Object} component - Alpine.js component (this)
 * @param {string[]} watchTargets - property names to watch for textarea changes
 */
function sheetSetupTextareaAutoResize(component, watchTargets) {
    const autoResize = (textarea) => {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    };

    const resizeAllTextareas = () => {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.removeEventListener('input', textarea._autoResizeHandler);
            textarea._autoResizeHandler = () => autoResize(textarea);
            autoResize(textarea);
            textarea.addEventListener('input', textarea._autoResizeHandler);
        });
    };

    resizeAllTextareas();

    for (const target of watchTargets) {
        component.$watch(target, () => setTimeout(resizeAllTextareas, 50), { deep: true });
    }
    component.$watch('data', () => setTimeout(resizeAllTextareas, 50), { deep: true });
}

/**
 * Add XP to a character and log the entry.
 * @param {Object} data - character data object (must have exp_total, exp_spent)
 * @param {Array} xpLog - the XP log array to append to
 * @returns {boolean} true if XP was added
 */
function sheetAddXP(data, xpLog) {
    const amount = prompt('How much XP to add?');
    const reason = prompt('Reason (optional):');
    if (amount && !isNaN(amount)) {
        const xpAmount = parseInt(amount);
        data.exp_total += xpAmount;
        data.exp_available = data.exp_total - data.exp_spent;
        xpLog.push({
            date: new Date().toLocaleDateString(),
            type: 'add',
            amount: xpAmount,
            reason: reason || 'XP Award'
        });
        return true;
    }
    return false;
}

/**
 * Spend XP from a character and log the entry.
 * @param {Object} data - character data object (must have exp_total, exp_spent, exp_available)
 * @param {Array} xpLog - the XP log array to append to
 * @returns {boolean} true if XP was spent
 */
function sheetSpendXP(data, xpLog) {
    const amount = prompt('How much XP to spend?');
    const reason = prompt('What did you buy?');
    if (amount && !isNaN(amount)) {
        const spend = parseInt(amount);
        if (spend <= data.exp_available) {
            data.exp_spent += spend;
            data.exp_available = data.exp_total - data.exp_spent;
            xpLog.push({
                date: new Date().toLocaleDateString(),
                type: 'spend',
                amount: spend,
                reason: reason || 'Purchase'
            });
            return true;
        } else {
            alert('Not enough available XP!');
        }
    }
    return false;
}
