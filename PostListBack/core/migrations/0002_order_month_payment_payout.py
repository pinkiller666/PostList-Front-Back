# Generated manually for order month and payment tracking.

import core.models
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="art",
            name="order_month",
            field=models.CharField(
                db_index=True,
                default=core.models.current_order_month,
                help_text="Месяц заказа в формате YYYY-MM.",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Месяц заказа должен быть в формате YYYY-MM.",
                        regex="^\\d{4}-(0[1-9]|1[0-2])$",
                    )
                ],
            ),
        ),
        migrations.AddField(
            model_name="art",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("unpaid", "Не оплачена"),
                    ("partially_paid", "Частично оплачена"),
                    ("fully_paid", "Фул оплачена"),
                    ("half_before_sketch", "Половина до скетча"),
                ],
                db_index=True,
                default="unpaid",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="art",
            name="payout_status",
            field=models.CharField(
                choices=[
                    ("not_withdrawn", "Не выведено"),
                    ("withdrawn", "Выведено"),
                ],
                db_index=True,
                default="not_withdrawn",
                max_length=32,
            ),
        ),
        migrations.AlterModelOptions(
            name="art",
            options={"ordering": ("-order_month", "-created_at")},
        ),
    ]
