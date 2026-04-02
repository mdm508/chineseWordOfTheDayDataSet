import unittest
from typing import List, Dict, Any, Optional
from collections import Counter

# Added "No Context" to the mapping
TRANSLATIONS = {
    "核心詞": "Core Words",
    "No Context Provided": "Miscellaneous / Unlabeled",
    "1.個人資料": "Personal Information",
    "2.日常起居": "Daily Life",
    "3.職業": "Occupations",
    "4.休閒、娛樂": "Leisure and Entertainment",
    "5.交通、旅遊": "Transportation and Travel",
    "6.社交、人際": "Socializing",
    "7.身體、醫療": "Body and Medical",
    "8.教育、學習": "Education and Learning",
    "9.購物、商店": "Shopping",
    "10.餐飲、烹飪": "Dining and Cooking",
    "11.公共服務": "Public Services",
    "12.安全": "Safety",
    "13.自然環境": "Natural Environment",
    "14.社會": "Society",
    "15.文化": "Culture",
    "16.情緒、態度": "Emotions and Attitudes",
    "17.科技": "Science and Technology"
}

def get_visual_width(text: str) -> int:
    return sum(2 if ord(char) > 127 else 1 for char in text)

def pad_to_width(text: str, total_width: int) -> str:
    return text + (" " * (total_width - get_visual_width(text)))

def count_context_frequencies(data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Tallies frequencies. If 'context' is empty, it groups them 
    under 'No Context Provided'.
    """
    counts = Counter()
    for row in data:
        raw_ctx = row.get('context', "")
        # Use a consistent label for empty or whitespace-only strings
        ctx = raw_ctx.strip() if raw_ctx and raw_ctx.strip() else "No Context Provided"
        counts[ctx] += 1
    return dict(counts)

def print_context_report(counts: Dict[str, int], output_file: Optional[str] = None) -> None:
    if not counts:
        print("\nNo data to report.")
        return

    # Sorts
    alphabetical_contexts = sorted(counts.keys())
    sorted_by_count = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    total_words = sum(counts.values())
    unique_contexts = len(counts)
    
    lines = []

    # SECTION 1: Alphabetical with Translation
    lines.append("="*80)
    lines.append(f"{'SECTION 1: ALL CONTEXTS (ALPHABETICAL)':^80}")
    lines.append("="*80)
    for ctx in alphabetical_contexts:
        eng = TRANSLATIONS.get(ctx, "Unknown Category")
        lines.append(f"{pad_to_width(ctx, 40)} | {eng}")
    lines.append("")

    # SECTION 2: Frequency Table
    lines.append("="*80)
    lines.append(f"{'SECTION 2: CONTEXT FREQUENCY TABLE':^80}")
    lines.append("="*80)
    
    col1_w, col2_w = 5, 55
    header = f"{'ID':<5} | {pad_to_width('Context Name', col2_w)} | {'Count'}"
    lines.append(header)
    lines.append("-" * 80)
    
    for idx, (name, count) in enumerate(sorted_by_count, start=1):
        row_str = f"{idx:<5} | {pad_to_width(name, col2_w)} | {count:<10}"
        lines.append(row_str)

    # SECTION 3: Summary Statistics
    lines.append("")
    lines.append("="*80)
    lines.append(f"{'SECTION 3: SUMMARY STATISTICS':^80}")
    lines.append("="*80)
    lines.append(f"Total Entries in JSON:      {total_words}")
    lines.append(f"Total Unique Categories:    {unique_contexts}")
    lines.append(f"Average Words/Category:     {total_words/unique_contexts:.2f}")
    
    # Calculate what % is uncategorized
    uncat_count = counts.get("No Context Provided", 0)
    lines.append(f"Unlabeled Data Ratio:       {(uncat_count/total_words)*100:.2f}%")
    lines.append("="*80 + "\n")

    report_content = "\n".join(lines)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report exported to: {output_file}")
    else:
        print(report_content)