# Generated by Django 4.2.16 on 2024-11-23 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_alter_usuario_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$PtNi0IXAHHfhCJVMfUjREw$+SExuRKZkmvzxKX9S9+HBwKJwF52oeHwGhAvQXD5/Xs=', max_length=128),
        ),
    ]
