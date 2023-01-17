# Generated by Django 3.2.16 on 2023-01-15 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_recipe_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]