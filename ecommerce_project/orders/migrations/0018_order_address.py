# Generated by Django 5.0.6 on 2024-09-17 07:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_rename_postal_code_address_zip_code_and_more'),
        ('orders', '0017_alter_cartitem_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customers.address'),
        ),
    ]