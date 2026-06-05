Afin d'utiliser le pipeline DAP, il faut d'abord lancer les containers Docker de Divvi Up avec `docker compose up` dans ce répertoire et configurer Divvi Up en suivant les instructions présentes dans sa [documentation](https://docs.divviup.org/command-line-tutorial/). 

La configuration de Divvi Up fournit les crédentials utilisés par le script `collect_to_prometheus` qui collecte les parts chez le leader et le helper Janus et les envoie à Pushgateway. 

Pour générer des données de test, il faut utiliser le script `generate_measurement.py`. Celui-ci crée des données qui seront utilisées par les scripts côté client présents dans `rust_client`. 

Chaque client doit envoyer ses parts en utilisant une tâche préalablement créée et connue des agrégateurs. Les tâches peuvent être créées avec l'outil CLI de Divvi Up (`./divviup`). Lorsqu'elles sont créées, il faut entrer leur ID dans les scripts Rust client en vérifiant que le type de données envoyées par le code est compatible avec celui de la tâche. 

Les commandes pour lancer les clients DAP sont les suivantes :

```bash
cd rust_client

cargo run --release --bin histogram_client
cargo run --release --bin sum_client
cargo run --release --bin count_client
cargo run --release --bin vdaf_shard_benchmark
```

Le code `vdaf_shard_benchmark` n'envoie pas de rapport à l'infrastructure Divvi Up et sert à évaluer le temps d'encodage et de création des rapports DAP/Prio3. 