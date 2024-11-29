from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Classe)
admin.site.register(models.Notificacao)
admin.site.register(models.Deck)
admin.site.register(models.Card)
admin.site.register(models.Mensagem)
admin.site.register(models.Arquivo)