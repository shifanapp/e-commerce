# Generated by Django 5.0.6 on 2024-08-21 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_orderitem_cart_cartitem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='owner',
            new_name='order',
        ),
    ]
