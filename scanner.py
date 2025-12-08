#!/usr/bin/env python3
"""
Scanner de vulnerabilites pour microservices Docker
Utilise Trivy pour scanner les images et envoie les resultats a Zabbix
"""

import subprocess
import json
import sys
import os
from datetime import datetime

# Configuration
ZABBIX_SERVER = os.environ.get('ZABBIX_SERVER', '172.23.0.20')
ZABBIX_PORT = os.environ.get('ZABBIX_PORT', '10051')
SCANNER_HOSTNAME = os.environ.get('SCANNER_HOSTNAME', 'vulnerability-scanner')

def get_running_containers():
    """Recupere la liste des conteneurs en cours d'execution"""
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}:{{.Image}}'], capture_output=True, text=True, check=True)
    containers = []
    for line in result.stdout.strip().split('\n'):
        if line and ':' in line:
            name, image = line.split(':', 1)
            if name != 'vulnerability-scanner':
                containers.append({'name': name, 'image': image})
    return containers

def scan_image(image):
    """Scan une image Docker avec Trivy et retourne les vulnerabilites"""
    result = subprocess.run(['trivy', 'image', '--format', 'json', '--quiet', image],capture_output=True, text=True, timeout=300)
    return json.loads(result.stdout) if result.returncode == 0 else None

def count_vulnerabilities(scan_results):
    """Compte les vulnerabilites par severite"""
    compteurs = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0, 'TOTAL': 0}
    
    if not scan_results or 'Results' not in scan_results:
        return compteurs
    
    for resultat in scan_results.get('Results', []):
        for vulnerabilite in resultat.get('Vulnerabilities', []):
            severite = vulnerabilite.get('Severity', 'UNKNOWN')
            compteurs[severite] = compteurs.get(severite, 0) + 1
            compteurs['TOTAL'] += 1
    
    return compteurs

def send_to_zabbix(hostname, key, value):
    """Envoie une metrique a Zabbix via zabbix_sender"""
    cmd = ['zabbix_sender', '-z', ZABBIX_SERVER, '-p', ZABBIX_PORT, '-s', hostname, '-k', key, '-o', str(value)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return result.returncode == 0

def main():
    """Fonction principale"""
    print(f"[{datetime.now()}] Demarrage du scan de vulnerabilites...")
    
    conteneurs = get_running_containers()
    print(f"Conteneurs trouves: {len(conteneurs)}")
    
    total_vulnerabilites = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0, 'TOTAL': 0}
    
    images_scannees = set()
    for conteneur in conteneurs:
        image = conteneur['image']
        nom = conteneur['name']
        if image in images_scannees:
            continue
        
        print(f"Scan de {nom} ({image})...")
        images_scannees.add(image)
        
        resultats_scan = scan_image(image)
        if resultats_scan:
            compteurs = count_vulnerabilities(resultats_scan)
            for severite in total_vulnerabilites:
                total_vulnerabilites[severite] += compteurs[severite]
            
            print(f"  -> CRITICAL={compteurs['CRITICAL']}, HIGH={compteurs['HIGH']}, "f"MEDIUM={compteurs['MEDIUM']}, LOW={compteurs['LOW']}, TOTAL={compteurs['TOTAL']}")
    
    print(f"\n[{datetime.now()}] Envoi des resultats a Zabbix...")
    
    metriques = {
        'vuln.critical': total_vulnerabilites['CRITICAL'],
        'vuln.high': total_vulnerabilites['HIGH'],
        'vuln.medium': total_vulnerabilites['MEDIUM'],
        'vuln.low': total_vulnerabilites['LOW'],
        'vuln.total': total_vulnerabilites['TOTAL'],
        'vuln.containers.scanned': len(images_scannees)
    }
    
    for cle, valeur in metriques.items():
        send_to_zabbix(SCANNER_HOSTNAME, cle, valeur)
    
    print(f"\n[{datetime.now()}] Scan termine!")
    print(f"Total: {total_vulnerabilites['TOTAL']} (CRITICAL: {total_vulnerabilites['CRITICAL']}, "
          f"HIGH: {total_vulnerabilites['HIGH']}, MEDIUM: {total_vulnerabilites['MEDIUM']}, "
          f"LOW: {total_vulnerabilites['LOW']})")

if __name__ == '__main__':
    main()
