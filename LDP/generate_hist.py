import random
import numpy as np

NB_CLIENTS = int(input("nb_clients"))
NB_BUCKETS = 24
MAX_BUCKETS_PER_CLIENT = 1
MEASUREMENTS_FILE = "measurements_hist.txt"


def generate_measurement_file(path, n_reports, nb_buckets):
    true_probs = np.exp(-((np.arange(nb_buckets) - 19)**2) / 10) + np.exp(-((np.arange(nb_buckets) - 8)**2) / 2)
    true_probs /= true_probs.sum()
    true_data = np.random.choice(nb_buckets, size=n_reports, p=true_probs)
    with open(path, "w") as fout:
        for client_id in range(1, n_reports + 1):
            fout.write(f"client_{client_id}: {true_data[client_id-1]}\n")

generate_measurement_file(MEASUREMENTS_FILE, NB_CLIENTS, NB_BUCKETS)
