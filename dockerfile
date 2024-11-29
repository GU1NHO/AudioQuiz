# Use a imagem oficial do Python como base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copie o arquivo requirements.txt para o container
COPY requirements.txt .

# Instale as dependências do sistema necessárias (como libportaudio, etc.)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para dentro do container
COPY . .

# Configuração de variáveis de ambiente para o superuser
ENV DJANGO_SUPERUSER_USERNAME=admin \
    DJANGO_SUPERUSER_PASSWORD=adminpassword \
    DJANGO_SUPERUSER_EMAIL=admin@example.com

# Rodar os comandos para preparar o banco de dados
RUN python manage.py collectstatic --no-input
RUN python manage.py makemigrations
RUN python manage.py migrate

# Criar o superusuário se ele não existir
RUN python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username=os.environ["DJANGO_SUPERUSER_USERNAME"]).exists() or \
    User.objects.create_superuser(os.environ["DJANGO_SUPERUSER_USERNAME"], os.environ["DJANGO_SUPERUSER_EMAIL"], os.environ["DJANGO_SUPERUSER_PASSWORD"])
EOF

# Exponha a porta que o Django estará escutando
EXPOSE 8000

# Comando para rodar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
