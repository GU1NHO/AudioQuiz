#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Atualiza a lista de pacotes do sistema e instala as dependências do apt
echo "Instalando dependências do sistema..."
sudo apt-get update
sudo apt-get install -y $(cat apt-packages.txt)

# Instala as dependências Python a partir do requirements.txt
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