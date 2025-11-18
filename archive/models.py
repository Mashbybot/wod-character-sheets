"""Database models for World of Darkness character sheets"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model - Discord OAuth authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    discord_username = Column(String, nullable=False)
    discord_avatar = Column(String)  # Avatar hash from Discord
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vtm_characters = relationship("VTMCharacter", back_populates="user", cascade="all, delete-orphan")
    htr_characters = relationship("HTRCharacter", back_populates="user", cascade="all, delete-orphan")


class VTMCharacter(Base):
    """Vampire: The Masquerade 5e Character Sheet"""
    __tablename__ = "vtm_characters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="vtm_characters")
    
    # TOP LEFT - Chronicle Information
    name = Column(String(100))
    chronicle = Column(String(100))
    
    concept = Column(String(200))
    predator = Column(String(50))  # Predator type
    ambition = Column(Text)
    desire = Column(Text)
    
    # Appearance & Features section
    apparent_age = Column(String(50))
    true_age = Column(String(50))
    date_of_birth = Column(String(50))
    date_of_death = Column(String(50))
    appearance = Column(Text)
    
    distinguishing_features = Column(Text)
    
    # Identity info
    pronouns = Column(String(50))
    ethnicity = Column(String(100))
    languages = Column(Text)
    birthplace = Column(String(100))
    
    # CENTER - Character Portrait
    portrait_url = Column(String(500))  # Path to uploaded image in Railway Volume
    
    # TOP RIGHT - Tracker Section
    clan = Column(String(50))
    generation = Column(Integer, default=13)
    
    # Bane information
    bane_type = Column(String(100))  # "Bane of [Clan]"
    bane_severity = Column(Integer, default=1)  # 1-5
    bane_description = Column(Text)
    
    # Compulsion
    compulsion = Column(Text)
    
    # Health, Willpower, Humanity (tracking as integers, UI will render as boxes)
    health_max = Column(Integer, default=6)
    health_superficial = Column(Integer, default=0)  # Marked boxes
    health_aggravated = Column(Integer, default=0)   # X'd boxes
    
    willpower_max = Column(Integer, default=5)
    willpower_superficial = Column(Integer, default=0)
    willpower_aggravated = Column(Integer, default=0)
    
    humanity_current = Column(Integer, default=7)
    humanity_max = Column(Integer, default=10)
    
    # Blood Potency section
    blood_potency = Column(Integer, default=0)  # 0-10
    blood_surge = Column(Integer, default=1)    # Based on BP
    mend_amount = Column(Integer, default=1)    # Based on BP
    power_bonus = Column(Integer, default=0)    # Based on BP
    rouse_reroll = Column(Integer, default=0)   # Based on BP
    feeding_penalty = Column(Integer, default=0) # Based on BP
    bane_severity_bp = Column(Integer, default=0) # Based on BP (redundant with bane_severity?)
    
    # Hunger (0-5)
    hunger = Column(Integer, default=1)
    
    # Resonance (text field for current resonance)
    resonance = Column(String(200))
    
    # ATTRIBUTES (left column, dots 1-5)
    # Physical
    strength = Column(Integer, default=1)
    dexterity = Column(Integer, default=1)
    stamina = Column(Integer, default=1)
    
    # Social
    charisma = Column(Integer, default=1)
    manipulation = Column(Integer, default=1)
    composure = Column(Integer, default=1)
    
    # Mental
    intelligence = Column(Integer, default=1)
    wits = Column(Integer, default=1)
    resolve = Column(Integer, default=1)
    
    # SKILLS (right column, dots 0-5)
    # Physical Skills
    athletics = Column(Integer, default=0)
    brawl = Column(Integer, default=0)
    craft = Column(Integer, default=0)
    drive = Column(Integer, default=0)
    firearms = Column(Integer, default=0)
    larceny = Column(Integer, default=0)
    melee = Column(Integer, default=0)
    stealth = Column(Integer, default=0)
    survival = Column(Integer, default=0)
    
    # Social Skills
    animal_ken = Column(Integer, default=0)
    etiquette = Column(Integer, default=0)
    insight = Column(Integer, default=0)
    intimidation = Column(Integer, default=0)
    leadership = Column(Integer, default=0)
    performance = Column(Integer, default=0)
    persuasion = Column(Integer, default=0)
    streetwise = Column(Integer, default=0)
    subterfuge = Column(Integer, default=0)
    
    # Mental Skills
    academics = Column(Integer, default=0)
    awareness = Column(Integer, default=0)
    finance = Column(Integer, default=0)
    investigation = Column(Integer, default=0)
    medicine = Column(Integer, default=0)
    occult = Column(Integer, default=0)
    politics = Column(Integer, default=0)
    science = Column(Integer, default=0)
    technology = Column(Integer, default=0)
    
    # Skill Specialties (comma-separated text fields)
    skill_specialties = Column(Text)  # Format: "skill:specialty,skill:specialty"
    
    # EXPERIENCE TRACKING
    exp_total = Column(Integer, default=0)
    exp_available = Column(Integer, default=0)
    exp_spent = Column(Integer, default=0)
    
    # BOTTOM LEFT SECTION
    # Touchstones (up to 5, storing as JSON-like text for now)
    touchstone_1_name = Column(String(100))
    touchstone_1_description = Column(Text)
    touchstone_1_conviction = Column(Text)
    
    touchstone_2_name = Column(String(100))
    touchstone_2_description = Column(Text)
    touchstone_2_conviction = Column(Text)
    
    touchstone_3_name = Column(String(100))
    touchstone_3_description = Column(Text)
    touchstone_3_conviction = Column(Text)
    
    touchstone_4_name = Column(String(100))
    touchstone_4_description = Column(Text)
    touchstone_4_conviction = Column(Text)
    
    touchstone_5_name = Column(String(100))
    touchstone_5_description = Column(Text)
    touchstone_5_conviction = Column(Text)
    
    # Chronicle Tenets (text list)
    chronicle_tenets = Column(Text)
    
    # Backgrounds, Merits & Flaws
    background_type_1 = Column(String(100))
    background_description_1 = Column(Text)
    
    background_type_2 = Column(String(100))
    background_description_2 = Column(Text)
    
    background_type_3 = Column(String(100))
    background_description_3 = Column(Text)
    
    background_type_4 = Column(String(100))
    background_description_4 = Column(Text)
    
    background_type_5 = Column(String(100))
    background_description_5 = Column(Text)
    
    background_type_6 = Column(String(100))
    background_description_6 = Column(Text)
    
    # Notes section (freeform)
    notes = Column(Text)
    
    # CENTER BOTTOM - History in Life
    history_in_life = Column(Text)
    
    # After Death section
    after_death = Column(Text)
    
    # RIGHT SIDE - Disciplines
    # Each discipline can have multiple powers, storing as structured text
    discipline_1_name = Column(String(50))
    discipline_1_level = Column(Integer, default=0)  # Dots 0-5
    discipline_1_powers = Column(Text)  # Comma-separated list of powers
    discipline_1_description = Column(Text)
    
    discipline_2_name = Column(String(50))
    discipline_2_level = Column(Integer, default=0)
    discipline_2_powers = Column(Text)
    discipline_2_description = Column(Text)
    
    discipline_3_name = Column(String(50))
    discipline_3_level = Column(Integer, default=0)
    discipline_3_powers = Column(Text)
    discipline_3_description = Column(Text)
    
    discipline_4_name = Column(String(50))
    discipline_4_level = Column(Integer, default=0)
    discipline_4_powers = Column(Text)
    discipline_4_description = Column(Text)
    
    discipline_5_name = Column(String(50))
    discipline_5_level = Column(Integer, default=0)
    discipline_5_powers = Column(Text)
    discipline_5_description = Column(Text)
    
    def __repr__(self):
        return f"<VTMCharacter {self.name} ({self.clan})>"


class HTRCharacter(Base):
    """Hunter: The Reckoning 5e Character Sheet (placeholder for future implementation)"""
    __tablename__ = "htr_characters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="htr_characters")
    
    # Basic fields - will be expanded when HTR implementation begins
    name = Column(String(100))
    concept = Column(String(200))
    creed = Column(String(50))
    
    # Portrait
    portrait_url = Column(String(500))
    
    # Placeholder for full HTR5e mechanics
    character_data = Column(Text)  # JSON storage for future expansion
    
    def __repr__(self):
        return f"<HTRCharacter {self.name} ({self.creed})>"
