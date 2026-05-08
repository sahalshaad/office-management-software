from channels.generic.websocket import AsyncJsonWebsocketConsumer


class OfficeFlowConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        self.user_group = f"user_{user.pk}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        if getattr(user, "is_admin_role", False):
            await self.channel_layer.group_add("attendance", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(f"user_{user.pk}", self.channel_name)
            if getattr(user, "is_admin_role", False):
                await self.channel_layer.group_discard("attendance", self.channel_name)

    async def notification_event(self, event):
        await self.send_json({"kind": "notification", **event})

    async def attendance_event(self, event):
        await self.send_json({"kind": "attendance", **event})
