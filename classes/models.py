from django.db import models
from accounts.models import Usuario
from django.utils.timezone import now

class Classe(models.Model):
    turma = models.CharField(max_length=255)
    idioma = models.CharField(max_length=255)
    poster = models.ImageField(upload_to='classes/', blank=True, null=True)
    usuarios = models.ManyToManyField(Usuario)

    def __str__(self):
        return self.turma
    
    @property
    def poster_url(self):
        """Retorna a URL do poster ou uma imagem padrão."""
        if self.poster:
            return self.poster.url
        return '/static/images/Japan.svg'  # Substitua pelo caminho correto para sua imagem padrão

class Notificacao(models.Model):
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(default=now)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)  # Relaciona à classe, se aplicável
    lida = models.BooleanField(default=False)  # Para marcar se o usuário já viu a notificação

    def __str__(self):
        return f"Notificação para {self.usuario.username}: {self.titulo}"
    
class Deck(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    idioma = models.CharField(max_length=255)
    
    @property
    def n_dominados(self):
        return self.card_set.filter(maduro=True).count()

    @property
    def n_cartoes(self):
        return self.card_set.count()


    @property
    def n_aprender(self):
        return self.n_cartoes - self.n_dominados

    def __str__(self):
        return self.nome


class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, )
    lado_frente = models.CharField(max_length=255)
    lado_tras = models.CharField(max_length=255)
    dica_1 = models.CharField(max_length=255, blank=True, null=True)
    dica_2 = models.CharField(max_length=255, blank=True, null=True)
    dica_3 = models.CharField(max_length=255, blank=True, null=True)
    n_revisoes = models.IntegerField(default=0)
    maduro = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_revisao = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.lado_frente

class Mensagem(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='mensagens' )
    conteudo = models.TextField(max_length=1000)
    data_envio = models.DateTimeField(auto_now_add=True)
    resposta_para = models.ForeignKey(
        'self',  # Faz referência ao próprio modelo
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='respostas'  # Permite acessar as respostas de uma mensagem
    )

    def __str__(self):
        return f"Mensagem de {self.usuario}"
    
class Arquivo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)  # Nome do arquivo
    tipo = models.CharField(max_length=50, default='PDF')  # Tipo do arquivo (ex: application/pdf)
    conteudo = models.BinaryField(default=b'')# Armazena o conteúdo binário do arquivo
    data_upload = models.DateTimeField(auto_now_add=True, null=True)  # Data de envio

    def __str__(self):
        return self.nome