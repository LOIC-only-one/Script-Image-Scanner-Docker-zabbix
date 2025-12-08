# Configuration Zabbix pour le Scanner de Vulnérabilités

## Vue d'ensemble

Le scanner de vulnérabilités analyse automatiquement tous les conteneurs Docker de votre infrastructure et envoie les résultats à Zabbix. Il utilise Trivy pour détecter les vulnérabilités dans les images Docker.

## Fonctionnement

- **Scan automatique** : Le scanner s'exécute toutes les heures (configurable via `SCAN_INTERVAL`)
- **Analyse Trivy** : Scan de sécurité des images Docker
- **Envoi à Zabbix** : Les métriques sont envoyées via `zabbix_sender`

## Métriques envoyées à Zabbix

Le scanner envoie les métriques suivantes avec le hostname `vulnerability-scanner` :

| Clé Zabbix | Description |
|------------|-------------|
| `vuln.critical` | Nombre de vulnérabilités critiques |
| `vuln.high` | Nombre de vulnérabilités de haute sévérité |
| `vuln.medium` | Nombre de vulnérabilités de moyenne sévérité |
| `vuln.low` | Nombre de vulnérabilités de faible sévérité |
| `vuln.total` | Nombre total de vulnérabilités |
| `vuln.containers.scanned` | Nombre de conteneurs scannés |

## Configuration dans Zabbix (à faire manuellement)

### 1. Créer l'hôte dans Zabbix

1. Allez dans **Configuration** → **Hôtes** → **Créer un hôte**
2. Configurez :
   - **Nom d'hôte** : `vulnerability-scanner`
   - **Nom visible** : `Scanner de Vulnérabilités`
   - **Groupes** : Créez ou sélectionnez `Security/Scanners`
   - **Interfaces** : Aucune interface n'est nécessaire (trapper uniquement)

### 2. Créer le template (optionnel mais recommandé)

1. Allez dans **Configuration** → **Templates** → **Créer un template**
2. Nom : `Template Vulnerability Scanner`
3. Groupes : `Templates/Security`

### 3. Créer les items (données)

Pour chaque métrique, créez un item de type **Zabbix trapper** :

#### Item 1 : Vulnérabilités Critiques
- **Nom** : `Vulnérabilités CRITICAL`
- **Type** : `Zabbix trapper`
- **Clé** : `vuln.critical`
- **Type d'information** : `Entier non signé`
- **Unités** : (vide)
- **Applications/Tags** : `Security`, `Vulnerabilities`

#### Item 2 : Vulnérabilités HIGH
- **Nom** : `Vulnérabilités HIGH`
- **Type** : `Zabbix trapper`
- **Clé** : `vuln.high`FROM alpine:3.19

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

- **Type d'information** : `Entier non signé`
- **Unités** : (vide)
- **Applications/Tags** : `Security`, `Vulnerabilities`

#### Item 3 : Vulnérabilités MEDIUM
- **Nom** : `Vulnérabilités MEDIUM`
- **Type** : `Zabbix trapper`
- **Clé** : `vuln.medium`
- **Type d'information** : `Entier non signé`
- **Unités** : (vide)
- **Applications/Tags** : `Security`, `Vulnerabilities`

#### Item 4 : Vulnérabilités LOW
- **Nom** : `Vulnérabilités LOW`
- **Type** : `Zabbix trapper`
- **Clé** : `vuln.low`
- **Type d'information** : `Entier non signé`
- **Unités** : (vide)
- **Applications/Tags** : `Security`, `Vulnerabilities`

#### Item 5 : Total des vulnérabilités
- **Nom** : `Total des vulnérabilités`
- **Type** : `Zabbix trapper`
- **Clé** : `vuln.total`
- **Type d'information** : `Entier non signé`
- **Unités** : (vide)
- **Applications/Tags** : `Security`, `Vulnerabilities`

