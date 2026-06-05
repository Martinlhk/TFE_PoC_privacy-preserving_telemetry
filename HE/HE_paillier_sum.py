import argparse
import json
import time

from phe import paillier


DEFAULT_MEASUREMENTS_FILE = "sum_measurements.txt"


def read_measurement_file(path):
    measurements = []

    with open(path, "r") as fin:
        for line in fin:
            _, value = line.strip().split(":")
            measurements.append(int(value.strip()))

    return measurements


def fixed_ciphertext_size_bytes(public_key):
    # A Paillier ciphertext is an integer modulo n^2.
    return 2 * ((public_key.n.bit_length() + 7) // 8)


def paillier_serialized_ciphertext(encrypted_number):
    return {
        "ciphertext": str(encrypted_number.ciphertext()),
        "exponent": encrypted_number.exponent,
    }


def serialized_ciphertext_size_bytes(encrypted_number):
    payload = paillier_serialized_ciphertext(encrypted_number)
    return len(json.dumps(payload, separators=(",", ":")).encode("utf-8"))


def print_metric(name, value):
    print(f"{name}: {value}")


parser = argparse.ArgumentParser()
parser.add_argument("--file", default=str(DEFAULT_MEASUREMENTS_FILE))
parser.add_argument("--key-bits", type=int, default=3072)
args = parser.parse_args()

measurements = read_measurement_file(args.file)
if not measurements:
    raise ValueError("measurement file is empty")

public_key, private_key = paillier.generate_paillier_keypair(n_length=args.key_bits)

# Client side encryption
start = time.perf_counter()
encrypted_reports = [public_key.encrypt(value) for value in measurements]
encryption_duration = time.perf_counter() - start

raw_report_size = fixed_ciphertext_size_bytes(public_key)

start = time.perf_counter()
serialized_report_sizes = [
    serialized_ciphertext_size_bytes(value) for value in encrypted_reports
]
serialization_duration = time.perf_counter() - start

# Aggregation
start = time.perf_counter()
encrypted_sum = sum(encrypted_reports)
aggregation_duration = time.perf_counter() - start

# Collector decryption
start = time.perf_counter()
result = private_key.decrypt(encrypted_sum)
decryption_duration = time.perf_counter() - start

print_metric("scheme", "paillier")
print_metric("operation", "sum")
print_metric("key_bits", public_key.n.bit_length())
print_metric("nb_reports", len(measurements))
print_metric(
    "client_report_build_seconds_total",
    f"{encryption_duration + serialization_duration:.6f}",
)
print_metric(
    "client_report_build_seconds_per_report",
    f"{(encryption_duration + serialization_duration) / len(measurements):.9f}",
)
print_metric("raw_ciphertext_bytes_per_report", raw_report_size)
print_metric(
    "raw_ciphertext_bytes_total",
    raw_report_size * len(encrypted_reports),
)
print_metric(
    "serialized_report_bytes_per_report_avg",
    f"{sum(serialized_report_sizes) / len(measurements):.2f}",
)
print_metric(
    "serialized_report_bytes_per_report_max",
    max(serialized_report_sizes),
)

with open("results_eval_HE_sum.csv", "a") as out:
    # nb_reports,client_report_build_seconds/report,serialized_report_bytes/report,raw_ciphertext_bytes_report,key_size
    out.write(
        f"{len(measurements)},"
        f"{(encryption_duration + serialization_duration) / len(measurements):.6f},"
        f"{max(serialized_report_sizes)},{raw_report_size},{args.key_bits}\n"
    )
