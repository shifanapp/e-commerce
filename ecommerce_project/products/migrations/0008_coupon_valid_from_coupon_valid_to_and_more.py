# Generated by Django 5.0.6 on 2024-09-04 08:02

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='valid_from',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coupon',
            name='valid_to',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coupon',
            name='coupon_code',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='minimum_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]