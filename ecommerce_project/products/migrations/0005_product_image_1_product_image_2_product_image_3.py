# Generated by Django 5.0.6 on 2024-07-10 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_1',
            field=models.ImageField(default='null', null=True, upload_to='media'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_2',
            field=models.ImageField(default='null', null=True, upload_to='media'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_3',
            field=models.ImageField(default='null', null=True, upload_to='media'),
        ),
    ]