#### Item 6 : Conteneurs scannés
- **Nom** : `Nombre de conteneurs scannés`
- **Type** : `Zabbix trapper`
- **Clé** : `vuln.containers.scanned`
- **Type d'information** : `Entier non signé`
- **Unités** : (vide)
- **Applications/Tags** : `Security`, `Monitoring`

### 4. Créer des triggers (alertes)

#### Trigger 1 : Vulnérabilités critiques détectées
- **Nom** : `Vulnérabilités CRITICAL détectées sur {HOST.NAME}`
- **Sévérité** : `Majeur` ou `Critique`
- **Expression** : 
  ```
  last(/vulnerability-scanner/vuln.critical)>0
  ```
- **Description** : `{ITEM.LASTVALUE} vulnérabilités critiques ont été détectées`

#### Trigger 2 : Vulnérabilités HIGH détectées
- **Nom** : `Vulnérabilités HIGH détectées sur {HOST.NAME}`
- **Sévérité** : `Moyen`
- **Expression** : 
  ```
  last(/vulnerability-scanner/vuln.high)>5
  ```
- **Description** : `{ITEM.LASTVALUE} vulnérabilités de haute sévérité détectées`

#### Trigger 3 : Nombre élevé de vulnérabilités totales
- **Nom** : `Nombre élevé de vulnérabilités ({ITEM.LASTVALUE})`
- **Sévérité** : `Avertissement`
- **Expression** : 
  ```
  last(/vulnerability-scanner/vuln.total)>50
  ```
- **Description** : `Plus de 50 vulnérabilités au total détectées`

### 5. Créer des graphiques (optionnel)

#### Graphique 1 : Évolution des vulnérabilités par sévérité
- **Nom** : `Vulnérabilités par sévérité`
- **Type** : `Normal`
- **Items** :
  - `vuln.critical` (Rouge)
  - `vuln.high` (Orange)
  - `vuln.medium` (Jaune)
  - `vuln.low` (Vert)

#### Graphique 2 : Total des vulnérabilités
- **Nom** : `Total des vulnérabilités`
- **Type** : `Normal`
- **Items** :
  - `vuln.total`

## Démarrage du scanner

```bash
cd <dir>

# Construire et démarrer le scanner
docker compose -f docker-compose.services.yaml up -d vulnerability-scanner

# Voir les logs
docker logs -f vulnerability-scanner
```

## Variables d'environnement

Vous pouvez personnaliser le scanner dans `docker-compose.services.yaml` :

- `ZABBIX_SERVER` : Adresse du serveur Zabbix (défaut: 172.23.0.20)
- `ZABBIX_PORT` : Port du serveur Zabbix (défaut: 10051)
- `SCANNER_HOSTNAME` : Nom d'hôte pour Zabbix (défaut: vulnerability-scanner)
- `SCAN_INTERVAL` : Intervalle entre les scans en secondes (défaut: 3600 = 1 heure)

## Tests

Pour forcer un scan immédiat :

```bash
docker exec vulnerability-scanner python3 /scanner/scanner.py
```

## Vérification dans Zabbix

1. Allez dans **Surveillance** → **Dernières données**
2. Filtrez par hôte : `vulnerability-scanner`
3. Vous devriez voir les 6 métriques avec leurs valeurs actuelles

## Dépannage

### Le scanner ne trouve pas les conteneurs
Vérifiez que le socket Docker est bien monté :
```bash
docker inspect vulnerability-scanner | grep docker.sock
```

### Pas de données dans Zabbix
1. Vérifiez les logs du scanner :
   ```bash
   docker logs vulnerability-scanner
   ```

2. Vérifiez que le serveur Zabbix est accessible :
   ```bash
   docker exec vulnerability-scanner nc -zv 172.23.0.20 10051
   ```

3. Testez manuellement zabbix_sender :
   ```bash
   docker exec vulnerability-scanner zabbix_sender -z 172.23.0.20 -p 10051 -s vulnerability-scanner -k vuln.test -o 123
   ```

### Trivy prend trop de temps
Les premiers scans peuvent être longs car Trivy télécharge sa base de données de vulnérabilités. Les scans suivants seront plus rapides.
