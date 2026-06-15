from tortoise import fields

from models.abstract_base_entity import AbstractBaseEntity


class User(AbstractBaseEntity):
    spotify_id = fields.CharField(max_length=255, unique=True, db_index=True)
    email = fields.CharField(max_length=255, db_index=True, null=True)
    name = fields.CharField(max_length=255, null=True)
    picture_url = fields.CharField(max_length=512, null=True)

    spotify_refresh_token = fields.CharField(max_length=512, null=True)
    spotify_access_token = fields.CharField(max_length=512, null=True)
    spotify_access_token_expires_at = fields.DatetimeField(null=True)

    refresh_token = fields.CharField(max_length=512, null=True)

    class Meta:
        table = "users"
