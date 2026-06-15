from tortoise import fields

from models.abstract_base_entity import AbstractBaseEntity


class AlbumReview(AbstractBaseEntity):
    description = fields.CharField(max_length=1000)

    spotify_album_id = fields.CharField(max_length=255)

    user = fields.ForeignKeyField("models.User", related_name="album_reviews")

    class Meta:
        table = "album_reviews"
