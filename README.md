# Privacy-Preserving Telemetry PoC

Ce dépôt contient le code expérimental associé au travail de fin d'études sur la télémétrie respectueuse de la confidentialité. Les explications détaillées, le modèle d'attaquant, la méthodologie et l'analyse des résultats sont documentés dans le rapport du TFE.

## Contenu

- `DAP_Divvi_up/` : déploiement local Divvi Up / DAP, génération de mesures et collecte des agrégats.
- `Mobile_app_android_DAP/` : application Android de simulation d'un client mobile.
- `Visualisation/` : stack Prometheus, Pushgateway et Grafana pour visualiser les résultats collectés.
- `LDP/` : expérimentations de confidentialité différentielle locale.
- `HE/` : expérimentations de chiffrement homomorphe.

## Démarrage rapide du pipeline DAP/Prio3

Lancer l'environnement Divvi Up :

```bash
cd DAP_Divvi_up
docker compose up
```

Lancer la visualisation :

```bash
cd Visualisation
docker compose up
```

Interfaces locales :

- Divvi Up API : `http://localhost:8080`
- Divvi Up console : `http://localhost:8081`
- Prometheus : `http://localhost:9090`
- Pushgateway : `http://localhost:9091`
- Grafana : `http://localhost:3000`

## Remarque

Ce dépôt est un PoC. Il n'est pas destiné à un déploiement en production.
Tous les crédentials présents dans ce dépôt sont présents à titre d'exemple et ne sont pas utilisés en production. 