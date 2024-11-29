#!/usr/bin/env bash
# exit on error
set -o errexit
# Atualizar os repositórios do apt
apt-get update

# Instalar o PortAudio (bibliotecas e headers necessários)
apt-get install -y portaudio19-dev

# Instalar dependências do Python com o Poetry
poetry install

echo "Instalando dependências do Python..."
pip install -r requirements.txt


python manage.py collectstatic --no-input
# adicione linhas abaixo
python manage.py migrate

# create superuser if missing
cat < | python manage.py shell
import os
from django.contrib.auth import get_user_model

User = get_user_model()

User.objects.filter(username=os.environ["DJANGO_SUPERUSER_USERNAME"]).exists() or \
    User.objects.create_superuser(os.environ["DJANGO_SUPERUSER_USERNAME"], os.environ["DJANGO_SUPERUSER_EMAIL"], os.environ["DJANGO_SUPERUSER_PASSWORD"])
EOF