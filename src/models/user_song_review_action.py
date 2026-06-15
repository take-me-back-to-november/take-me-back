from tortoise import fields

from models.abstract_base_entity import AbstractBaseEntity


class UserSongReviewAction(AbstractBaseEntity):
    action = fields.CharField(max_length=10, choices=["like", "unlike"])
    user = fields.ForeignKeyField("models.User", related_name="song_review_actions")
    song_review = fields.ForeignKeyField(
        "models.SongReview", related_name="song_review_actions"
    )

    class Meta:
        table = "user_song_review_actions"
        unique_together = (("user", "song_review"),)
