# Generated by Django 3.2.16 on 2023-01-12 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]