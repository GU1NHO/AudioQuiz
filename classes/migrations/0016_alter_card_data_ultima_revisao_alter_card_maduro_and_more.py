# Generated by Django 5.1.1 on 2024-11-23 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0015_remove_deck_n_aprender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='data_ultima_revisao',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='maduro',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='card',
            name='n_revisoes',
            field=models.IntegerField(default=0),
        ),
    ]
