# Generated by Django 4.1.11 on 2023-09-29 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_orderitem_delete_orderitems"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="stripe_id",
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
