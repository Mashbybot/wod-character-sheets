# Hunter: The Reckoning Character Sheet - Implementation Complete! 🔶

## Status: READY FOR TESTING

All core implementation is complete and ready for database migration and testing.

---

## 📦 What's Been Built

### 1. Database Models (`app/models_new.py`)
✅ **HTRCharacter** - Full character model with:
- Identity fields (name, cell, chronicle, creed, drive, age, blood type, pronouns, origin)
- 6 portrait slots (face, body, 4 hobbies) + graffiti alias
- 9 Attributes (Strength through Resolve)
- 27 Skills (Physical, Social, Mental) + specialties
- 4 Trackers (Danger, Desperation, Health, Willpower)
- Despair indicator (triggers overlay!)
- Edge/Perk system (1e2p or 2e1p config)
- Equipment quick stats
- XP tracking
- History fields (First Encounter, History, Notes)

✅ **HTRTouchstone** - Up to 3 touchstones per character
✅ **HTRAdvantage** - Merits with 7-dot max
✅ **HTRFlaw** - Flaws with 2-dot max
✅ **HTRXPLogEntry** - Experience tracking

### 2. Database Migration (`alembic/versions/002_add_htr_tables.py`)
✅ Comprehensive migration that:
- Expands placeholder HTR table with all fields
- Creates 4 relationship tables
- Includes rollback capability
- **READY TO RUN**

**To apply migration:**
```bash
alembic upgrade head
```

### 3. Backend Routes (`app/routes/htr.py`)
✅ Complete route mirror of VTM:
- `/htr/` - Character list
- `/htr/character/new` - Create new
- `/htr/character/{id}` - View character
- `/htr/character/{id}/edit` - Edit character
- `/htr/api/character/{id}` - JSON API
- `/htr/character/create` - Create endpoint
- `/htr/character/{id}/update` - Update endpoint (auto-save)
- `/htr/character/{id}/delete` - Delete endpoint
- `/htr/character/{id}/upload-portrait` - Portrait upload

### 4. Frontend Templates

✅ **Character List** (`templates/htr/character_list.html`)
- Grid display of characters
- Create new button
- Edit/Delete actions
- Character limit enforcement (3 max)

✅ **Character Sheet** (`templates/htr/character_sheet.html`)
- Full Hunter v5 sheet layout
- 3-column grid (25% | 50% | 25%)
- Portrait bento box with graffiti alias overlay
- 4 medical monitor trackers
- Drive-boosted skill highlighting
- Edge/Perk selection with validation
- Advantages/Flaws split tracking
- First Encounter emphasis section
- Orange caution tape page break
- Despair overlay effect

### 5. JavaScript Component (`app/static/js/htr-sheet.js`)
✅ Full Alpine.js reactive component with:
- Auto-save (debounced)
- Character creation/update
- Portrait upload
- Skill specialty management
- Edge/Perk validation logic
- Drive-boosted skill detection
- Health/Willpower cycling
- Tracker management
- XP logging
- Blood type warning
- Touchstone/Advantage/Flaw CRUD

