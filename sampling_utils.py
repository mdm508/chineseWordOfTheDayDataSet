import random
import unittest
from typing import List, Dict, Any

def generate_meanings_sample(data: List[Dict[str, Any]], sample_size: int = 100, filename: str = "meaningssample.txt") -> int:
    """
    Collects all meanings from the dataset, shuffles them, and writes a 
    sample to a text file, one per line.
    """
    if not data:
        return 0
    
    # Flatten the list of lists (each row has a list of meanings)
    all_meanings = []
    for row in data:
        all_meanings.extend(row.get("meanings", []))
    
    # Remove duplicates to get unique meanings for analysis
    unique_meanings = list(set(all_meanings))
    
    # Adjust sample size if data is smaller than requested
    actual_sample_size = min(len(unique_meanings), sample_size)
    
    # Randomly sample
    sample = random.sample(unique_meanings, actual_sample_size)
    
    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        for meaning in sample:
            f.write(f"{meaning}\n")
            
    return actual_sample_size

class TestSampling(unittest.TestCase):
    def test_sample_generation(self):
        data = [{"meanings": ["apple", "fruit"]}, {"meanings": ["banana"]}]
        count = generate_meanings_sample(data, sample_size=2, filename="test_sample.txt")
        self.assertEqual(count, 2)
        import os
        if os.path.exists("test_sample.txt"):
            os.remove("test_sample.txt")

if __name__ == "__main__":
    unittest.main()