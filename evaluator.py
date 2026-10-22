"""
Password Strength Evaluator Module
Calculates password entropy, detects weaknesses/patterns, and produces a 0-100% score.
"""

import math
import re
from typing import Dict, List, Tuple, Any

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "123456789", "12345", "1234", "111111", "000000",
    "qwerty", "abc123", "password1", "admin", "welcome", "login", "secret", "iloveyou",
    "monkey", "dragon", "football", "baseball", "letmein", "master", "sunshine", "princess",
    "trustno1", "passw0rd", "p@ssword", "p@ssw0rd", "qwerty123", "admin123", "root",
    "changeme", "pass1234", "testing", "default", "hello", "starwars", "superman"
}

KEYBOARD_SEQUENCES = [
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "1234567890", "0987654321",
    "abcdefghijklmnopqrstuvwxyz"
]


def calculate_entropy(password: str) -> float:
    """Calculate theoretical Shannon / pool-based entropy in bits."""
    if not password:
        return 0.0

    pool_size = 0
    if re.search(r'[a-z]', password):
        pool_size += 26
    if re.search(r'[A-Z]', password):
        pool_size += 26
    if re.search(r'[0-9]', password):
        pool_size += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        pool_size += 33  # Standard printable symbols

    if pool_size == 0:
        return 0.0

    return len(password) * math.log2(pool_size)


def check_sequential_or_keyboard(password: str) -> Tuple[bool, List[str]]:
    """Check for obvious consecutive or keyboard sequences."""
    pw_lower = password.lower()
    matches = []
    
    for seq in KEYBOARD_SEQUENCES:
        for i in range(len(seq) - 2):
            sub = seq[i:i+3]
            if sub in pw_lower:
                matches.append(sub)
                
    return (len(matches) > 0, matches)


def estimate_crack_time(entropy_bits: float) -> Dict[str, str]:
    """
    Estimate time to crack based on offline GPU hash attack rate:
    Assuming 100 billion (10^11) guesses per second (standard high-end modern GPU rig).
    """
    total_combinations = 2 ** entropy_bits
    speed_per_sec = 100_000_000_000  # 100 billion guesses/sec
    seconds = (total_combinations / 2) / speed_per_sec  # average crack at 50% search space

    def format_time(sec: float) -> str:
        if sec < 1e-4:
            return "Instant (< 1 ms)"
        elif sec < 1:
            return f"{sec*1000:.1f} milliseconds"
        elif sec < 60:
            return f"{sec:.1f} seconds"
        elif sec < 3600:
            return f"{sec/60:.1f} minutes"
        elif sec < 86400:
            return f"{sec/3600:.1f} hours"
        elif sec < 31536000:
            return f"{sec/86400:.1f} days"
        elif sec < 31536000 * 1000:
            return f"{sec/31536000:.1f} years"
        elif sec < 31536000 * 1_000_000:
            return f"{sec/(31536000*1000):.1f} thousand years"
        elif sec < 31536000 * 1_000_000_000:
            return f"{sec/(31536000*1_000_000):.1f} million years"
        else:
            return f"{sec/(31536000*1_000_000_000):.1e} billion years"

    # Online rate: 100 guesses / sec (rate limited)
    online_sec = (total_combinations / 2) / 100

    return {
        "offline_gpu": format_time(seconds),
        "online_throttled": format_time(online_sec)
    }


