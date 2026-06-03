import json
import re
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.db import transaction


from .models import (
    Art,
    ArtStatus,
    IsHuman,
    IsFurry,
    PaymentStatus,
    PayoutStatus,
    PostState,
    PaymentPart,
    Payout,
    PayoutAllocation,
    PaymentPartStatus,
    current_order_month,
)
from .serializer import serialize_art


def validate_choice(value, choices, field_name):
    valid_values = [c[0] for c in choices]
    if value not in valid_values:
        return JsonResponse(
            {
                "detail": (
                    f"Недопустимое значение '{value}' для поля '{field_name}'. "
                    f"Допустимо одно из: {valid_values}"
                )
            },
            status=400,
        )
    return None


def validate_order_month(value):
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", str(value)):
        return JsonResponse(
            {"detail": "Поле 'order_month' должно быть в формате YYYY-MM."},
            status=400,
        )
    return None


def validation_error_response(err):
    if hasattr(err, "message_dict"):
        return JsonResponse({"detail": err.message_dict}, status=400)
    return JsonResponse({"detail": err.messages}, status=400)


def model_field_default(field_name):
    default = Art._meta.get_field(field_name).default
    if callable(default):
        return default()
    return default


def parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        return JsonResponse(
            {"detail": f"Поле '{field_name}' должно быть целым числом."},
            status=400,
        )


def healthcheck(request):
    return JsonResponse({"status": "ok", "app": "core"})


@csrf_exempt  # только для разработки, потом уберём/заменим на норм. аутентификацию
def arts_list(request):
    if request.method == "GET":
        qs = Art.objects.exclude(status=ArtStatus.DELETED)

        month = request.GET.get("month")
        if month:
            err = validate_order_month(month)
            if err:
                return err
            qs = qs.filter(order_month=month)

        qs = qs.order_by("-order_month", "-created_at")

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
                ("human_type", IsHuman.choices),
                ("furry_type", IsFurry.choices),
                ("bsky_posted", PostState.choices),
                ("decent_twi_posted", PostState.choices),
                ("lewd_twi_posted", PostState.choices),
                ("payment_status", PaymentStatus.choices),
                ("payout_status", PayoutStatus.choices),
        ):
            if fld in data and data[fld] is not None:
                err = validate_choice(data[fld], choices, fld)
                if err:
                    return err

        if "order_month" in data and data["order_month"] is not None:
            err = validate_order_month(data["order_month"])
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

        a = Art(
            name=name,
            status=data.get("status") or model_field_default("status"),
            human_type=(
                    data.get("human_type") or model_field_default("human_type")
            ),
            furry_type=(
                    data.get("furry_type") or model_field_default("furry_type")
            ),
            order_month=(
                    data.get("order_month") or model_field_default("order_month")
            ),
            price=price,
            payment_status=(
                    data.get("payment_status")
                    or model_field_default("payment_status")
            ),
            payout_status=(
                    data.get("payout_status")
                    or model_field_default("payout_status")
            ),
            # sfw/nsfw-флаги
            is_sfw=bool(data.get("is_sfw") or False),
            is_nsfw=bool(data.get("is_nsfw") or False),
            is_nsfw_plus_crop=bool(data.get("is_nsfw_plus_crop") or False),
            # куда планируем постить
            post_on_bsky=bool(data.get("post_on_bsky") or False),
            post_on_decent_twi=bool(data.get("post_on_decent_twi") or False),
            post_on_lewd_twi=bool(data.get("post_on_lewd_twi") or False),
            # статусы по площадкам
            bsky_posted=(
                    data.get("bsky_posted")
                    or model_field_default("bsky_posted")
            ),
            decent_twi_posted=(
                    data.get("decent_twi_posted")
                    or model_field_default("decent_twi_posted")
            ),
            lewd_twi_posted=(
                    data.get("lewd_twi_posted")
                    or model_field_default("lewd_twi_posted")
            ),
            # замок
            locked=bool(data.get("locked") or False),
        )
        try:
            a.full_clean()
        except ValidationError as err:
            return validation_error_response(err)

        a.save()
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
                ("human_type", IsHuman.choices),
                ("furry_type", IsFurry.choices),
                ("bsky_posted", PostState.choices),
                ("decent_twi_posted", PostState.choices),
                ("lewd_twi_posted", PostState.choices),
                ("payment_status", PaymentStatus.choices),
                ("payout_status", PayoutStatus.choices),
        ):
            if fld in data and data[fld] is not None:
                err = validate_choice(data[fld], choices, fld)
                if err:
                    return err

        if "order_month" in data and data["order_month"] is not None:
            err = validate_order_month(data["order_month"])
            if err:
                return err

        # частичное обновление: только присланные поля
        for field in [
            "name",
            "status",
            "human_type",
            "furry_type",
            "order_month",
            "payment_status",
            "payout_status",
            "bsky_posted",
            "decent_twi_posted",
            "lewd_twi_posted",
            "locked",
            "is_sfw",
            "is_nsfw",
            "is_nsfw_plus_crop",
        ]:
            if field in data and data[field] is not None:
                setattr(a, field, data[field])

        # булевы-флаги "куда планируем постить"
        for bfield in ["post_on_bsky", "post_on_decent_twi", "post_on_lewd_twi"]:
            if bfield in data and data[bfield] is not None:
                setattr(a, bfield, bool(data[bfield]))

        # price
        if "price" in data and data["price"] is not None:
            parsed = parse_int(data["price"], "price")
            if isinstance(parsed, JsonResponse):
                return parsed
            a.price = parsed

        try:
            a.full_clean()
        except ValidationError as err:
            return validation_error_response(err)

        a.save()
        return JsonResponse(serialize_art(a))

    if request.method == "DELETE":
        a.status = ArtStatus.DELETED
        a.save(update_fields=["status", "updated_at"])
        return JsonResponse(serialize_art(a))

    return HttpResponseNotAllowed(["GET", "PATCH", "PUT", "DELETE"])


