#!/usr/bin/env python3
"""
Utility script to fix double-encoded HTML entities in the database.

This fixes touchstone names and other fields that were double/triple encoded
due to the old sanitization bug.

Run with: python3 fix_double_encoding.py
"""

import html
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models_new import HTRTouchstone, Touchstone, HTRAdvantage, HTRFlaw, Background, HTRCharacter, VTMCharacter


def unescape_field(value: str) -> str:
    """
    Recursively unescape HTML entities until we get the original text.

    Example:
        &amp;quot;Brad&amp;quot; -> &quot;Brad&quot; -> "Brad"
    """
    if not value or not isinstance(value, str):
        return value

    # Keep unescaping until the string stops changing (handles multiple layers)
    prev = None
    current = value
    max_iterations = 10  # Safety limit
    iterations = 0

    while prev != current and iterations < max_iterations:
        prev = current
        current = html.unescape(current)
        iterations += 1

    return current


def fix_touchstones(db: Session, dry_run: bool = True):
    """Fix VTM touchstones"""
    touchstones = db.query(Touchstone).all()
    fixed_count = 0

    print(f"\nProcessing {len(touchstones)} VTM touchstones...")

    for ts in touchstones:
        original_name = ts.name
        original_desc = ts.description
        original_conv = ts.conviction

        # Unescape fields
        ts.name = unescape_field(ts.name)
        ts.description = unescape_field(ts.description)
        ts.conviction = unescape_field(ts.conviction)

        if (ts.name != original_name or
            ts.description != original_desc or
            ts.conviction != original_conv):

            fixed_count += 1
            print(f"  Fixed touchstone ID {ts.id}:")
            if ts.name != original_name:
                print(f"    Name: {original_name[:50]} -> {ts.name[:50]}")

            if not dry_run:
                db.add(ts)

    return fixed_count


def fix_htr_touchstones(db: Session, dry_run: bool = True):
    """Fix HTR touchstones"""
    touchstones = db.query(HTRTouchstone).all()
    fixed_count = 0

    print(f"\nProcessing {len(touchstones)} HTR touchstones...")

    for ts in touchstones:
        original_name = ts.name
        original_desc = ts.description

        ts.name = unescape_field(ts.name)
        ts.description = unescape_field(ts.description)

        if ts.name != original_name or ts.description != original_desc:
            fixed_count += 1
            print(f"  Fixed HTR touchstone ID {ts.id}:")
            if ts.name != original_name:
                print(f"    Name: {original_name[:50]} -> {ts.name[:50]}")

            if not dry_run:
                db.add(ts)

    return fixed_count


def fix_htr_advantages_flaws(db: Session, dry_run: bool = True):
    """Fix HTR advantages and flaws"""
    advantages = db.query(HTRAdvantage).all()
    flaws = db.query(HTRFlaw).all()
    fixed_count = 0

    print(f"\nProcessing {len(advantages)} HTR advantages...")
    for adv in advantages:
        original_type = adv.type
        original_desc = adv.description

        adv.type = unescape_field(adv.type)
        adv.description = unescape_field(adv.description)

        if adv.type != original_type or adv.description != original_desc:
            fixed_count += 1
            if not dry_run:
                db.add(adv)

    print(f"\nProcessing {len(flaws)} HTR flaws...")
    for flaw in flaws:
        original_type = flaw.type
        original_desc = flaw.description

        flaw.type = unescape_field(flaw.type)
        flaw.description = unescape_field(flaw.description)

        if flaw.type != original_type or flaw.description != original_desc:
            fixed_count += 1
            if not dry_run:
                db.add(flaw)

    return fixed_count


def fix_backgrounds(db: Session, dry_run: bool = True):
    """Fix VTM backgrounds"""
    backgrounds = db.query(Background).all()
    fixed_count = 0

    print(f"\nProcessing {len(backgrounds)} VTM backgrounds...")

    for bg in backgrounds:
        original_type = bg.type
        original_desc = bg.description

        bg.type = unescape_field(bg.type)
        bg.description = unescape_field(bg.description)

        if bg.type != original_type or bg.description != original_desc:
            fixed_count += 1
            if not dry_run:
                db.add(bg)

    return fixed_count


def fix_character_text_fields(db: Session, dry_run: bool = True):
    """Fix text fields in character models"""
    vtm_chars = db.query(VTMCharacter).all()
    htr_chars = db.query(HTRCharacter).all()
    fixed_count = 0

    print(f"\nProcessing {len(vtm_chars)} VTM characters...")
    text_fields = ['name', 'chronicle', 'concept', 'notes', 'history_in_life', 'after_death',
                   'ambition', 'desire', 'clan', 'sire']

    for char in vtm_chars:
        changed = False
        for field in text_fields:
            if hasattr(char, field):
                original = getattr(char, field)
                if original:
                    unescaped = unescape_field(original)
                    if unescaped != original:
                        setattr(char, field, unescaped)
                        changed = True

        if changed:
            fixed_count += 1
            if not dry_run:
                db.add(char)

    print(f"\nProcessing {len(htr_chars)} HTR characters...")
    htr_text_fields = ['name', 'chronicle', 'cell', 'notes', 'history', 'first_encounter',
                       'current_mission', 'desire', 'ambition', 'creed', 'drive', 'origin']

    for char in htr_chars:
        changed = False
        for field in htr_text_fields:
            if hasattr(char, field):
                original = getattr(char, field)
                if original:
                    unescaped = unescape_field(original)
                    if unescaped != original:
                        setattr(char, field, unescaped)
                        changed = True

        if changed:
            fixed_count += 1
            if not dry_run:
                db.add(char)

    return fixed_count


def main():
    """Run the fix"""
    import sys

    dry_run = '--apply' not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be saved")
        print("Run with --apply flag to actually fix the database")
        print("=" * 60)
    else:
        print("=" * 60)
        print("APPLYING FIXES TO DATABASE")
        print("=" * 60)

    db = SessionLocal()

    try:
        total_fixed = 0

        total_fixed += fix_touchstones(db, dry_run)
        total_fixed += fix_htr_touchstones(db, dry_run)
        total_fixed += fix_htr_advantages_flaws(db, dry_run)
        total_fixed += fix_backgrounds(db, dry_run)
        total_fixed += fix_character_text_fields(db, dry_run)

        if not dry_run:
            db.commit()
            print(f"\n✅ Fixed {total_fixed} records in database")
        else:
            print(f"\n📝 Would fix {total_fixed} records (run with --apply to save changes)")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
