# Generated by Django 5.1.1 on 2024-11-23 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_alter_usuario_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$pbleYtYtTJRWQAm3DrJ9IN$zjvRn5jSVg7PT2jaXZtnQpuXgJ8glc9duFP4e/yOKFs=', max_length=128),
        ),
    ]