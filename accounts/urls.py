from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registro_view, ListaAlunosView

app_name = 'accounts'
urlpatterns = [
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('profile/atualizar/', views.atualizar_perfil, name='atualizar_perfil'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('signup/', views.registro_view, name='signup'),
    path('alunos/', views.ListaAlunosView.as_view(), name='lista_alunos')
]