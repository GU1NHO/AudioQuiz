# Generated by Django 4.2.16 on 2024-11-27 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_alter_usuario_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$UrPhV36R734Duyp8pEMpYL$zHS9y3Ow4cICjvt17orQRVY6Xjd7cf8FNsjzashAEig=', max_length=128),
        ),
    ]
