# Generated manually for soft delete status.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_order_month_payment_payout"),
    ]

    operations = [
        migrations.AlterField(
            model_name="art",
            name="status",
            field=models.CharField(
                choices=[
                    ("done", "Готово"),
                    ("in_progress", "В процессе"),
                    ("cancelled", "Отменено"),
                    ("only_planned", "Только запланировано"),
                    ("waiting_to_start", "Ожидает начала"),
                    ("deleted", "Удалено"),
                ],
                db_index=True,
                default="only_planned",
                max_length=32,
            ),
        ),
    ]
