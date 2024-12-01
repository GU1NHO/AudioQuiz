from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from datetime import datetime
import os, shutil
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import  Notificacao, Classe, Deck, Card, Mensagem, Arquivo
from .forms import ClasseForm, ArquivoForm, DeckForm, CardForm, MensagemForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.safestring import mark_safe
import json
from django.http import JsonResponse
from django.utils.timezone import now
import os
import speech_recognition as sr
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
from pydub.utils import which
import logging
import os
import sounddevice as sd
import numpy as np
import wave
import logging
from pydub import AudioSegment
import speech_recognition as sr
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess

class ClasseListView(ListView):
    model = Classe
    template_name = 'classes/index.html'

class ClasseDeleteView(DeleteView):
    model = Classe
    template_name = 'classes/delete.html'
    success_url = reverse_lazy('classes:index')

class ClasseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'classes/update.html'
    success_url = reverse_lazy('classes:index')

    def form_valid(self, form):
        classe = form.save(commit=False)
        classe.save()
        form.save_m2m()  # Salvar alunos selecionados
        # Verifica novos alunos para evitar notificações duplicadas
        novos_alunos = form.cleaned_data['alunos'].exclude(id__in=classe.usuarios.all())
        classe.usuarios.add(self.request.user)  # Adiciona o professor à classe
        self.enviar_notificacao_para_alunos(novos_alunos, classe)
        return super().form_valid(form)

    def enviar_notificacao_para_alunos(self, novos_alunos, classe):
        """Envia notificações apenas para novos alunos convidados"""
        for aluno in novos_alunos:
            Notificacao.objects.create(
                titulo="Convite para a classe",
                mensagem=f"Você foi convidado para a classe '{classe.turma}' de {classe.idioma}.",
                classe=classe,
                usuario=aluno
            )
    def test_func(self):
        # Permitir acesso apenas para professores
        return self.request.user.is_authenticated and self.request.user.tipo == 1