def accounting_month(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    month = request.GET.get("month") or current_order_month()

    err = validate_order_month(month)
    if err:
        return err

    arts = Art.objects.exclude(status=ArtStatus.DELETED).filter(
        order_month=month,
        is_fanart=False,
    ).prefetch_related(
        "payment_parts__payout_allocations"
    )

    payouts = Payout.objects.filter(
        order_month=month,

    ).prefetch_related("allocations__payment_part__art")

    def serialize_accounting_order(art):
        payment_parts = list(art.payment_parts.all())

        paid_total_usd = sum(
            (part.amount_usd for part in payment_parts),
            Decimal("0"),
        )

        withdrawn_usd = sum(
            (
                allocation.amount_usd
                for part in payment_parts
                for allocation in part.payout_allocations.all()
            ),
            Decimal("0"),
        )

        broker_usd = paid_total_usd - withdrawn_usd
        expected_usd = Decimal(art.price) - paid_total_usd

        return {
            "id": art.id,
            "name": art.name,
            "status": art.status,
            "price": art.price,
            "paid_total_usd": str(paid_total_usd),
            "withdrawn_usd": str(withdrawn_usd),
            "broker_usd": str(broker_usd),
            "expected_usd": str(expected_usd),
            "payment_parts": [
                {
                    "id": part.id,
                    "amount_usd": str(part.amount_usd),
                    "status": part.status,
                    "note": part.note,
                }
                for part in payment_parts
            ],
        }

    return JsonResponse({
        "month": month,
        "orders": [
            serialize_accounting_order(art)
            for art in arts
        ],
        "payouts": [
            {
                "id": payout.id,
                "date": payout.date.isoformat(),
                "amount_usd": str(payout.amount_usd),
                "amount_rub": str(payout.amount_rub),
                "exchange_rate": str(payout.exchange_rate),
                "comment": payout.comment,
                "allocations": [
                    {
                        "id": allocation.id,
                        "payment_part_id": allocation.payment_part_id,
                        "art_id": allocation.payment_part.art_id,
                        "art_name": allocation.payment_part.art.name,
                        "amount_usd": str(allocation.amount_usd),
                    }
                    for allocation in payout.allocations.all()
                ],
            }
            for payout in payouts
        ],

    })

@csrf_exempt
def payment_parts_list(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    art_id = data.get("art_id")
    try:
        art = Art.objects.get(pk=art_id)
    except Art.DoesNotExist:
        return JsonResponse({"detail": "Art not found"}, status=404)

    amount_raw = data.get("amount_usd")
    try:
        amount_usd = Decimal(str(amount_raw))
    except Exception:
        return JsonResponse({"detail": "amount_usd must be a number"}, status=400)

    status = data.get("status") or PaymentPartStatus.RECEIVED
    err = validate_choice(status, PaymentPartStatus.choices, "status")
    if err:
        return err

    part = PaymentPart.objects.create(
        art=art,
        amount_usd=amount_usd,
        status=status,
        note=data.get("note") or "",
    )

    return JsonResponse({
        "id": part.id,
        "art_id": part.art_id,
        "amount_usd": str(part.amount_usd),
        "status": part.status,
        "note": part.note,
    }, status=201)


@csrf_exempt
def payment_part_detail(request, part_id: int):
    try:
        part = PaymentPart.objects.get(pk=part_id)
    except PaymentPart.DoesNotExist:
        return JsonResponse({"detail": "PaymentPart not found"}, status=404)

    if request.method in ("PATCH", "PUT"):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)

        if "amount_usd" in data and data["amount_usd"] is not None:
            try:
                part.amount_usd = Decimal(str(data["amount_usd"]))
            except Exception:
                return JsonResponse({"detail": "amount_usd must be a number"}, status=400)

        if "status" in data and data["status"] is not None:
            err = validate_choice(data["status"], PaymentPartStatus.choices, "status")
            if err:
                return err
            part.status = data["status"]

        if "note" in data and data["note"] is not None:
            part.note = data["note"]

        part.save()

        return JsonResponse({
            "id": part.id,
            "art_id": part.art_id,
            "amount_usd": str(part.amount_usd),
            "status": part.status,
            "note": part.note,
        })

    if request.method == "DELETE":
        part.delete()
        return JsonResponse({"deleted": True})

    return HttpResponseNotAllowed(["PATCH", "PUT", "DELETE"])

@csrf_exempt
def payouts_list(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    allocations_data = data.get("allocations") or []

    if not allocations_data:
        return JsonResponse(
            {"detail": "Нужно выбрать хотя бы один заказ для вывода."},
            status=400,
        )

    amount_rub_raw = data.get("amount_rub") or "0"

    try:
        amount_rub = Decimal(str(amount_rub_raw))
    except Exception:
        return JsonResponse(
            {"detail": "amount_rub должен быть числом."},
            status=400,
        )

    if amount_rub < 0:
        return JsonResponse(
            {"detail": "amount_rub не может быть меньше нуля."},
            status=400,
        )

    parsed_allocations = []
    total_usd = Decimal("0")

    for item in allocations_data:
        art_id = item.get("art_id")
        amount_raw = item.get("amount_usd")

        try:
            amount_usd = Decimal(str(amount_raw))
        except Exception:
            return JsonResponse(
                {"detail": "amount_usd должен быть числом."},
                status=400,
            )

        if amount_usd <= 0:
            continue

        try:
            art = Art.objects.get(pk=art_id)
        except Art.DoesNotExist:
            return JsonResponse(
                {"detail": f"Заказ art_id={art_id} не найден."},
                status=404,
            )

        parsed_allocations.append({
            "art": art,
            "amount_usd": amount_usd,
        })

        total_usd += amount_usd

    if total_usd <= 0:
        return JsonResponse(
            {"detail": "Сумма вывода должна быть больше нуля."},
            status=400,
        )

    order_month = parsed_allocations[0]["art"].order_month

    try:
        with transaction.atomic():
            payout = Payout.objects.create(
                order_month=order_month,
                amount_usd=total_usd,
                amount_rub=amount_rub,
            )

            for item in parsed_allocations:
                art = item["art"]
                amount_left = item["amount_usd"]

                payment_parts = PaymentPart.objects.filter(
                    art=art,
                ).prefetch_related("payout_allocations").order_by("created_at")

                for part in payment_parts:
                    already_allocated = sum(
                        (
                            allocation.amount_usd
                            for allocation in part.payout_allocations.all()
                        ),
                        Decimal("0"),
                    )

                    available = part.amount_usd - already_allocated

                    if available <= 0:
                        continue

                    amount_to_allocate = min(available, amount_left)

                    PayoutAllocation.objects.create(
                        payout=payout,
                        payment_part=part,
                        amount_usd=amount_to_allocate,
                    )

                    amount_left -= amount_to_allocate

                    if amount_left <= 0:
                        break

                if amount_left > 0:
                    raise ValueError(
                        f"У заказа '{art.name}' недостаточно денег у посредника."
                    )

    except ValueError as err:
        return JsonResponse({"detail": str(err)}, status=400)
    return JsonResponse({
        "id": payout.id,
        "order_month": payout.order_month,
        "date": payout.date.isoformat(),
        "amount_usd": str(payout.amount_usd),
        "amount_rub": str(payout.amount_rub),
        "exchange_rate": str(payout.exchange_rate),
    }, status=201)