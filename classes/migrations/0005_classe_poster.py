# Generated by Django 5.1.1 on 2024-11-22 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0004_arquivo_classe_arquivo_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='classe',
            name='poster',
            field=models.ImageField(blank=True, null=True, upload_to='classes/'),
        ),
    ]
