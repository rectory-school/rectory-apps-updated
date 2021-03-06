"""Command to create a sample email"""

import email.utils
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from stored_mail import models


class Command(BaseCommand):
    help = "Create a sample email"

    def add_arguments(self, parser) -> None:
        parser.add_argument("from_address")
        parser.add_argument("to_address")
        parser.add_argument("--count", type=int, default=1)

    def handle(self, *args, **options):
        from_name, from_address = email.utils.parseaddr(options["from_address"])
        to_name, to_address = email.utils.parseaddr(options["to_address"])
        count = options["count"]

        now = timezone.now()

        with transaction.atomic():
            for i in range(count):
                outgoing = models.OutgoingMessage()
                outgoing.from_address = from_address
                outgoing.from_name = from_name
                outgoing.subject = "Test message"
                outgoing.discard_after = now + timedelta(hours=1)
                outgoing.text = f"This is a test message generated at {now}, sequence {i+1} of {count}"
                outgoing.html = f"<body><div>This is a <em>test</em> message generated at {now}, sequence {i+1} of {count}</div></body>"
                outgoing.save()

                send_addr = models.RelatedAddress()
                send_addr.message = outgoing
                send_addr.field = "to"
                send_addr.name = to_name
                send_addr.address = to_address
                send_addr.save()
