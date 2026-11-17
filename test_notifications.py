"""Tests for the mocked notifications: no HTTP, no database, no real email."""
import os
import tempfile
import unittest
from unittest import mock

import fine_service
import notifications


class MockNotifierTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.outbox = os.path.join(self.temp_dir.name, "outbox.txt")
        self.notifier = notifications.MockNotifier(self.outbox)
        self.original = notifications.notifier
        notifications.use_notifier(self.notifier)

    def tearDown(self):
        notifications.use_notifier(self.original)
        self.temp_dir.cleanup()

    def test_records_sent_email(self):
        notifications.send_email("sam@campus.edu", "Hello", "Test body")
        self.assertEqual(self.notifier.sent, [{"to": "sam@campus.edu", "subject": "Hello", "body": "Test body"}])
        with open(self.outbox) as f:
            self.assertEqual(f.read(), "TO: sam@campus.edu | SUBJECT: Hello | BODY: Test body\n")

    def test_pay_fine_notifies_member(self):
        # Mock the repositories too, so the service runs without a database.
        loan = {"id": 7, "member_id": 3, "returned": 1, "fine": 2.5, "fine_paid": 0}
        with mock.patch("loan_repository.get_loan", return_value=loan), \
             mock.patch("loan_repository.mark_fine_paid", return_value={**loan, "fine_paid": 1}), \
             mock.patch("member_repository.get_member", return_value={"email": "alex@campus.edu"}):
            fine_service.pay_fine(7)
        self.assertEqual(
            self.notifier.sent, [{"to": "alex@campus.edu", "subject": "Fine paid", "body": "We received $2.5"}]
        )


if __name__ == "__main__":
    unittest.main()
