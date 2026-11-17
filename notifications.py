"""Notifications, mocked: no real email is ever sent.

MockNotifier is a mock object (https://en.wikipedia.org/wiki/Mock_object). It has
the same send_email method a real email client would have, but it only records each
message in memory (`sent`) and in outbox.txt, which stands in for a mail server.

Services call notifications.send_email(...). To use a real email service later,
write a class with the same send_email method and pass it to use_notifier(); no
service has to change.
"""
OUTBOX_PATH = "outbox.txt"


class MockNotifier:
    def __init__(self, outbox_path=OUTBOX_PATH):
        self.outbox_path = outbox_path
        self.sent = []

    def send_email(self, email, subject, body):
        self.sent.append({"to": email, "subject": subject, "body": body})
        with open(self.outbox_path, "a") as f:
            f.write("TO: " + email + " | SUBJECT: " + subject + " | BODY: " + body + "\n")


notifier = MockNotifier()


def use_notifier(new_notifier):
    """Swap the notifier, for example for a real email client or a test double."""
    global notifier
    notifier = new_notifier


def send_email(email, subject, body):
    notifier.send_email(email, subject, body)
