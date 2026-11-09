# version de python
FROM python:3.12-slim

# S'assurer que le système est à jour
RUN apt-get update -y && apt-get install -y --no-install-recommends \
        build-essential default-libmysqlclient-dev pkg-config \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir les variables d'environnement pour configurer Python
ENV PYTHONUNBUFFERED 1  
ENV PYTHONDONTWRITEBYTECODE 1 
ENV APP_HOME /bendingiron
ENV XDG_RUNTIME_DIR /tmp/runtime-root  

# Créer le répertoire d'exécution et définir les permissions
RUN mkdir -p /tmp/runtime-root
RUN chmod -R 0700 /tmp/runtime-root 

# Créer le répertoire de l'application
RUN mkdir -p $APP_HOME
# Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR $APP_HOME

# Installer les dépendances Python à partir du fichier requirements.txt
COPY requirements.txt $APP_HOME  
RUN python -m pip install --upgrade pip  
RUN pip install -r requirements.txt  

# Copier le code de l'application dans le répertoire de travail
COPY . $APP_HOME

# L'application ne tourne pas en root dans le conteneur
RUN useradd --create-home appuser && chown -R appuser $APP_HOME /tmp/runtime-root
USER appuser