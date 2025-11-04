import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Art, ArtStatus, HowLewd, IsHuman, IsFurry, PostState


def validate_choice(value, choices, field_name):
    valid_values = [c[0] for c in choices]
    if value not in valid_values:
        return JsonResponse({
            "detail": (
                f"Недопустимое значение '{value}' для поля '{field_name}'. "
                f"Допустимо одно из: {valid_values}"
            )
        }, status=400)
    return None


def parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        return JsonResponse({
            "detail": f"Поле '{field_name}' должно быть целым числом."
        }, status=400)


def serialize_art(a: Art) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "status": a.status,
        "how_lewd": a.how_lewd,
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
    }


def healthcheck(request):
    return JsonResponse({"status": "ok", "app": "core"})


@csrf_exempt  # только для разработки, потом уберём/заменим на норм. аутентификацию
def arts_list(request):
    if request.method == "GET":
        qs = Art.objects.all().order_by("-created_at")
        return JsonResponse({"items": [serialize_art(a) for a in qs]})

    if request.method == "POST":
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)

        name = (data.get("name") or "").strip()
        if not name:
            return JsonResponse({"detail": "Field 'name' is required"}, status=400)

        # choices валидация
        for fld, choices in (
            ("status", ArtStatus.choices),
            ("how_lewd", HowLewd.choices),
            ("human_type", IsHuman.choices),
            ("furry_type", IsFurry.choices),
            ("bsky_posted", PostState.choices),
            ("decent_twi_posted", PostState.choices),
            ("lewd_twi_posted", PostState.choices),
        ):
            if fld in data and data[fld] is not None:
                err = validate_choice(data[fld], choices, fld)
                if err:
                    return err

        # price
        if "price" in data and data["price"] is not None:
            parsed = parse_int(data["price"], "price")
            if isinstance(parsed, JsonResponse):
                return parsed
            price = parsed
        else:
            price = 0

        a = Art.objects.create(
            name=name,
            status=data.get("status") or Art._meta.get_field("status").default,
            how_lewd=data.get("how_lewd") or Art._meta.get_field("how_lewd").default,
            human_type=data.get("human_type") or Art._meta.get_field("human_type").default,
            furry_type=data.get("furry_type") or Art._meta.get_field("furry_type").default,
            price=price,
            post_on_bsky=bool(data.get("post_on_bsky") or False),
            post_on_decent_twi=bool(data.get("post_on_decent_twi") or False),
            post_on_lewd_twi=bool(data.get("post_on_lewd_twi") or False),
            bsky_posted=data.get("bsky_posted") or Art._meta.get_field("bsky_posted").default,
            decent_twi_posted=data.get("decent_twi_posted") or Art._meta.get_field("decent_twi_posted").default,
            lewd_twi_posted=data.get("lewd_twi_posted") or Art._meta.get_field("lewd_twi_posted").default,
        )
        return JsonResponse(serialize_art(a), status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def art_detail(request, art_id: int):
    try:
        a = Art.objects.get(pk=art_id)
    except Art.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(serialize_art(a))

    if request.method in ("PATCH", "PUT"):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)

        # choices валидация
        for fld, choices in (
            ("status", ArtStatus.choices),
            ("how_lewd", HowLewd.choices),
            ("human_type", IsHuman.choices),
            ("furry_type", IsFurry.choices),
            ("bsky_posted", PostState.choices),
            ("decent_twi_posted", PostState.choices),
            ("lewd_twi_posted", PostState.choices),
        ):
            if fld in data and data[fld] is not None:
                err = validate_choice(data[fld], choices, fld)
                if err:
                    return err

        # частичное обновление: только присланные поля
        for field in [
            "name", "status", "how_lewd", "human_type", "furry_type",
            "bsky_posted", "decent_twi_posted", "lewd_twi_posted",
        ]:
            if field in data and data[field] is not None:
                setattr(a, field, data[field])

        for bfield in ["post_on_bsky", "post_on_decent_twi", "post_on_lewd_twi"]:
            if bfield in data and data[bfield] is not None:
                setattr(a, bfield, bool(data[bfield]))

        if "price" in data and data["price"] is not None:
            parsed = parse_int(data["price"], "price")
            if isinstance(parsed, JsonResponse):
                return parsed
            a.price = parsed

        a.save()
        return JsonResponse(serialize_art(a))

    if request.method == "DELETE":
        a.delete()
        return JsonResponse({"deleted": True})

    return HttpResponseNotAllowed(["GET", "PATCH", "PUT", "DELETE"])
