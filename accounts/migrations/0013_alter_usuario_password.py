# Generated by Django 4.2.16 on 2024-11-22 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_usuario_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$PbJfL7nMVZtSE8gH0SsTSj$VOOVx/VNzUk46G7VsOUjyeKLPKMtuXlVjSWPWTLL+FI=', max_length=128),
        ),
    ]
