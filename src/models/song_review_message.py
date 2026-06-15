from tortoise import fields

from models.abstract_base_entity import AbstractBaseEntity


class SongReviewMessage(AbstractBaseEntity):
    text = fields.CharField(max_length=1000)
    user = fields.ForeignKeyField("models.User", related_name="song_review_messages")
    song_review = fields.ForeignKeyField(
        "models.SongReview", related_name="messages", null=True
    )
    parent = fields.ForeignKeyField(
        "models.SongReviewMessage", related_name="replies", null=True
    )

    class Meta:
        table = "song_review_messages"
