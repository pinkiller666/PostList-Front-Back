from .models import Art


def serialize_art(a: Art) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "status": a.status,
        "human_type": a.human_type,
        "furry_type": a.furry_type,
        "price": a.price,
        "post_on_bsky": a.post_on_bsky,
        "post_on_decent_twi": a.post_on_decent_twi,
        "post_on_lewd_twi": a.post_on_lewd_twi,
        "bsky_posted": a.bsky_posted,
        "decent_twi_posted": a.decent_twi_posted,
        "lewd_twi_posted": a.lewd_twi_posted,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
        "locked": a.locked,
    }
