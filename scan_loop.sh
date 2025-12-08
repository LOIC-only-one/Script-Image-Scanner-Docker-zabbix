#!/bin/bash

# Boucle de scan toutes les heures
SCAN_INTERVAL=${SCAN_INTERVAL:-3600}

echo "Scanner de vulnérabilités démarré"
echo "Intervalle de scan: ${SCAN_INTERVAL} secondes"
echo "Serveur Zabbix: ${ZABBIX_SERVER:-172.23.0.20}"
echo ""

while true; do
    python3 /scanner/scanner.py
    echo ""
    echo "Prochain scan dans ${SCAN_INTERVAL} secondes..."
    sleep ${SCAN_INTERVAL}
done
