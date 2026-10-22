import unittest
from evaluator import evaluate_password, calculate_entropy, estimate_crack_time

class TestPasswordEvaluator(unittest.TestCase):
    def test_empty_password(self):
        res = evaluate_password("")
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["rating"], "Very Weak")

    def test_common_passwords(self):
        for common in ["password", "123456", "qwerty", "admin123"]:
            res = evaluate_password(common)
            self.assertLessEqual(res["score"], 25)
            self.assertIn(res["rating"], ["Very Weak", "Weak"])

    def test_short_simple_passwords(self):
        res = evaluate_password("abc")
        self.assertLessEqual(res["score"], 25)
        self.assertEqual(res["rating"], "Very Weak")

    def test_moderate_password(self):
        res = evaluate_password("BlueSky88")
        self.assertTrue(25 <= res["score"] <= 75)

    def test_strong_password(self):
        res = evaluate_password("T7#mK9!pL2@wQz4v")
        self.assertGreaterEqual(res["score"], 90)
        self.assertEqual(res["rating"], "Very Strong")

    def test_entropy_increases_with_diversity_and_length(self):
        e1 = calculate_entropy("aaaaaaaa")
        e2 = calculate_entropy("aA1!aA1!")
        self.assertGreater(e2, e1)

    def test_crack_time_structure(self):
        times = estimate_crack_time(80.0)
        self.assertIn("offline_gpu", times)
        self.assertIn("online_throttled", times)

if __name__ == "__main__":
    unittest.main()
