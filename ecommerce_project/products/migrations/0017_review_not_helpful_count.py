# Generated by Django 5.0.6 on 2024-09-15 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_review_helpful_count_review_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='not_helpful_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]