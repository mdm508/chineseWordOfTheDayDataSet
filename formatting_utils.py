import re
import unittest
from typing import Dict, List, Set, Any

def capture_raw_context(row: Dict[str, Any]) -> str:
    """
    Ensures the 'context' field is preserved exactly as it appears in the 
    source data without any modifications or splitting.
    """
    return row.get('context', "")

def clean_meaning_list(row: Dict[str, Any], pattern: str) -> None:
    """
    Removes 'see also' style definitions and sorts the remaining meanings 
    by character length.
    """
    meanings = row.get('meanings', [])
    filtered = [m for m in meanings if not re.search(pattern, m)]
    row['meanings'] = sorted(filtered, key=lambda m: (len(m), m))

class TestFormattingUtils(unittest.TestCase):
    """Test suite for string preservation and meaning filtering."""
    def test_capture_raw_context(self):
        row = {'context': '1.科技、2.日常起居'}
        ctx = capture_raw_context(row)
        self.assertEqual(ctx, '1.科技、2.日常起居')

    def test_clean_meaning_list(self):
        row = {'meanings': ['long definition', 'short', 'see word[abc]']}
        clean_meaning_list(row, r'see.*\[.*\]')
        self.assertEqual(row['meanings'], ['short', 'long definition'])

if __name__ == "__main__":
    unittest.main()