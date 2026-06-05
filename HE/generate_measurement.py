import random

MAX_BRACELET_SYNC = 100
MEASUREMENTS_FILE_SUM = "sum_measurements.txt"


def generate_sum_measurement_file(path, nb_clients):
    with open(path, "w") as fout:
        for client_id in range(1, nb_clients + 1):
            bracelet_sync = random.randint(0, MAX_BRACELET_SYNC)
            fout.write(f"client_{client_id}: {bracelet_sync}\n")


NB_BUCKETS = 24
MAX_BUCKETS_PER_CLIENT = 1
MEASUREMENTS_FILE_HIST = "hist_measurements.txt"


def generate_hist_measurement_file(path, nb_clients, nb_buckets):
    with open(path, "w") as fout:
        for client_id in range(1, nb_clients + 1):
            nb_measurements = random.randint(1, MAX_BUCKETS_PER_CLIENT)
            measurements = random.sample(range(nb_buckets), nb_measurements)
            values = ",".join(str(measurement) for measurement in measurements)

            fout.write(f"client_{client_id}: {values}\n")


generate_sum_measurement_file(MEASUREMENTS_FILE_SUM, int(input("nbClient_sum: ")))

# generate_hist_measurement_file(MEASUREMENTS_FILE_HIST, int(input("nbClient_hist: ")), NB_BUCKETS)
