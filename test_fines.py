"""Tests for the fine rules alone: no HTTP, no database."""
import unittest
from datetime import date

import fines

TODAY = date(2026, 11, 17)


class FineRulesTest(unittest.TestCase):
    def test_days_late(self):
        self.assertEqual(fines.days_late("2026-11-12", TODAY), 5)
        self.assertEqual(fines.days_late("2026-11-20", TODAY), -3)

    def test_is_overdue(self):
        self.assertTrue(fines.is_overdue("2026-11-16", TODAY))
        self.assertFalse(fines.is_overdue("2026-11-17", TODAY))
        self.assertFalse(fines.is_overdue("2026-11-30", TODAY))

    def test_late_fine_is_half_a_dollar_per_day(self):
        self.assertEqual(fines.late_fine("2026-11-12", TODAY), 2.5)
        self.assertEqual(fines.late_fine("2026-11-17", TODAY), 0)
        self.assertEqual(fines.late_fine("2026-11-30", TODAY), 0)

    def test_current_fine_builds_up_while_open(self):
        self.assertEqual(fines.current_fine("2026-11-12", False, 0.0, TODAY), 2.5)

    def test_current_fine_is_fixed_once_returned(self):
        self.assertEqual(fines.current_fine("2026-11-12", True, 1.0, TODAY), 1.0)

    def test_balance_owed(self):
        self.assertEqual(fines.balance_owed("2026-11-12", False, 0.0, False, TODAY), 2.5)
        self.assertEqual(fines.balance_owed("2026-11-12", True, 2.5, False, TODAY), 2.5)
        self.assertEqual(fines.balance_owed("2026-11-12", True, 2.5, True, TODAY), 0.0)

    def test_has_fine_to_pay(self):
        self.assertTrue(fines.has_fine_to_pay(2.5, False))
        self.assertFalse(fines.has_fine_to_pay(2.5, True))
        self.assertFalse(fines.has_fine_to_pay(0.0, False))

    def test_money_rounds_to_cents(self):
        self.assertEqual(fines.money(2.5), 2.5)
        self.assertEqual(fines.money("3.456"), 3.46)


if __name__ == "__main__":
    unittest.main()
