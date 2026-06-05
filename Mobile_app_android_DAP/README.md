# Application Android de télémétrie DAP

Cette application Android simule un client mobile envoyant des mesures de
télémétrie aux agrégateurs DAP de Divvi Up. Elle permet d'envoyer :

- un nombre de synchronisations de bracelet avec une tâche Prio3 Sum ;
- une ou plusieurs heures d'utilisation avec une tâche Prio3 Histogram.

L'application affiche également le temps total d'envoi et le temps moyen par
rapport.

## Prérequis

- Android Studio avec un émulateur Android ;
- l'infrastructure locale Divvi Up démarrée ;
- deux tâches Divvi Up compatibles avec les paramètres Prio3 de l'application.

## Configuration

Les adresses des agrégateurs et les ID des tâches sont définis dans
[`TelemetryTaskConfig.kt`](app/src/main/java/com/example/daptelemetry/TelemetryTaskConfig.kt).

Les adresses `http://10.0.2.2:9001/` et `http://10.0.2.2:9002/` permettent à
l'émulateur Android d'accéder aux agrégateurs lancés sur la machine hôte.

## Installation

Depuis la racine du dépôt, installer la version de débogage sur l'émulateur
Android actif :

```sh
cd Mobile_app_android_DAP
./gradlew installDebug
```

L'application peut ensuite être ouverte depuis l'émulateur.

## Compilation

Pour générer l'APK :

```sh
./gradlew assembleDebug
```