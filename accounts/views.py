from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from datetime import datetime
import os, shutil
from django.views.generic import TemplateView
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
from .forms import UsuarioForm
from django.shortcuts import render, redirect
from .forms import UsuarioForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Usuario
from classes.models import Classe, Arquivo, Deck, Card
from .forms import UsuarioUpdateForm
from django.db.models import Sum

from django.db.models import Q  # Import para busca com múltiplos critérios

from django.shortcuts import render, redirect
from .forms import UsuarioForm

class ListaAlunosView(TemplateView):
    template_name = 'accounts/lista_alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated and user.tipo == 1:  # Verifica se o usuário é um professor
            # Obtém todas as classes do professor
            classes = Classe.objects.filter(usuarios=user)

            # Coleta todos os alunos matriculados nas classes do professor, excluindo professores
            alunos = set()
            for classe in classes:
                alunos.update(classe.usuarios.filter(tipo=0))  # Inclui apenas usuários do tipo aluno

            # Aplica filtro de pesquisa se houver um termo no GET
            search_query = self.request.GET.get('q', '')
            if search_query:
                alunos = {aluno for aluno in alunos if 
                          search_query.lower() in aluno.username.lower() or 
                          search_query.lower() in aluno.email.lower()}

            # Cria um dicionário com informações detalhadas dos alunos
            alunos_detalhes = []
            for aluno in alunos:
                aluno_classes = Classe.objects.filter(usuarios=aluno)  # Classes em que o aluno está matriculado
                alunos_detalhes.append({
                    'aluno': aluno,
                    'classes': aluno_classes
                })

            context['alunos_detalhes'] = alunos_detalhes
            context['search_query'] = search_query  # Passa o termo de busca para o template

        return context


def registro_view(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)  # Inclua request.FILES
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirecione para a página de login
    else:
        form = UsuarioForm()
    return render(request, 'accounts/signup.html', {'form': form})

from django.db.models import Sum

from django.db.models import Count

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Inicializa valores padrão
        total_alunos = 0
        total_arquivos = 0
        total_cartoes_dominados = 0

        if user.is_authenticated:
            if user.tipo == 1:  # Professor
                # Calcula o total de alunos e arquivos
                classes = Classe.objects.filter(usuarios=user)
                total_alunos = sum(classe.usuarios.exclude(id=user.id).count() for classe in classes)
                total_arquivos = Arquivo.objects.filter(usuario=user).count()
            elif user.tipo == 0:  # Aluno
                # Calcula o total de cartões dominados
                total_cartoes_dominados = (
                    Card.objects.filter(deck__usuario=user, maduro=True).count()
                )

        # Adiciona os valores ao contexto
        context['total_alunos'] = total_alunos
        context['total_arquivos'] = total_arquivos
        context['total_cartoes_dominados'] = total_cartoes_dominados
        return context



def atualizar_perfil(request):
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')  # Redireciona para o perfil após salvar
    else:
        form = UsuarioUpdateForm(instance=request.user)
    return render(request, 'accounts/atualizar_perfil.html', {'form': form})