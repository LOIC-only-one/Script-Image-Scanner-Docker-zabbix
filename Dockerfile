FROM alpine:3.19

# Installation des dépendances
RUN apk add --no-cache \
    python3 \
    py3-pip \
    docker-cli \
    zabbix-utils \
    bash \
    curl

# Installation de Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Création du répertoire de travail
WORKDIR /scanner

# Copie des scripts
COPY scanner.py /scanner/
COPY scan_loop.sh /scanner/

RUN chmod +x /scanner/scan_loop.sh

# Lancement du scanner en boucle
CMD ["/scanner/scan_loop.sh"]
