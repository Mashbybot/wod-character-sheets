"""Pydantic schemas for request/response validation"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    discord_id: str
    discord_username: str
    discord_avatar: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== TOUCHSTONE SCHEMAS =====

class TouchstoneBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    conviction: Optional[str] = None


class TouchstoneCreate(TouchstoneBase):
    pass


class TouchstoneUpdate(TouchstoneBase):
    name: Optional[str] = Field(None, max_length=100)


class TouchstoneResponse(TouchstoneBase):
    id: int
    character_id: int
    
    class Config:
        from_attributes = True


# ===== BACKGROUND SCHEMAS =====

class BackgroundBase(BaseModel):
    type: str = Field(..., max_length=100)
    description: Optional[str] = None
    dots: int = Field(default=0, ge=0, le=5)


class BackgroundCreate(BackgroundBase):
    pass


class BackgroundUpdate(BackgroundBase):
    type: Optional[str] = Field(None, max_length=100)
    dots: Optional[int] = Field(None, ge=0, le=5)


class BackgroundResponse(BackgroundBase):
    id: int
    character_id: int
    
    class Config:
        from_attributes = True


# ===== XP LOG SCHEMAS =====

class XPLogEntryBase(BaseModel):
    date: str
    type: str = Field(..., pattern="^(add|spend)$")
    amount: int = Field(..., gt=0)
    reason: str


class XPLogEntryCreate(XPLogEntryBase):
    pass


class XPLogEntryResponse(XPLogEntryBase):
    id: int
    character_id: int
    
    class Config:
        from_attributes = True


# ===== VTM CHARACTER SCHEMAS =====

class VTMCharacterBase(BaseModel):
    # Chronicle Information
    name: Optional[str] = Field(None, max_length=100)
    chronicle: Optional[str] = Field(None, max_length=100)
    concept: Optional[str] = Field(None, max_length=200)
    predator: Optional[str] = Field(None, max_length=50)
    ambition: Optional[str] = None
    desire: Optional[str] = None
    
    # Appearance & Identity
    apparent_age: Optional[str] = Field(None, max_length=50)
    true_age: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[str] = Field(None, max_length=50)
    date_of_death: Optional[str] = Field(None, max_length=50)
    appearance: Optional[str] = None
    distinguishing_features: Optional[str] = None
    pronouns: Optional[str] = Field(None, max_length=50)
    ethnicity: Optional[str] = Field(None, max_length=100)
    languages: Optional[str] = None
    birthplace: Optional[str] = Field(None, max_length=100)
    
    # Identity
    clan: Optional[str] = Field(None, max_length=50)
    sire: Optional[str] = Field(None, max_length=100)
    generation: Optional[int] = Field(None, ge=1, le=16)
    bane_type: Optional[str] = Field(None, max_length=100)
    bane_custom: Optional[str] = Field(None, max_length=200)
    compulsion: Optional[str] = Field(None, max_length=100)
    compulsion_custom: Optional[str] = Field(None, max_length=200)
    
    # Attributes (1-5)
    strength: Optional[int] = Field(None, ge=1, le=5)
    dexterity: Optional[int] = Field(None, ge=1, le=5)
    stamina: Optional[int] = Field(None, ge=1, le=5)
    charisma: Optional[int] = Field(None, ge=1, le=5)
    manipulation: Optional[int] = Field(None, ge=1, le=5)
    composure: Optional[int] = Field(None, ge=1, le=5)
    intelligence: Optional[int] = Field(None, ge=1, le=5)
    wits: Optional[int] = Field(None, ge=1, le=5)
    resolve: Optional[int] = Field(None, ge=1, le=5)
    
    # Skills (0-5)
    athletics: Optional[int] = Field(None, ge=0, le=5)
    brawl: Optional[int] = Field(None, ge=0, le=5)
    craft: Optional[int] = Field(None, ge=0, le=5)
    drive: Optional[int] = Field(None, ge=0, le=5)
    firearms: Optional[int] = Field(None, ge=0, le=5)
    larceny: Optional[int] = Field(None, ge=0, le=5)
    melee: Optional[int] = Field(None, ge=0, le=5)
    stealth: Optional[int] = Field(None, ge=0, le=5)
    survival: Optional[int] = Field(None, ge=0, le=5)
    animal_ken: Optional[int] = Field(None, ge=0, le=5)
    etiquette: Optional[int] = Field(None, ge=0, le=5)
    insight: Optional[int] = Field(None, ge=0, le=5)
    intimidation: Optional[int] = Field(None, ge=0, le=5)
    leadership: Optional[int] = Field(None, ge=0, le=5)
    performance: Optional[int] = Field(None, ge=0, le=5)
    persuasion: Optional[int] = Field(None, ge=0, le=5)
    streetwise: Optional[int] = Field(None, ge=0, le=5)
    subterfuge: Optional[int] = Field(None, ge=0, le=5)
    academics: Optional[int] = Field(None, ge=0, le=5)
    awareness: Optional[int] = Field(None, ge=0, le=5)
    finance: Optional[int] = Field(None, ge=0, le=5)
    investigation: Optional[int] = Field(None, ge=0, le=5)
    medicine: Optional[int] = Field(None, ge=0, le=5)
    occult: Optional[int] = Field(None, ge=0, le=5)
    politics: Optional[int] = Field(None, ge=0, le=5)
    science: Optional[int] = Field(None, ge=0, le=5)
    technology: Optional[int] = Field(None, ge=0, le=5)
    
    skill_specialties: Optional[str] = None
    
    # Trackers
    hunger: Optional[int] = Field(None, ge=0, le=5)
    resonance: Optional[str] = Field(None, max_length=200)
    
    blood_potency: Optional[int] = Field(None, ge=0, le=10)
    
    health_max: Optional[int] = Field(None, ge=1, le=10)
    health_superficial: Optional[int] = Field(None, ge=0, le=10)
    health_aggravated: Optional[int] = Field(None, ge=0, le=10)
    
    willpower_max: Optional[int] = Field(None, ge=1, le=10)
    willpower_superficial: Optional[int] = Field(None, ge=0, le=10)
    willpower_aggravated: Optional[int] = Field(None, ge=0, le=10)
    
    humanity_current: Optional[int] = Field(None, ge=0, le=10)
    humanity_stained: Optional[int] = Field(None, ge=0, le=10)
    
    # Experience
    exp_total: Optional[int] = Field(None, ge=0)
    exp_spent: Optional[int] = Field(None, ge=0)
    exp_available: Optional[int] = Field(None, ge=0)
    
    # Portraits
    portrait_face: Optional[str] = Field(None, max_length=500)
    portrait_body: Optional[str] = Field(None, max_length=500)
    portrait_hobby_1: Optional[str] = Field(None, max_length=500)
    portrait_hobby_2: Optional[str] = Field(None, max_length=500)
    portrait_hobby_3: Optional[str] = Field(None, max_length=500)
    portrait_hobby_4: Optional[str] = Field(None, max_length=500)
    alias: Optional[str] = Field(None, max_length=100)
    
    # Disciplines are stored via the Discipline relationship table
    # (no longer denormalized on VTMCharacter)

    # Chronicle Tenets (5 individual fields)
    chronicle_tenet_1: Optional[str] = Field(None, max_length=200)
    chronicle_tenet_2: Optional[str] = Field(None, max_length=200)
    chronicle_tenet_3: Optional[str] = Field(None, max_length=200)
    chronicle_tenet_4: Optional[str] = Field(None, max_length=200)
    chronicle_tenet_5: Optional[str] = Field(None, max_length=200)
    
    # History
    history_in_life: Optional[str] = None
    after_death: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('health_superficial', 'health_aggravated')
    def validate_health_damage(cls, v, values):
        """Ensure total damage doesn't exceed max health"""
        if 'health_max' in values and values['health_max']:
            health_max = values['health_max']
            superficial = values.get('health_superficial', 0) or 0
            aggravated = values.get('health_aggravated', 0) or 0
            if superficial + aggravated > health_max:
                raise ValueError('Total health damage cannot exceed maximum health')
        return v
    
    @validator('willpower_superficial', 'willpower_aggravated')
    def validate_willpower_damage(cls, v, values):
        """Ensure total damage doesn't exceed max willpower"""
        if 'willpower_max' in values and values['willpower_max']:
            willpower_max = values['willpower_max']
            superficial = values.get('willpower_superficial', 0) or 0
            aggravated = values.get('willpower_aggravated', 0) or 0
            if superficial + aggravated > willpower_max:
                raise ValueError('Total willpower damage cannot exceed maximum willpower')
        return v
    
    @validator('exp_available')
    def validate_exp_available(cls, v, values):
        """Ensure available XP = total - spent"""
        if 'exp_total' in values and 'exp_spent' in values:
            if values['exp_total'] and values['exp_spent']:
                calculated = values['exp_total'] - values['exp_spent']
                if v != calculated:
                    return calculated  # Auto-correct
        return v


