"""Database models for World of Darkness character sheets - REFACTORED"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model - Discord OAuth authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    discord_username = Column(String, nullable=False)
    discord_avatar = Column(String)
    role = Column(String(20), default="player", nullable=False, index=True)  # player, storyteller, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vtm_characters = relationship("VTMCharacter", back_populates="user", cascade="all, delete-orphan")
    htr_characters = relationship("HTRCharacter", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.discord_username}>"


class UserPreferences(Base):
    """User UI preferences - separate from character data"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Column layout preferences
    column_widths_above = Column(String(50), default="30,35,35")
    column_widths_below = Column(String(50), default="33,33,34")

    # Textarea height preferences
    history_in_life_height = Column(Integer, nullable=True)
    after_death_height = Column(Integer, nullable=True)
    notes_height = Column(Integer, nullable=True)
    ambition_height = Column(Integer, nullable=True)
    desire_height = Column(Integer, nullable=True)

    # Theme preferences
    theme = Column(String(20), default="dark")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences user_id={self.user_id}>"


class AuditLog(Base):
    """Audit log for security-relevant events"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_id = Column(Integer, nullable=True)
    target_type = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.event_type} user_id={self.user_id} at {self.timestamp}>"


class Touchstone(Base):
    """Touchstone - separate table for VTM characters"""
    __tablename__ = "touchstones"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("vtm_characters.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    conviction = Column(Text)
    
    # Order for display
    display_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    character = relationship("VTMCharacter", back_populates="touchstones")
    
    def __repr__(self):
        return f"<Touchstone {self.name}>"


class Background(Base):
    """Background, Merit, or Flaw - separate table for VTM characters"""
    __tablename__ = "backgrounds"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("vtm_characters.id"), nullable=False)

    category = Column(String(20), default="Background")  # "Merit", "Flaw", "Background", "Loresheet"
    type = Column(String(100), nullable=False)  # e.g., "Resources", "Fame", "Haven"
    description = Column(Text)
    dots = Column(Integer, default=0)  # 0-5 rating
    description_height = Column(Integer, default=60)  # Save textarea height in pixels

    # Order for display
    display_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    character = relationship("VTMCharacter", back_populates="backgrounds")
    
    def __repr__(self):
        return f"<Background {self.type} ({self.dots} dots)>"


class Discipline(Base):
    """Discipline - separate table for VTM characters"""
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("vtm_characters.id"), nullable=False)

    name = Column(String(100), nullable=False)  # e.g., "animalism", "auspex", "dominate"
    level = Column(Integer, default=0)  # 0-5 rating
    powers = Column(Text)  # List of powers
    description = Column(Text)  # Notes about the discipline

    # Order for display
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    character = relationship("VTMCharacter", back_populates="disciplines")

    def __repr__(self):
        return f"<Discipline {self.name} (Level {self.level})>"


class XPLogEntry(Base):
    """Experience log entry - separate table for VTM characters"""
    __tablename__ = "xp_log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("vtm_characters.id"), nullable=False)
    
    date = Column(String(50), nullable=False)  # ISO date string
    type = Column(String(10), nullable=False)  # 'add' or 'spend'
    amount = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    
    # Order for display (newest first)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    character = relationship("VTMCharacter", back_populates="xp_log")
    
    def __repr__(self):
        return f"<XPLogEntry {self.type} {self.amount} XP>"


class VTMCharacter(Base):
    """Vampire: The Masquerade 5e Character Sheet - REFACTORED"""
    __tablename__ = "vtm_characters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="vtm_characters")
    touchstones = relationship("Touchstone", back_populates="character", cascade="all, delete-orphan", order_by="Touchstone.display_order")
    backgrounds = relationship("Background", back_populates="character", cascade="all, delete-orphan", order_by="Background.display_order")
    disciplines = relationship("Discipline", back_populates="character", cascade="all, delete-orphan", order_by="Discipline.display_order")
    xp_log = relationship("XPLogEntry", back_populates="character", cascade="all, delete-orphan", order_by="XPLogEntry.created_at.desc()")
    
    # TOP LEFT - Chronicle Information
    name = Column(String(100))
    chronicle = Column(String(100))
    
    concept = Column(String(200))
    predator = Column(String(50))
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
    
    # CENTER - Character Portraits (6 slots)
    portrait_face = Column(String(500))
    portrait_body = Column(String(500))
    portrait_hobby_1 = Column(String(500))
    portrait_hobby_2 = Column(String(500))
    portrait_hobby_3 = Column(String(500))
    portrait_hobby_4 = Column(String(500))
    alias = Column(String(100))
    
    # TOP RIGHT - Tracker Section
    clan = Column(String(50))
    sire = Column(String(100))
    generation = Column(Integer, default=13)
    
    # Bane information
    bane_type = Column(String(100))
    bane_custom = Column(String(200))
    
    # Compulsion
    compulsion = Column(String(100))
    compulsion_custom = Column(String(200))
    
    # Health, Willpower, Humanity
    health_max = Column(Integer, default=6)
    health_superficial = Column(Integer, default=0)
    health_aggravated = Column(Integer, default=0)
    
    willpower_max = Column(Integer, default=5)
    willpower_superficial = Column(Integer, default=0)
    willpower_aggravated = Column(Integer, default=0)
    
    humanity_current = Column(Integer, default=7)
    humanity_stained = Column(Integer, default=0)
    
    # Blood Potency section
    blood_potency = Column(Integer, default=0)
    
    # Hunger (0-5)
    hunger = Column(Integer, default=1)
    
    # Resonance
    resonance = Column(String(200))
    
    # ATTRIBUTES (1-5)
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
    
    # SKILLS (0-5)
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
    
    # Skill Specialties (comma-separated)
    skill_specialties = Column(Text)
    
    # EXPERIENCE TRACKING
    exp_total = Column(Integer, default=0)
    exp_available = Column(Integer, default=0)
    exp_spent = Column(Integer, default=0)
    
    # Chronicle Tenets (5 individual fields)
    chronicle_tenet_1 = Column(String(200))
    chronicle_tenet_2 = Column(String(200))
    chronicle_tenet_3 = Column(String(200))
    chronicle_tenet_4 = Column(String(200))
    chronicle_tenet_5 = Column(String(200))
    
    # Notes section (freeform)
    notes = Column(Text)
    
    # CENTER BOTTOM - History in Life
    history_in_life = Column(Text)
    
    # After Death section
    after_death = Column(Text)
    
    # RIGHT SIDE - Disciplines (5 slots)
    discipline_1_name = Column(String(50))
    discipline_1_level = Column(Integer, default=0)
    discipline_1_powers = Column(Text)
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


class HTRTouchstone(Base):
    """Touchstone - separate table for HTR characters"""
    __tablename__ = "htr_touchstones"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Order for display
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    character = relationship("HTRCharacter", back_populates="touchstones")

    def __repr__(self):
        return f"<HTRTouchstone {self.name}>"


class HTRAdvantage(Base):
    """Advantages/Merits - separate table for HTR characters (max 7 dots total)"""
    __tablename__ = "htr_advantages"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    type = Column(String(100), nullable=False)  # e.g., "Resources", "Contacts", "Allies"
    description = Column(Text)
    dots = Column(Integer, default=1)  # 1-5 rating

    # Order for display
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    character = relationship("HTRCharacter", back_populates="advantages")

    def __repr__(self):
        return f"<HTRAdvantage {self.type} ({self.dots} dots)>"


class HTRFlaw(Base):
    """Flaws - separate table for HTR characters (max 2 dots total)"""
    __tablename__ = "htr_flaws"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    type = Column(String(100), nullable=False)  # e.g., "Enemy", "Dark Secret"
    description = Column(Text)
    dots = Column(Integer, default=1)  # 1-5 rating

    # Order for display
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    character = relationship("HTRCharacter", back_populates="flaws")

    def __repr__(self):
        return f"<HTRFlaw {self.type} ({self.dots} dots)>"


class HTRXPLogEntry(Base):
    """Experience log entry - separate table for HTR characters"""
    __tablename__ = "htr_xp_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    date = Column(String(50), nullable=False)  # ISO date string
    type = Column(String(10), nullable=False)  # 'add' or 'spend'
    amount = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)

    # Order for display (newest first)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    character = relationship("HTRCharacter", back_populates="xp_log")

    def __repr__(self):
        return f"<HTRXPLogEntry {self.type} {self.amount} XP>"


class HTREdge(Base):
    """Edges - separate table for HTR characters"""
    __tablename__ = "htr_edges"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    edge_id = Column(String(100), nullable=False)  # e.g., 'arsenal', 'fleet'
    display_order = Column(Integer, default=0)

    # Relationship
    character = relationship("HTRCharacter", back_populates="edges")

    def __repr__(self):
        return f"<HTREdge {self.edge_id}>"


class HTRPerk(Base):
    """Perks - separate table for HTR characters"""
    __tablename__ = "htr_perks"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    edge_id = Column(String(100), nullable=False)  # Which edge this perk belongs to
    perk_id = Column(String(100), nullable=False)  # e.g., 'team-requisition'
    display_order = Column(Integer, default=0)

    # Relationship
    character = relationship("HTRCharacter", back_populates="perks")

    def __repr__(self):
        return f"<HTRPerk {self.perk_id} (Edge: {self.edge_id})>"


class HTREquipment(Base):
    """Equipment - separate table for HTR characters"""
    __tablename__ = "htr_equipment"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("htr_characters.id"), nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    character = relationship("HTRCharacter", back_populates="equipment")

    def __repr__(self):
        return f"<HTREquipment {self.name}>"


class HTRCharacter(Base):
    """Hunter: The Reckoning 5e Character Sheet"""
    __tablename__ = "htr_characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="htr_characters")
    touchstones = relationship("HTRTouchstone", back_populates="character", cascade="all, delete-orphan", order_by="HTRTouchstone.display_order")
    advantages = relationship("HTRAdvantage", back_populates="character", cascade="all, delete-orphan", order_by="HTRAdvantage.display_order")
    flaws = relationship("HTRFlaw", back_populates="character", cascade="all, delete-orphan", order_by="HTRFlaw.display_order")
    edges = relationship("HTREdge", back_populates="character", cascade="all, delete-orphan", order_by="HTREdge.display_order")
    perks = relationship("HTRPerk", back_populates="character", cascade="all, delete-orphan", order_by="HTRPerk.display_order")
    equipment = relationship("HTREquipment", back_populates="character", cascade="all, delete-orphan", order_by="HTREquipment.display_order")
    xp_log = relationship("HTRXPLogEntry", back_populates="character", cascade="all, delete-orphan", order_by="HTRXPLogEntry.created_at.desc()")

    # HEADER - Chronicle Information
    name = Column(String(100))
    cell = Column(String(100))  # Cell/group name
    chronicle = Column(String(100))

    # IDENTITY
    creed = Column(String(50))  # faithful, inquisitive, martial, entrepreneurial, underground
    drive = Column(String(50))  # atonement, justice, legacy, pride, revenge
    desire = Column(Text)  # Short-term goal or momentary want
    ambition = Column(Text)  # Long-term goal

    # Personal Info
    age = Column(String(50))
    blood_type = Column(String(10))
    pronouns = Column(String(50))
    origin = Column(String(100))

    # CHARACTER PORTRAITS (6 slots)
    portrait_face = Column(String(500))
    portrait_body = Column(String(500))
    portrait_hobby_1 = Column(String(500))
    portrait_hobby_2 = Column(String(500))
    portrait_hobby_3 = Column(String(500))
    portrait_hobby_4 = Column(String(500))
    alias = Column(String(100))  # Graffiti alias

    # ATTRIBUTES (1-5)
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

    # SKILLS (0-5)
    # Physical Skills
    athletics = Column(Integer, default=0)
    brawl = Column(Integer, default=0)
    craft = Column(Integer, default=0)
    drive_skill = Column(Integer, default=0)  # Renamed from 'drive' to avoid conflict with Drive mechanic
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

    # Skill Specialties (JSON stored as text)
    skill_specialties = Column(Text)

    # TRACKERS
    danger_current = Column(Integer, default=0)  # 0-20
    desperation_current = Column(Integer, default=0)  # 0-20

    health_max = Column(Integer, default=6)
    health_superficial = Column(Integer, default=0)
    health_aggravated = Column(Integer, default=0)

    willpower_max = Column(Integer, default=5)
    willpower_superficial = Column(Integer, default=0)
    willpower_aggravated = Column(Integer, default=0)

    in_despair = Column(Boolean, default=False)  # Triggers overlay!

    # EDGES & PERKS
    # DEPRECATED: Old edge/perk system - replaced by edges and perks relationships
    # Kept for backward compatibility during migration
    edge_config = Column(String(10), default='1e2p')  # '1e2p' or '2e1p'
    edge_1_id = Column(String(50))  # e.g., 'arsenal'
    edge_2_id = Column(String(50))  # null if only 1 edge chosen
    selected_perks = Column(Text)  # JSON array: ["well-armed", "ordnance"]
    # NEW: Use character.edges and character.perks relationships instead

    # EQUIPMENT
    equipment_weapon = Column(String(100))
    equipment_weapon_damage = Column(Integer, default=0)
    equipment_armor_rating = Column(Integer, default=0)
    equipment_notes = Column(Text)

    # EXPERIENCE TRACKING
    exp_total = Column(Integer, default=0)
    exp_available = Column(Integer, default=0)
    exp_spent = Column(Integer, default=0)

    # HISTORY & NOTES
    first_encounter = Column(Text)  # CRITICAL FIELD - defining moment
    history = Column(Text)
    notes = Column(Text)
    current_mission = Column(Text)

    # CHARACTER CREATION
    creation_complete = Column(Boolean, default=False)

    def __repr__(self):
        return f"<HTRCharacter {self.name} ({self.creed})>"
