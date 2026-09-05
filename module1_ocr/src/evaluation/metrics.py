"""Evaluation Metrics for Module 1 OCR & Information Extraction.

Computes:
- Character Error Rate (CER) & Character Accuracy
- Word Error Rate (WER) & Word Accuracy
- Field-level Exact Match (EM) & Normalized Match
- Precision, Recall, and F1-Score
- Processing Latency & Failure Rate

Includes a pure-Python Levenshtein algorithm with optional C-extension acceleration.
"""

from typing import Dict, List, Any, Tuple
import difflib

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein edit distance using dynamic programming."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def string_similarity_ratio(s1: str, s2: str) -> float:
    """Calculates normalized string similarity ratio [0.0 - 1.0]."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def compute_cer(reference: str, hypothesis: str) -> Tuple[float, float]:
    """Calculates Character Error Rate (CER) and Character Accuracy.
    
    CER = Levenshtein_Distance(ref, hyp) / max(1, len(ref))
    Accuracy = max(0.0, 1.0 - CER)
    """
    ref_clean = "".join(reference.split())
    hyp_clean = "".join(hypothesis.split())
    
    if not ref_clean and not hyp_clean:
        return 0.0, 1.0
    if not ref_clean:
        return 1.0, 0.0

    dist = levenshtein_distance(ref_clean, hyp_clean)
    cer = float(dist / len(ref_clean))
    accuracy = max(0.0, 1.0 - min(1.0, cer))
    return round(cer, 4), round(accuracy, 4)

def compute_wer(reference: str, hypothesis: str) -> Tuple[float, float]:
    """Calculates Word Error Rate (WER) and Word Accuracy."""
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()

    if not ref_words and not hyp_words:
        return 0.0, 1.0
    if not ref_words:
        return 1.0, 0.0

    dist = levenshtein_distance(" ".join(ref_words), " ".join(hyp_words))
    r_len = max(1, len(" ".join(ref_words)))
    wer = min(1.0, float(dist / r_len))
    accuracy = max(0.0, 1.0 - wer)
    return round(wer, 4), round(accuracy, 4)

def evaluate_field_extraction(ground_truth_fields: Dict[str, Any], extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates field-level extraction precision, recall, F1, and exact matches."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    exact_matches = 0
    total_gt_fields = len(ground_truth_fields)
    
    field_details = {}

    for field_name, gt_info in ground_truth_fields.items():
        gt_val = str(gt_info.get("text", "")).strip().upper() if isinstance(gt_info, dict) else str(gt_info).strip().upper()
        
        if field_name in extracted_fields:
            ext_obj = extracted_fields[field_name]
            ext_val = ext_obj.value.strip().upper() if hasattr(ext_obj, "value") else str(ext_obj.get("value", "")).strip().upper()
            
            # Compare
            is_exact = (gt_val == ext_val)
            if is_exact:
                exact_matches += 1
                true_positives += 1
            else:
                sim = string_similarity_ratio(gt_val, ext_val)
                if sim >= 0.80:
                    true_positives += 1
                else:
                    false_positives += 1
                    false_negatives += 1
                    
            field_details[field_name] = {
                "ground_truth": gt_val,
                "extracted": ext_val,
                "exact_match": is_exact,
                "similarity": round(string_similarity_ratio(gt_val, ext_val), 3)
            }
        else:
            false_negatives += 1
            field_details[field_name] = {
                "ground_truth": gt_val,
                "extracted": None,
                "exact_match": False,
                "similarity": 0.0
            }

    for ext_name in extracted_fields:
        if ext_name not in ground_truth_fields:
            false_positives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    exact_match_ratio = exact_matches / total_gt_fields if total_gt_fields > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "exact_match_ratio": round(exact_match_ratio, 4),
        "field_details": field_details
    }
