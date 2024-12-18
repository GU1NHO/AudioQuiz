# Generated by Django 4.2.16 on 2024-11-22 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('classes', '0003_arquivo_conteudo_arquivo_data_upload_arquivo_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='arquivo',
            name='classe',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='classes.classe'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='arquivo',
            name='usuario',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.usuario'),
            preserve_default=False,
        ),
    ]
