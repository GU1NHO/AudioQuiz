# Generated by Django 5.1.1 on 2024-11-23 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_alter_usuario_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$PpnaGRaM2CD64FBxD1kngS$EgnD5QBXxVdCMehM5k3E+uzUw49ytjwvlVc6fdregzE=', max_length=128),
        ),
    ]