class VTMCharacterCreate(VTMCharacterBase):
    """Schema for creating a new character - name is required"""
    name: str = Field(..., max_length=100)


class VTMCharacterUpdate(VTMCharacterBase):
    """Schema for updating a character - all fields optional"""
    pass


class VTMCharacterResponse(VTMCharacterBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    touchstones: List[TouchstoneResponse] = []
    backgrounds: List[BackgroundResponse] = []
    xp_log: List[XPLogEntryResponse] = []
    
    class Config:
        from_attributes = True


# ===== USER PREFERENCES SCHEMAS =====

class UserPreferencesBase(BaseModel):
    column_widths_above: str = Field(default="30,35,35", max_length=50)
    column_widths_below: str = Field(default="33,33,34", max_length=50)
    theme: Optional[str] = Field(default="dark", max_length=20)
    
    @validator('column_widths_above', 'column_widths_below')
    def validate_column_widths(cls, v):
        """Ensure column widths are valid percentages"""
        try:
            widths = [int(w.strip()) for w in v.split(',')]
            if len(widths) != 3:
                raise ValueError('Must have exactly 3 column widths')
            if sum(widths) != 100:
                raise ValueError('Column widths must sum to 100')
            if any(w < 10 or w > 70 for w in widths):
                raise ValueError('Each column must be between 10% and 70%')
            return v
        except (ValueError, AttributeError):
            raise ValueError('Invalid column width format')


class UserPreferencesCreate(UserPreferencesBase):
    pass


class UserPreferencesUpdate(UserPreferencesBase):
    column_widths_above: Optional[str] = Field(None, max_length=50)
    column_widths_below: Optional[str] = Field(None, max_length=50)
    theme: Optional[str] = Field(None, max_length=20)


class UserPreferencesResponse(UserPreferencesBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


# ===== ERROR RESPONSE SCHEMAS =====

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
    status_code: int
