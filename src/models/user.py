from tortoise import fields

from models.abstract_base_entity import AbstractBaseEntity


class User(AbstractBaseEntity):
    google_id = fields.CharField(max_length=255, unique=True, db_index=True)
    google_email = fields.CharField(
        max_length=255, unique=True, db_index=True, null=True
    )
    email_verified = fields.BooleanField(null=True)
    name = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    picture_url = fields.CharField(max_length=512, null=True)
    hosted_domain = fields.CharField(max_length=255, null=True)

    spotify_refresh_token = fields.CharField(max_length=512, null=True)
    spotify_access_token = fields.CharField(max_length=512, null=True)
    spotify_access_token_expires_at = fields.DatetimeField(null=True)

    refresh_token = fields.CharField(max_length=512, null=True)

    class Meta:
        table = "users"
