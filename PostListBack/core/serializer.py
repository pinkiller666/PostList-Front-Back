from .models import Art


def serialize_art(a: Art) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "status": a.status,
        "human_type": a.human_type,
        "furry_type": a.furry_type,
        "order_month": a.order_month,
        "price": a.price,
        "payment_status": a.payment_status,
        "payout_status": a.payout_status,
        "is_sfw": a.is_sfw,
        "is_nsfw": a.is_nsfw,
        "is_nsfw_plus_crop": a.is_nsfw_plus_crop,
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
