"""
Grading logic for the CodeReview environment.
Computes reward based on precision/recall of identified issues.
"""
from typing import List, Dict, Tuple


def normalize(text: str) -> str:
    """Normalize text for fuzzy matching."""
    return text.lower().strip()


def issue_matches(submitted: Dict[str, str], ground_truth: Dict[str, str]) -> bool:
    """
    Check if a submitted issue matches a ground truth issue.
    Uses fuzzy matching on category and description keywords.
    """
    # Category must match
    if normalize(submitted.get("category", "")) != normalize(ground_truth.get("category", "")):
        return False
    
    # Check if key words from ground truth appear in submitted description
    gt_desc = normalize(ground_truth.get("description", ""))
    sub_desc = normalize(submitted.get("description", ""))
    
    # Extract key terms from ground truth
    key_terms = []
    gt_words = gt_desc.split()
    # Use significant words (length > 3) as matching terms
    for word in gt_words:
        cleaned = word.strip(".,;:'\"()[]{}!?")
        if len(cleaned) > 3:
            key_terms.append(cleaned)
    
    if not key_terms:
        return len(sub_desc) > 0  # If no key terms, any description counts
    
    # At least 30% of key terms should appear in submission
    matches = sum(1 for term in key_terms if term in sub_desc)
    return matches / len(key_terms) >= 0.3


def grade_review(
    submitted_issues: List[Dict[str, str]],
    ground_truth_issues: List[Dict[str, str]],
    difficulty: str
) -> Tuple[float, str, int, int]:
    """
    Grade a code review submission.
    
    Returns: (reward, feedback_message, true_positives, false_positives)
    
    Reward formula:
      reward = (precision_weight * precision + recall_weight * recall) * difficulty_multiplier
    """
    if not ground_truth_issues:
        # No issues to find — reward 1.0 if agent also found nothing
        if not submitted_issues:
            return 1.0, "Correct! No issues in this code.", 0, 0
        else:
            return 0.5, "Code was clean but you reported issues.", 0, len(submitted_issues)
    
    # Match submitted issues to ground truth
    gt_matched = [False] * len(ground_truth_issues)
    true_positives = 0
    false_positives = 0
    
    for sub_issue in submitted_issues:
        matched = False
        for i, gt_issue in enumerate(ground_truth_issues):
            if not gt_matched[i] and issue_matches(sub_issue, gt_issue):
                gt_matched[i] = True
                true_positives += 1
                matched = True
                break
        if not matched:
            false_positives += 1
    
    # Calculate precision and recall
    total_submitted = len(submitted_issues)
    total_ground_truth = len(ground_truth_issues)
    
    precision = true_positives / total_submitted if total_submitted > 0 else 0.0
    recall = true_positives / total_ground_truth if total_ground_truth > 0 else 0.0
    
    # Difficulty-based weights
    weights = {
        "easy":   {"precision": 0.3, "recall": 0.7},
        "medium": {"precision": 0.4, "recall": 0.6},
        "hard":   {"precision": 0.5, "recall": 0.5},
    }
    w = weights.get(difficulty, weights["medium"])
    
    reward = w["precision"] * precision + w["recall"] * recall
    reward = round(min(max(reward, 0.0), 1.0), 4)  # Clamp to [0, 1]
    
    # Build feedback
    feedback_parts = [
        f"Found {true_positives}/{total_ground_truth} issues correctly.",
        f"False positives: {false_positives}.",
        f"Precision: {precision:.2f}, Recall: {recall:.2f}.",
        f"Reward: {reward:.4f}"
    ]
    
    # Add specific feedback on missed issues
    missed = [gt for i, gt in enumerate(ground_truth_issues) if not gt_matched[i]]
    if missed:
        feedback_parts.append(f"Missed issues: {len(missed)}")
    
    return reward, " ".join(feedback_parts), true_positives, false_positives
