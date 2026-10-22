<div align="center">

# 🔐 Password Strength Meter CLI

**A modern, robust terminal tool to rate password security from 0% to 100% with entropy analysis, pattern detection, and crack time estimation.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)]()

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [How Scoring Works](#-how-scoring-works) • [Push to GitHub](#-how-to-push-to-github)

</div>

---

## 📺 Preview

```text
╭──────────────── Password Security Rating: 100% - Very Strong ────────────────╮
│                                                                              │
│  Strength Meter:                 ████████████████████████████████ 100%       │
│  Password:                       K9#xP!2026@Secure                           │
│  Length:                         17 characters                               │
│  Entropy:                        111.69 bits                                 │
│  Composition:                    ✓ a-z  ✓ A-Z  ✓ 0-9  ✓ Special              │
│  Crack Time (GPU 100B/s):        6.6e+05 billion years                       │
│  Crack Time (Online Throttled):  6.6e+14 billion years                       │
│  Feedback / Tips:                  ✓ Excellent password! Meets high          │
│                                  security standards.                         │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## ✨ Features

- 📊 **Normalized 0% – 100% Strength Score**: Combines length, character diversity, and Shannon entropy.
- 🛡️ **Vulnerability & Pattern Detection**:
  - Catches top common breached passwords (e.g., `password`, `123456`, `admin123`).
  - Flags sequential keys & keyboard walks (`qwerty`, `12345`, `abcdef`).
  - Detects repeated consecutive characters (`aaaa`, `1111`).
  - Penalizes predictable patterns (e.g., capitalized word + digits + exclamation mark).
- ⏱️ **Brute-Force Crack Time Estimates**:
  - **High-speed GPU Rig**: Benchmarked at 100 billion ($10^{11}$) guesses/sec (e.g., Hashcat / offline attack).
  - **Online Attack**: Rate-limited server benchmarked at 100 attempts/sec.
- 💡 **Actionable Recommendations**: Instant tips to level up weak passwords to 90%+.
- 🔑 **Cryptographic Password Generator**: Built-in generator creating secure passwords with score $\ge 90\%$.
- 🎨 **Rich Visual Terminal UI**: Colored progress meters and status boxes with automatic fallback to standard ANSI.
- ⚙️ **Flexible CLI Modes**:
  - **Interactive Mode**: Hidden password input (`getpass`) to protect against shoulder-surfing.
  - **Command-Line Argument**: Quickly test passwords via flags.
  - **Piping / Stdin**: Seamless integration with Unix pipelines (`echo "pw" | ./password_checker.py`).
  - **Batch File Mode**: Test password lists from text files.
  - **Machine-readable JSON**: Integration with CI/CD and security automation.

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/password-strength-cli.git
cd password-strength-cli
```

### 2. Set up a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
*(Note: The CLI also runs zero-dependency with standard Python 3 and ANSI styling if `rich` is omitted!)*

### 4. Make executable (macOS / Linux)
```bash
chmod +x password_checker.py
```

---

## 💻 Quick Start & Usage

### 1. Interactive Mode
Run without arguments for interactive hidden input:
```bash
./password_checker.py
```
> - Type `gen` to quickly generate a secure password.
> - Type `q` to exit.
> - Run with `-s` (`./password_checker.py -s`) to show input visibly.

### 2. Direct Password Check
```bash
./password_checker.py "MySuperSecret#2026!"
```
To show the password in the terminal report:
```bash
./password_checker.py -s "MySuperSecret#2026!"
```

### 3. Generate a Strong Password ($\ge 90\%$)
```bash
# Default length: 16 characters
./password_checker.py --generate

# Custom length: 24 characters
./password_checker.py --generate --length 24
```

### 4. Pipe via Stdin
```bash
echo "P@ssw0rd2026" | ./password_checker.py
```

### 5. Batch File Evaluation
Evaluate a file containing multiple passwords (one per line):
```bash
./password_checker.py --file sample_passwords.txt
```

### 6. JSON Output (for CI/CD or APIs)
```bash
./password_checker.py --json "K9#xP!2026@Secure"
```
Output:
```json
{
  "score": 100,
  "rating": "Very Strong",
  "entropy": 111.69,
  "length": 17,
  "has_lower": true,
  "has_upper": true,
  "has_digit": true,
  "has_symbol": true,
  "char_types_count": 4,
  "feedback": [
    "Excellent password! Meets high security standards."
  ],
  "crack_times": {
    "offline_gpu": "6.6e+05 billion years",
    "online_throttled": "6.6e+14 billion years"
  }
}
```

---

## 📐 How Scoring Works

The score is calculated on a calibrated scale from **0% to 100%**:

$$\text{Final Score} = \max(0, \min(100, \text{Length} + \text{Diversity} + \text{Entropy} - \text{Penalties}))$$

### 1. Base Score Components (up to 100 pts)
| Component | Criteria | Max Points |
|---|---|:---:|
| **Length** | $\ge 16$ chars (45 pts), 12–15 (35 pts), 8–11 (25 pts), 6–7 (15 pts), $<6$ (5 pts) | 45 |
| **Character Diversity** | 4 types (30 pts), 3 types (22 pts), 2 types (12 pts), 1 type (5 pts) | 30 |
| **Shannon Entropy** | $\ge 60$ bits (25 pts), 40–59 bits (17 pts), 28–39 bits (10 pts), $<28$ bits (3 pts) | 25 |

Shannon Entropy Formula:
$$E = L \times \log_2(R)$$
*Where $L$ is password length and $R$ is character pool size ($26 + 26 + 10 + 33 = 95$).*

### 2. Penalty Deductions
- **Common Password Match**: -60 points
- **Only Numbers**: -20 points
- **Only Letters**: -10 points
- **Sequential Patterns (e.g. `123`, `abc`, `qwerty`)**: -15 points
- **Repeated Characters (e.g. `aaa`)**: -15 points
- **Predictable Prefix/Suffix Pattern**: -10 points

### 3. Strength Ratings
| Score Range | Rating Level | Assessment |
|---|---|---|
| **0% – 24%** | 🔴 Very Weak | Cracked instantly; trivial to guess. |
| **25% – 49%** | 🟡 Weak | Vulnerable to fast brute-force or dictionary lookup. |
| **50% – 74%** | 🔵 Moderate | Acceptable for low-risk accounts; needs length or special chars. |
| **75% – 89%** | 🔷 Strong | High resistance to brute force; good entropy. |
| **90% – 100%** | 🟢 Very Strong | Excellent entropy ($\ge 80$ bits); immune to offline GPU clusters. |

---

## 🧪 Testing

Run the included unit test suite:
```bash
python3 -m unittest test_evaluator.py
```

---

## 📁 Project Structure

```text
password_sec/
├── .gitignore              # Ignored files (venv, caches, macOS files)
├── LICENSE                 # MIT License
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies (rich)
├── evaluator.py            # Core entropy & scoring logic
├── password_checker.py     # CLI interface & terminal UI
├── sample_passwords.txt    # Sample passwords for testing
└── test_evaluator.py       # Unit test suite
```

---

## 📤 How to Push to GitHub

To publish this project to your GitHub account:

```bash
# 1. Initialize git
git init

# 2. Add files and make initial commit
git add .
git commit -m "Initial commit: Password Strength Meter CLI (0-100%)"

# 3. Create a new repository on GitHub (e.g. named 'password-strength-cli')
# 4. Link your remote repository and push (replace with your repo URL):
git branch -M main
git remote add origin https://github.com/<your-username>/password-strength-cli.git
git push -u origin main
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
