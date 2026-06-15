from datetime import datetime

from tortoise import Model, fields


class AbstractBaseEntity(Model):
    id = fields.UUIDField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    async def soft_delete(self) -> None:
        self.deleted_at = datetime.now()
        await self.save()

    class Meta:
        abstract = True
