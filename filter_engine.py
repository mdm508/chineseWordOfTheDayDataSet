import re
from typing import List, Dict, Any, Tuple, Set

def clean_to_traditional(text: str) -> str:
    """Extracts only the Traditional part of a TRAD|SIMP string."""
    if '|' in text:
        return text.split('|')[0].strip()
    return text.strip()

def normalize_context(ctx: str) -> str:
    """Removes leading numbers/dots and defaults to '雜項'."""
    if not ctx or ctx.strip().lower() in ["no context", ""]:
        return "雜項"
    # Regex to remove "1. ", "10. ", etc.
    clean_ctx = re.sub(r'^\d+\.\s*', '', ctx.strip())
    return clean_ctx if clean_ctx else "雜項"

def parse_meanings(raw_definition: str) -> List[Dict[str, str]]:
    """
    Splits by Senses (/) and Glosses (;). 
    Extracts usage notes from () and applies them to all glosses in that sense.
    """
    # CEDICT definitions are wrapped in / /
    senses = [s.strip() for s in raw_definition.split('/') if s.strip()]
    processed_meanings = []
    seen_defs = set()

    for sense in senses:
        # 1. Extract all notes inside parentheses anywhere in the sense
        notes = re.findall(r'\((.*?)\)', sense)
        usage_note = "; ".join(notes) if notes else None
        
        # 2. Clean the sense by removing the parentheses and their content
        clean_sense = re.sub(r'\(.*?\)', '', sense).strip()
        
        # 3. Split the remaining sense into individual glosses
        glosses = [g.strip() for g in clean_sense.split(';') if g.strip()]
        
        for gloss in glosses:
            if gloss.lower() not in seen_defs:
                processed_meanings.append({
                    "definition": gloss,
                    "usage_note": usage_note
                })
                seen_defs.add(gloss.lower())
                
    return processed_meanings

def extract_metadata(meanings_list: List[Dict[str, str]]) -> Tuple[List[str], List[str], List[Dict[str, str]]]:
    """
    Identifies Classifiers and Synonyms within meanings.
    Removes them from the meaning list and moves them to their own fields.
    """
    classifiers = []
    synonyms = []
    final_meanings = []
    
    # Common markers for synonyms in CEDICT
    syn_markers = ["variant of ", "also written ", "also pr. "]

    for item in meanings_list:
        defn = item["definition"]
        
        # Handle Classifiers (CL:...)
        if defn.startswith("CL:"):
            # Format: CL:個|个[ge4],座[zuo4]
            raw_cl_list = defn.replace("CL:", "").split(',')
            for cl in raw_cl_list:
                # Remove pinyin [xxx]
                cl_chars = re.sub(r'\[.*?\]', '', cl).strip()
                classifiers.append(clean_to_traditional(cl_chars))
            continue # Don't add to meanings

        # Handle Synonyms/Variants
        is_synonym = False
        for marker in syn_markers:
            if marker in defn.lower():
                # Extract the characters (usually right after the marker before any [ or /)
                # This is a simplified extraction; CEDICT often puts characters right after
                parts = defn.split(marker)
                if len(parts) > 1:
                    raw_syn = parts[1].split('[')[0].strip()
                    synonyms.append(clean_to_traditional(raw_syn))
                    is_synonym = True
        
        if not is_synonym:
            final_meanings.append(item)

    return classifiers, synonyms, final_meanings

def process_csv_rows(rows: List[Dict[str, Any]], cedict_db: Dict[str, Any], redirect_pattern: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Master processing loop for all CSV rows."""
    processed_data = []
    discarded = []

    for row in rows:
        word = row.get('word', '').strip()
        if not word:
            continue
            
        # Get entry from CEDICT
        entry = cedict_db.get(word)
        if not entry:
            discarded.append(word)
            continue

        # 1. Parse Meanings and extract notes
        raw_meanings = parse_meanings(entry['raw_definitions'])
        
        # 2. Extract Classifiers and Synonyms from the parsed list
        cls, syns, clean_meanings = extract_metadata(raw_meanings)

        # 3. Construct Final Object
        processed_row = {
            "traditional": word, # Already stripped to traditional in main usually
            "pinyin": entry['pinyin'],
            "context": normalize_context(row.get('context', '')),
            "classifiers": list(set(cls)),
            "synonyms": list(set(syns)),
            "meanings": clean_meanings,
            # Keep frequency/level for sorting in main.py
            "spokenFrequencyPerMillion": row.get('spokenFrequencyPerMillion', 0),
            "levelNumber": row.get('levelNumber', 0)
        }
        
        processed_data.append(processed_row)

    return processed_data, discarded