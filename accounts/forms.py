from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Senha",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirme a Senha",
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo', 'poster', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(choices=[(True, "Professor"), (False, "Aluno")], attrs={'class': 'form-control'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': "Nome de Usuário",
            'email': "E-mail",
            'first_name': "Primeiro Nome",
            'last_name': "Sobrenome",
            'tipo': "Tipo de Usuário",
            'poster': "Imagem de Perfil",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        # Salva o usuário e configura a senha
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Criptografa a senha
        if commit:
            user.save()
        return user

# accounts/forms.py
from django import forms
from .models import Usuario

class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo', 'poster']  # Campos que podem ser atualizados
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(choices=[(True, "Professor"), (False, "Aluno")], attrs={'class': 'form-control'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': "Nome de Usuário",
            'email': "E-mail",
            'first_name': "Primeiro Nome",
            'last_name': "Sobrenome",
            'tipo': "Tipo de Usuário",
            'poster': "Imagem de Perfil",
        }