### 6. CSS Styling (`app/static/css/htr-sheet.css`)
✅ Complete orange neumorphic theme:
- Hunter orange color palette (#FF8C00)
- Neumorphic box shadows with orange glow
- Medical tracker aesthetics
- Drive-boosted skill highlighting (🔶 + orange gradient)
- Despair overlay animation
- Bullet hole graphic styling
- Orange caution tape divider
- First Encounter emphasis border
- Responsive design
- Blood type warning badge

### 7. Data Files

✅ **Edges JSON** (`app/static/data/htr_edges.json`)
- 8 Edges with nested Perks structure
- Arsenal, Library, Logistics, Ordination, Tradecraft, Network, Preparedness, Custom
- Character creation rules embedded

✅ **Creed Boosts JSON** (`app/static/data/htr_creed_boosts.json`)
- 5 Creeds (Faithful, Inquisitive, Martial, Entrepreneurial, Underground)
- Drive-boosted skill mappings
- 5 Drives (Atonement, Justice, Legacy, Pride, Revenge)
- Skill descriptions

### 8. Asset Directories
✅ Created placeholder directories:
- `app/static/images/edges/` - For edge icons (*.webp)
- `app/static/images/htr/` - For hunter logo and assets
- `app/static/data/` - For JSON data files

---

## 🎯 Implementation Highlights

### Drive-Boosted Skills ✨
Skills automatically highlight with 🔶 icon and orange gradient based on selected Creed:
- **Faithful**: insight, medicine, occult
- **Inquisitive**: academics, investigation, science
- **Martial**: athletics, brawl, firearms
- **Entrepreneurial**: finance, persuasion, streetwise
- **Underground**: larceny, stealth, survival

### Edge/Perk System ✅
- Character creation: Choose **1 Edge + 2 Perks** OR **2 Edges + 1 Perk**
- Real-time validation with visual feedback
- Nested structure: Edges contain Perks
- Checkbox selection UI

### Medical Tracker System 🏥
Four trackers with unique aesthetics:
1. **Danger** (0-20) - Color-coded: Green → Yellow → Red
2. **Desperation** (0-20) - Warning at 15+
3. **Health** (0-10) - Cycle: Empty → Superficial (/) → Aggravated (×)
4. **Willpower** (0-10) - Same cycling as Health

### Despair Mechanic ⚠️
- Checkbox indicator
- Triggers full-screen orange pulsing overlay
- Shows bullet hole graphic when active
- Non-intrusive to gameplay

### First Encounter Section 🔶
- Orange bordered emphasis box
- 8-row textarea
- Critical field highlighting
- Placeholder prompts

### Advantages vs Flaws Split 📊
- **Advantages**: Max 7 dots total
- **Flaws**: Max 2 dots total
- Separate tracking and validation
- Running totals displayed

---

## 🚀 Next Steps

### 1. Apply Database Migration
```bash
# From project root
alembic upgrade head
```

### 2. Add Your Assets
Place your images in:
- `app/static/images/bullet-hole.png` - Despair indicator
- `app/static/images/htr/hunter-logo.png` - Hunter logo (placeholder for now)
- `app/static/images/edges/*.webp` - Edge icons (36 files)

### 3. Test Character Creation
1. Start the server: `uvicorn app.main:app --reload`
2. Navigate to `/htr`
3. Create a new character
4. Test all features:
   - Portrait uploads
   - Skill specialties
   - Edge/Perk selection
   - Tracker cycling
   - Auto-save
   - Despair overlay

### 4. Commit and Push
```bash
git add .
git commit -m "$(cat <<'EOF'
Implement Hunter: The Reckoning v5 character sheets

- Add HTRCharacter model with full HTR5e mechanics
- Create HTR relationship tables (Touchstones, Advantages, Flaws, XP)
- Implement HTR routes mirroring VTM pattern
- Build HTR character sheet with medical tracker aesthetic
- Add Drive-boosted skill highlighting
- Implement Edge/Perk selection system with validation
- Create Despair overlay mechanic
- Add orange neumorphic theme matching implementation plan
- Include First Encounter emphasis section
- Implement Advantages/Flaws split tracking
EOF
)"
git push -u origin claude/hunter-v5-sheet-016VvMmV2CaeDgCNuK6QMjGr
```

---

## 📝 Notes & Considerations

### Differences from Implementation Plan

1. **Edge/Perk Structure**: Corrected from flat list to nested structure (Edges contain Perks)
2. **Database Field**: Used `drive_skill` instead of `drive` to avoid conflict with Drive mechanic field
3. **Placeholder Assets**: Hunter logo needs to be created (you mentioned you're drawing it)

### Technical Decisions

1. **Auto-save**: Implemented with 300ms debounce for smooth UX
2. **Portrait Storage**: Uses existing VTM portrait upload system
3. **JSON Storage**: Skill specialties and selected perks stored as JSON text
4. **Validation**: Client-side Edge/Perk validation with visual feedback
5. **Responsive Design**: Mobile-friendly with breakpoints at 1200px and 768px

### Known Limitations

1. **Hunter Logo**: Placeholder needed until you create the final design
2. **Edge Icons**: Directory created, awaiting your 36 .webp files
3. **Bullet Hole**: Directory created, awaiting your PNG file

---

## 🐛 Testing Checklist

Before merging to main, verify:

- [ ] Database migration runs without errors
- [ ] Can create new HTR character
- [ ] Can edit existing HTR character
- [ ] Can delete HTR character
- [ ] Auto-save works (check "✓ Saved" indicator)
- [ ] Portrait uploads work for all 6 slots
- [ ] Graffiti alias displays correctly
- [ ] Drive-boosted skills highlight based on Creed
- [ ] Edge/Perk validation shows ✓ when valid
- [ ] Advantages total cannot exceed 7 dots
- [ ] Flaws total cannot exceed 2 dots
- [ ] Health tracker cycles: Empty → / → ×
- [ ] Willpower tracker cycles correctly
- [ ] Danger tracker color-codes correctly
- [ ] Desperation shows warning at 15+
- [ ] Despair checkbox triggers orange overlay
- [ ] Blood type warning shows for AB-, B-, A-, O-
- [ ] First Encounter section has orange border
- [ ] XP Add/Spend buttons work
- [ ] Skill specialties can be added/removed
- [ ] Touchstones can be added (max 3)
- [ ] Character list displays all characters
- [ ] Character limit enforced (3 max)
- [ ] Back links work correctly
- [ ] Responsive design works on mobile

---

## 🎉 Summary

**Total Files Created/Modified: 12**

1. `app/models_new.py` - Expanded HTR models
2. `alembic/versions/002_add_htr_tables.py` - Migration
3. `app/routes/htr.py` - Complete routes
4. `templates/htr/character_list.html` - Character list
5. `templates/htr/character_sheet.html` - Character sheet
6. `app/static/js/htr-sheet.js` - Alpine.js component
7. `app/static/css/htr-sheet.css` - Orange neumorphic theme
8. `app/static/data/htr_edges.json` - Edges with nested perks
9. `app/static/data/htr_creed_boosts.json` - Creed/Drive data
10. `app/static/images/edges/` - Directory created
11. `app/static/images/htr/` - Directory created
12. `HTR_IMPLEMENTATION_SUMMARY.md` - This file

**Lines of Code: ~2500+**

**Ready to test!** 🚀

---

*Implementation completed on branch: `claude/hunter-v5-sheet-016VvMmV2CaeDgCNuK6QMjGr`*
*Next step: Apply migration, test, and merge to main*
