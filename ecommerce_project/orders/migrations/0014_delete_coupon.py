# Generated by Django 5.0.6 on 2024-09-04 10:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_coupon'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Coupon',
        ),
    ]
