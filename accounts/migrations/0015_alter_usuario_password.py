# Generated by Django 4.2.16 on 2024-11-22 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_usuario_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$dAdWJ9Jnm8kS2oxWFxhmvm$u/WOY2VmUjwFQxP1GBscj89O3DCG/YxB5yPBvn09ndQ=', max_length=128),
        ),
    ]
