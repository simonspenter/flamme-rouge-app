# logic/ids.py
import random
import string

def generate_short_race_id(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

def generate_unique_race_id(cursor, length=6):
    from .ids import generate_short_race_id  # safe self-import pattern if needed
    while True:
        race_id = generate_short_race_id(length)
        cursor.execute("SELECT 1 FROM races WHERE id = ?", (race_id,))
        if not cursor.fetchone():
            return race_id