class MensagemDeleteView(DeleteView):
    model = Mensagem
    template_name = 'classes/mural/delete.html'

    def get_object(self, queryset=None):
        # Recupera o objeto Mensagem usando o mensagem_id
        mensagem_id = self.kwargs.get('mensagem_id')
        return get_object_or_404(Mensagem, pk=mensagem_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o objeto Classe ao contexto
        context['Classe'] = get_object_or_404(Classe, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redireciona de volta para o mural da classe
        return reverse_lazy('classes:mural', kwargs={'pk': self.kwargs['pk']})

class ClasseMuralView(View):
    def get(self, request, pk):
        classe = get_object_or_404(Classe, pk=pk)
        mensagens = classe.mensagens.filter(resposta_para__isnull=True)  # Apenas mensagens principais
        return render(request, 'classes/mural/index.html', {'Classe': classe, 'mensagens': mensagens})

class ClasseAtividadesView(DetailView):
    model = Classe
    template_name = 'classes/atividades/index.html'
    context_object_name = 'Classe'

class AtividadeCreateView(View):
    def get(self, request, pk):
        classe = get_object_or_404(Classe, pk=pk)# Garante que a Classe existe
        form = ArquivoForm()
        return render(request, 'classes/atividades/atividade.html', {'form': form, 'Classe': classe})

    def post(self, request, pk):
        classe = get_object_or_404(Classe, pk=pk)
        form = ArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.classe = classe
            arquivo.usuario = request.user  # Associa o usuário autenticado
            arquivo.tipo = request.FILES['conteudo'].content_type
            arquivo.conteudo = request.FILES['conteudo'].read()
            arquivo.save()
            return HttpResponseRedirect(reverse_lazy('classes:atividades_index', kwargs={'pk': pk}))
        return render(request, 'classes/atividades/atividade.html', {'form': form, 'Classe': classe})

class AtividadeDeleteView(DeleteView):
    model = Arquivo  # Corrige para deletar o modelo Arquivo (atividade)
    template_name = 'classes/atividades/delete.html'
    
    def get_success_url(self):
        # Retorna para a lista de atividades da classe após a exclusão
        return reverse_lazy('classes:atividades_index', kwargs={'pk': self.object.classe.id})

class AtividadeUpdateView(View):
    def get(self, request, pk):
        # Recupera a atividade pelo ID
        atividade = get_object_or_404(Arquivo, pk=pk)
        form = ArquivoForm(instance=atividade)  # Preenche o formulário com os dados da atividade existente
        return render(request, 'classes/atividades/update.html', {'form': form, 'atividade': atividade})

    def post(self, request, pk):
        # Recupera a atividade pelo ID
        atividade = get_object_or_404(Arquivo, pk=pk)
        form = ArquivoForm(request.POST, request.FILES, instance=atividade)  # Associa o formulário à atividade
        if form.is_valid():
            arquivo = form.save(commit=False)
            
            # Verifica se um novo arquivo foi enviado
            if 'conteudo' in request.FILES:
                arquivo.tipo = request.FILES['conteudo'].content_type
                arquivo.conteudo = request.FILES['conteudo'].read()

            arquivo.save()  # Salva as alterações na atividade
            return HttpResponseRedirect(reverse_lazy('classes:atividades_index', kwargs={'pk': atividade.classe.pk}))

        return render(request, 'classes/atividades/update.html', {'form': form, 'atividade': atividade})

def download_pdf(request, pk):
    # Recupera o arquivo pelo ID
    arquivo = get_object_or_404(Arquivo, pk=pk)

    try:
        # Retorna o conteúdo binário como resposta para download
        response = HttpResponse(arquivo.conteudo, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{arquivo.nome}.pdf"'
        return response
    except Exception as e:
        raise Http404("Erro ao processar o arquivo")

class ClasseFlashcardsView(DetailView):
    model = Classe
    template_name = 'classes/flashcards/index.html'
    context_object_name = 'Classe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classe = self.object  # A classe atual (detalhe sendo exibido)

        # Adiciona a Classe ao contexto
        context['Classe'] = classe

        # Filtra decks associados à classe, ao usuário logado e ao tipo de usuário
        if self.request.user.tipo == 0:  # Garante que o filtro é feito apenas para tipo 0
            context['Deck_list'] = Deck.objects.filter(classe=classe, usuario=self.request.user)
        else:
            context['Deck_list'] = Deck.objects.filter(classe=classe)  # Nenhum deck se o tipo não for 0

        return context

class ClasseFlashcardsCreate(CreateView):
    model = Deck
    form_class = DeckForm
    template_name = 'classes/flashcards/create.html'

    def form_valid(self, form):
        """
        Define a classe e o usuário associados ao deck e salva.
        """
        classe = get_object_or_404(Classe, pk=self.kwargs['pk'])
        form.instance.classe = classe
        form.instance.usuario = self.request.user
        self.object = form.save()  # Salva e armazena o objeto criado
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Classe'] = get_object_or_404(Classe, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        """
        Redireciona para a página de flashcards da classe.
        """
        return reverse_lazy('classes:flashcards', kwargs={'pk': self.object.classe.pk})
    
class ClasseFlashcardsDelete(DeleteView):
    model = Deck
    template_name = 'classes/flashcards/delete.html'

    def get_object(self, queryset=None):
        print(f"Classe ID: {self.kwargs['pk']}, Deck ID: {self.kwargs['deck_id']}")
        return get_object_or_404(Deck, pk=self.kwargs['deck_id'], classe_id=self.kwargs['pk'])

    def get_success_url(self):
        # Redireciona para a lista de flashcards após a exclusão
        return reverse_lazy('classes:flashcards', kwargs={'pk': self.kwargs['pk']})
    
class CardCreateView(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'classes/flashcards/cards/create.html'

    def form_valid(self, form):
        """
        Define o deck associado ao card e salva.
        """
        deck = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        form.instance.deck = deck
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Adiciona o deck ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context['deck'] = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        return context

    def get_success_url(self):
        """
        Redireciona para o deck após criar o card.
        """
        return reverse_lazy('classes:cards_in_deck', kwargs={
            'deck_id': self.kwargs['deck_id'],
        })


class CardDetailView(DetailView):
    model = Card
    template_name = "classes/flashcards/cards/cards.html"
    context_object_name = "card"

    def get_object(self):
        """Sobrescreve get_object para retornar um card específico ou o primeiro do deck."""
        deck_id = self.kwargs['deck_id']
        pk = self.kwargs.get('pk')

        # Se um ID de card for fornecido, tenta buscar por ele
        if pk:
            return get_object_or_404(Card, pk=pk, deck_id=deck_id)

        # Caso contrário, retorna o primeiro card do deck
        deck = get_object_or_404(Deck, pk=deck_id)
        first_card = deck.card_set.first()
        if not first_card:
            raise Http404("Nenhum card disponível neste deck.")
        return first_card

    def get_context_data(self, **kwargs):
        """Adiciona navegação ao contexto e verifica se o deck possui cards."""
        context = super().get_context_data(**kwargs)
        card = self.get_object()
        deck = card.deck

        # Próximo card
        next_card = deck.card_set.filter(id__gt=card.id).first()

        # Card anterior
        prev_card = deck.card_set.filter(id__lt=card.id).last()

        # Adiciona deck e navegação ao contexto
        context['deck'] = deck
        context['next_card'] = next_card  # None se não houver próximo
        context['prev_card'] = prev_card  # None se não houver anterior
        context['has_cards'] = deck.card_set.exists()  # Verifica se o deck tem cards
        return context

class ClasseCreateView(CreateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'classes/create.html'
    success_url = reverse_lazy('classes:index')

    def form_valid(self, form):
        # Salva a classe sem commit
        classe = form.save(commit=False)
        # Salva a instância da classe
        classe.save()
        # Salva a relação N pra N dos usuários selecionados
        form.save_m2m()
        # Adiciona o usuário logado à relação N pra N como criador/professor
        classe.usuarios.add(self.request.user)
        # Envia notificações para os alunos selecionados
        self.enviar_notificacao_para_alunos(form.cleaned_data['alunos'], classe)
        return super().form_valid(form)

    def enviar_notificacao_para_alunos(self, alunos, classe):
        """Envia notificações para os alunos convidados"""
        for aluno in alunos:
            Notificacao.objects.create(
                titulo="Convite para a classe",
                mensagem=f"Você foi convidado para a classe '{classe.turma}' de {classe.idioma}.",
                classe = classe,
                usuario = aluno
            )

class MensagemCreateView(View):
    def get(self, request, pk, resposta_id=None):
        classe = get_object_or_404(Classe, pk=pk)
        resposta_para = None
        if resposta_id:
            resposta_para = get_object_or_404(Mensagem, pk=resposta_id)
        form = MensagemForm()
        return render(request, 'classes/mural/mensagem.html', {'form': form, 'Classe': classe, 'resposta_para': resposta_para})

    def post(self, request, pk, resposta_id=None):
        classe = get_object_or_404(Classe, pk=pk)
        resposta_para = None
        if resposta_id:
            resposta_para = get_object_or_404(Mensagem, pk=resposta_id)
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.classe = classe
            mensagem.usuario = request.user
            mensagem.resposta_para = resposta_para
            mensagem.save()
            return HttpResponseRedirect(reverse_lazy('classes:mural', kwargs={'pk': pk}))
        return render(request, 'classes/mural/mensagem.html', {'form': form, 'Classe': classe})

def aceitar_convite(request, notificacao_id):
    # Verifica se o usuário está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para aceitar o convite.")
        return redirect('accounts:login')

    # Obtém a classe e a notificação
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    classe = get_object_or_404(Classe, id=notificacao.classe_id)

    # Adiciona o usuário à classe
    classe.usuarios.add(request.user)

    # Marca a notificação como lida
    notificacao.lida = True
    notificacao.save()

    messages.success(request, f"Você agora faz parte da classe '{classe.turma}'.")
    return redirect('classes:index')  # Redireciona para a página inicial ou lista de classes

@login_required
def recusar_convite(request, notificacao_id):
    """
    View para recusar o convite de uma classe.
    """
    # Obtém a notificação
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)

    # Exclui a notificação, já que o convite foi recusado
    notificacao.delete()

    # Adiciona uma mensagem de sucesso
    messages.success(request, "Você recusou o convite para a classe.")

    # Redireciona o usuário para uma página apropriada (ex: página inicial ou painel de notificações)
    return redirect('classes:index')  # Substitua pelo nome correto da URL

def marcar_maduro_proximo(request, deck_id, pk):
    if request.method == "POST":
        card = get_object_or_404(Card, pk=pk, deck_id=deck_id)

        # Atualiza o card atual
        card.maduro = True
        card.data_ultima_revisao = now()
        card.save()

        # Busca o próximo card
        next_card = card.deck.card_set.filter(id__gt=card.id).first()

        # Identifica a classe associada ao deck
        deck = card.deck
        classe_id = deck.classe.id

        # Define a URL de redirecionamento
        if next_card:
            redirect_url = reverse('classes:cards', args=[deck.id, next_card.id])
        else:
            redirect_url = reverse('classes:flashcards', args=[classe_id])

        # Verifica se a requisição foi feita via AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': redirect_url})

        # Para requisições normais, redireciona diretamente
        return redirect(redirect_url)

    return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)

def desmarcar_maduro_proximo(request, deck_id, pk):
    """
    Desmarca o card como maduro, atualiza a data de última revisão,
    e redireciona para o próximo card ou para a página de flashcards da classe.
    """
    if request.method == "POST":
        card = get_object_or_404(Card, pk=pk, deck_id=deck_id)

        # Atualiza o card atual
        card.maduro = False
        card.data_ultima_revisao = now()
        card.save()

        # Busca o próximo card
        next_card = card.deck.card_set.filter(id__gt=card.id).first()

        # Identifica a classe associada ao deck
        deck = card.deck
        classe_id = deck.classe.id  # Substitua pelo campo correto que liga Deck à Classe

        # Redireciona para o próximo card ou para a página de flashcards da classe
        if next_card:
            redirect_url = reverse('classes:cards', args=[deck.id, next_card.id])
        else:
            redirect_url = reverse('classes:flashcards', args=[classe_id])

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': redirect_url})

        # Para requisições normais, redireciona diretamente
        return redirect(redirect_url)

    return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)


class CardsInDeckListView(ListView):
    model = Card
    template_name = "classes/flashcards/cards/cards_list.html"  # Substitua pelo nome do seu template
    context_object_name = "cards"
    paginate_by = 10  # Número de cards por página (opcional)

    def get_queryset(self):
        """
        Filtra os cards pelo deck fornecido na URL.
        """
        deck = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        return Card.objects.filter(deck=deck)

    def get_context_data(self, **kwargs):
        """
        Adiciona o deck ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context['deck'] = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        return context

class CardDeleteView(DeleteView):
    model = Card
    template_name = 'classes/flashcards/cards/delete.html'

    def get_object(self, queryset=None):
        """
        Recupera o objeto Card usando o card_id da URL.
        """
        card_id = self.kwargs.get('card_id')
        return get_object_or_404(Card, pk=card_id)

    def get_context_data(self, **kwargs):
        """
        Adiciona informações do Deck ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context['deck'] = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        return context

    def get_success_url(self):
        """
        Redireciona para a lista de cards no deck após a exclusão.
        """
        return reverse_lazy('classes:cards_in_deck', kwargs={'deck_id': self.object.deck.id})
    
class CardUpdateView(UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'classes/flashcards/cards/update.html'

    def form_valid(self, form):
        """
        Confirma as alterações feitas no card e mantém o deck associado.
        """
        deck = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        form.instance.deck = deck
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Adiciona o deck ao contexto para o template.
        """
        context = super().get_context_data(**kwargs)
        context['deck'] = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        return context

    def get_success_url(self):
        # Redireciona de volta para o mural da classe
        return reverse_lazy('classes:cards_in_deck', kwargs={'deck_id': self.kwargs['deck_id']})

logger = logging.getLogger(__name__)

# Função para capturar áudio com sounddevice
def record_audio(duration=3, fs=44100):
    # duration em segundos, fs = frequência de amostragem (44.1kHz padrão para áudio)
    logger.info("Iniciando gravação com sounddevice...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Espera até que a gravação termine
    return audio_data, fs

logger = logging.getLogger(__name__)

@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST':
        try:
            # Verificar se o arquivo foi enviado
            if 'audio' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'Nenhum arquivo de áudio enviado.'}, status=400)
            
            audio_file = request.FILES['audio']
            
            # Define os caminhos para salvar os arquivos
            media_dir = os.path.join(settings.MEDIA_ROOT, 'classes')
            os.makedirs(media_dir, exist_ok=True)  # Garante que o diretório existe

            webm_path = os.path.join(media_dir, 'uploaded_audio.webm')
            wav_path = os.path.join(media_dir, 'uploaded_audio.wav')

            # Salvar o arquivo .webm enviado
            with open(webm_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            
            logger.info(f"Arquivo .webm salvo em: {webm_path}")

            # Converter o arquivo .webm para .wav usando FFmpeg
            try:
                subprocess.run(
                    ['ffmpeg', '-i', webm_path, '-ar', '16000', '-ac', '1', wav_path],
                    check=True
                )
                logger.info(f"Conversão para .wav concluída: {wav_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Erro ao converter .webm para .wav: {str(e)}")
                return JsonResponse({'success': False, 'error': 'Falha na conversão de áudio.'}, status=500)

            # Processar o arquivo WAV com reconhecimento de fala
            r = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = r.record(source)
                transcribed_text = r.recognize_google(audio_data, language="pt-BR")
            
            logger.info(f"Transcrição concluída: {transcribed_text}")
            return JsonResponse({'success': True, 'transcription': transcribed_text})

        except Exception as e:
            logger.error(f"Erro ao processar áudio: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Método inválido!'}, status=400)