def evaluate_password(password: str) -> Dict[str, Any]:
    """
    Evaluates password strength and returns a detailed report
    including score (0-100%), level, entropy, feedback, and tips.
    """
    if not password:
        return {
            "score": 0,
            "rating": "Very Weak",
            "entropy": 0.0,
            "length": 0,
            "has_lower": False,
            "has_upper": False,
            "has_digit": False,
            "has_symbol": False,
            "feedback": ["Password cannot be empty."],
            "crack_times": estimate_crack_time(0.0)
        }

    length = len(password)
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_symbol = bool(re.search(r'[^a-zA-Z0-9]', password))
    char_types_count = sum([has_lower, has_upper, has_digit, has_symbol])

    entropy = calculate_entropy(password)
    feedback: List[str] = []
    penalties = 0

    # 1. Base Score calculation (max 100 points)
    # Length component (up to 45 pts)
    # Length < 6: 5 pts
    # 6-7: 15 pts
    # 8-11: 25 pts
    # 12-15: 35 pts
    # 16+: 45 pts
    if length < 6:
        length_score = 5
        feedback.append("Critically short length (less than 6 characters).")
    elif length < 8:
        length_score = 15
        feedback.append("Short length (minimum 8 recommended, 12+ preferred).")
    elif length < 12:
        length_score = 25
        if length < 10:
            feedback.append("Decent length, but 12+ characters is much safer.")
    elif length < 16:
        length_score = 35
    else:
        length_score = 45

    # Character Diversity component (up to 30 pts)
    # 1 type: 5 pts
    # 2 types: 12 pts
    # 3 types: 22 pts
    # 4 types: 30 pts
    diversity_map = {1: 5, 2: 12, 3: 22, 4: 30}
    diversity_score = diversity_map.get(char_types_count, 5)

    if not has_lower:
        feedback.append("Add lowercase letters (a-z).")
    if not has_upper:
        feedback.append("Add uppercase letters (A-Z).")
    if not has_digit:
        feedback.append("Add numeric digits (0-9).")
    if not has_symbol:
        feedback.append("Add special symbols (!@#$%^&*...).")

    # Entropy component (up to 25 pts)
    # Entropy: < 28 bits: 3 pts, 28-39: 10 pts, 40-59: 17 pts, 60+: 25 pts
    if entropy < 28:
        entropy_score = 3
    elif entropy < 40:
        entropy_score = 10
    elif entropy < 60:
        entropy_score = 17
    else:
        entropy_score = 25

    base_score = length_score + diversity_score + entropy_score

    # 2. Penalties & Weak Pattern Detection
    # Common password check
    clean_lower = password.strip().lower()
    if clean_lower in COMMON_PASSWORDS:
        penalties += 60
        feedback.append("Warning: This is an extremely common, easily crackable password!")

    # Repeated characters (e.g. 'aaaa', '1111')
    if re.search(r'(.)\1{2,}', password):
        penalties += 15
        feedback.append("Avoid sequences of 3+ identical consecutive characters.")

    # Keyboard / sequential patterns
    has_seq, seq_matches = check_sequential_or_keyboard(password)
    if has_seq:
        penalties += 15
        feedback.append(f"Contains sequential patterns: {', '.join(seq_matches[:3])}.")

    # Only digits or only letters
    if password.isdigit():
        penalties += 20
        feedback.append("Password consists solely of numbers.")
    elif password.isalpha():
        penalties += 10
        feedback.append("Password consists solely of letters.")

    # Simple suffix/prefix pattern (e.g. Word1, Word123!)
    if re.match(r'^[A-Z][a-z]+[0-9]{1,3}[!@#$?]?$', password):
        penalties += 10
        feedback.append("Predictable pattern: Capitalized word followed by simple numbers/symbol.")

    # Calculate final score (clamped between 0 and 100)
    raw_score = base_score - penalties
    score = max(0, min(100, raw_score))

    # Rating categorization
    if score < 25:
        rating = "Very Weak"
    elif score < 50:
        rating = "Weak"
    elif score < 75:
        rating = "Moderate"
    elif score < 90:
        rating = "Strong"
    else:
        rating = "Very Strong"

    if not feedback:
        feedback.append("Excellent password! Meets high security standards.")

    return {
        "score": score,
        "rating": rating,
        "entropy": round(entropy, 2),
        "length": length,
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "char_types_count": char_types_count,
        "feedback": feedback,
        "crack_times": estimate_crack_time(entropy)
    }
