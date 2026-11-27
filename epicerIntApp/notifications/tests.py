from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase

from users.models import User

from .consumers import NotificationConsumer


class NotificationConsumerTests(SimpleTestCase):
    async def test_connected_user_can_open_websocket(self):
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/",
        )
        communicator.scope["user"] = User(email="member@example.com")

        connected, _ = await communicator.connect()

        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_anonymous_user_is_rejected(self):
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/",
        )
        communicator.scope["user"] = AnonymousUser()

        connected, _ = await communicator.connect()

        self.assertFalse(connected)
