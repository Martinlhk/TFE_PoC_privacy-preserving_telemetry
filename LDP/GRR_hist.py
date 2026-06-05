import numpy as np
import matplotlib.pyplot as plt


MEASUREMENTS_FILE = "measurements_hist.txt"

def read_measurement_file(path):
    measurements = []

    with open(path, "r") as fin:
        for line in fin:
            _, values = line.strip().split(":")

            for value in values.split(","):
                measurements.append(int(value.strip()))

    return measurements


true_data = read_measurement_file(MEASUREMENTS_FILE)
n_reports = len(true_data)  # Total number of mobile app reports

d = 24           # Domain size: 24 hour buckets
epsilon = 3.0    # Privacy budget 

# --- Calculate LDP Probabilities ---
# p: probability of reporting the true hour
p = np.exp(epsilon) / (np.exp(epsilon) + d - 1)
# q: probability of reporting a specific incorrect hour
q = 1 / (np.exp(epsilon) + d - 1)

print(f"Probability of keeping true value (p): {p:.4f}")
print(f"Probability of changing to a specific false value (q): {q:.4f}")



# --- Perturbation (Happens locally on the user's phone) ---
perturbed_data = np.zeros(n_reports, dtype=int)
for i in range(n_reports):
    true_val = true_data[i]
    if np.random.rand() < p:
        # Keep the true value
        perturbed_data[i] = true_val
    else:
        # Flip to one of the other (d-1) values uniformly
        possible_other_values = [v for v in range(d) if v != true_val]
        perturbed_data[i] = np.random.choice(possible_other_values)
# print(f"perturbed_data: {perturbed_data}")

# --- Aggregation & Estimation (Happens on company's server) ---
# 1. Count the raw frequencies of the perturbed data received by the server
perturbed_counts = np.bincount(perturbed_data, minlength=d)
perturbed_freqs = perturbed_counts / n_reports

# 2. Apply the unbiased estimator correction formula
estimated_freqs = (perturbed_freqs - q) / (p - q)
estimated_counts = estimated_freqs * n_reports

# Calculate true frequencies strictly for accuracy comparison
true_counts = np.bincount(true_data, minlength=d)
true_freqs = true_counts / n_reports


# errors of estimation
estimation_error_sum = np.sum(np.abs(true_freqs - estimated_freqs))
print(f"estimation error sum: {estimation_error_sum:.5f}")

perturbed_freqs_diff = np.sum(np.abs(true_freqs - perturbed_freqs))

with open(f"results_{n_reports}_{epsilon}_8_19.txt", "a")as out:
    out.write(f"{n_reports} {epsilon} {estimation_error_sum:.5f} {perturbed_freqs_diff:.5f}\n")


# --- Plotting with Matplotlib ---
plt.figure(figsize=(14, 7))

# Set bar widths and positions
width = 0.25
x = np.arange(d)

# Plot the three sets of data side-by-side
plt.bar(x - width, true_freqs, width, label='True Distribution', color='#4C72B0')
plt.bar(x, perturbed_freqs, width, label='Perturbed (Noisy) Reports', color='#C44E52')
plt.bar(x + width, estimated_freqs, width, label='Estimated Distribution', color='#55A868')


plt.xlabel('Hour of the Day (0-23)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title(f'LDP Frequency Estimation (GRR) - $\epsilon={epsilon}$, reports={n_reports}', fontsize=14)
plt.xticks(x)
plt.legend(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)


plt.tight_layout()
plt.savefig(f'./output/ldp_grr_histogram_{n_reports}_{epsilon}_freq_test.png')