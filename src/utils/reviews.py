from models.song_review import SongReview


def to_song_review_response(review: SongReview) -> dict:
    return {
        "id": review.id,
        "stars_count": review.stars_count,
        "text": review.text,
        "image_url": review.image_url,
        "song_name": review.song_name,
        "song_artist": review.song_artist,
        "song_album": review.song_album,
        "likes_count": review.likes_count,
        "unlikes_count": review.unlikes_count,
        "spotify_song_id": review.spotify_song_id,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
    }
