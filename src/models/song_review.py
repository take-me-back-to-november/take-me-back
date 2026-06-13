from tortoise import fields

from models.abstract_base_entity import AbstractBaseEntity


class SongReview(AbstractBaseEntity):
    stars_count = fields.IntField()
    text = fields.TextField()

    likes_count = fields.IntField(default=0)
    unlikes_count = fields.IntField(default=0)

    spotify_song_id = fields.CharField(max_length=255)

    song_name = fields.CharField(max_length=255, null=True)
    song_artist = fields.CharField(max_length=255, null=True)
    song_album = fields.CharField(max_length=255, null=True)

    image_url = fields.CharField(max_length=512, null=True)

    user = fields.ForeignKeyField("models.User", related_name="song_reviews")

    class Meta:
        table = "song_reviews"
