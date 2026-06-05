use prio::vdaf::prio3::{Prio3Count, Prio3Histogram, Prio3Sum};
use prio::vdaf::Client;
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;
use std::time::Instant;

const HIST_MEASUREMENTS_FILE: &str = "../measurements_hist.txt";
const SUM_MEASUREMENTS_FILE: &str = "../measurements_sum.txt";
const COUNT_MEASUREMENTS_FILE: &str = "../measurements_count.txt";
const HIST_RESULTS_FILE: &str = "./results_vdaf_shard_hist.txt";
const SUM_RESULTS_FILE: &str = "./results_vdaf_shard_sum.txt";
const COUNT_RESULTS_FILE: &str = "./results_vdaf_shard_count.txt";

const HIST_BUCKETS: usize = 24;
const HIST_CHUNK_LENGTH: usize = 4;
const SUM_BITS: usize = 16;

fn main() {
    let histogram_measurements = read_usize_measurements(HIST_MEASUREMENTS_FILE);
    let sum_measurements = read_u128_measurements(SUM_MEASUREMENTS_FILE);
    let count_measurements = read_bool_measurements(COUNT_MEASUREMENTS_FILE);

    let histogram_seconds = benchmark_histogram_sharding(&histogram_measurements);
    let sum_seconds = benchmark_sum_sharding(&sum_measurements);
    let count_seconds = benchmark_count_sharding(&count_measurements);

    print_result("histogram", histogram_measurements.len(), histogram_seconds);
    print_result("sum", sum_measurements.len(), sum_seconds);
    print_result("count", count_measurements.len(), count_seconds);

    append_result(
        HIST_RESULTS_FILE,
        histogram_measurements.len(),
        histogram_seconds,
    );
    append_result(SUM_RESULTS_FILE, sum_measurements.len(), sum_seconds);
    append_result(COUNT_RESULTS_FILE, count_measurements.len(), count_seconds);
}

fn benchmark_histogram_sharding(measurements: &[usize]) -> f64 {
    let vdaf = Prio3Histogram::new_histogram(2, HIST_BUCKETS, HIST_CHUNK_LENGTH).unwrap();

    let start = Instant::now();
    for (index, measurement) in measurements.iter().enumerate() {
        let nonce = nonce_from_index(index);
        let (_public_share, _input_shares) = vdaf.shard(measurement, &nonce).unwrap();
    }
    start.elapsed().as_secs_f64()
}

fn benchmark_sum_sharding(measurements: &[u128]) -> f64 {
    let vdaf = Prio3Sum::new_sum(2, SUM_BITS).unwrap();

    let start = Instant::now();
    for (index, measurement) in measurements.iter().enumerate() {
        let nonce = nonce_from_index(index);
        let (_public_share, _input_shares) = vdaf.shard(measurement, &nonce).unwrap();
    }
    start.elapsed().as_secs_f64()
}

fn benchmark_count_sharding(measurements: &[bool]) -> f64 {
    let vdaf = Prio3Count::new_count(2).unwrap();

    let start = Instant::now();
    for (index, measurement) in measurements.iter().enumerate() {
        let nonce = nonce_from_index(index);
        let (_public_share, _input_shares) = vdaf.shard(measurement, &nonce).unwrap();
    }
    start.elapsed().as_secs_f64()
}

fn nonce_from_index(index: usize) -> [u8; 16] {
    let mut nonce = [0u8; 16];
    nonce[8..].copy_from_slice(&(index as u64).to_be_bytes());
    nonce
}

fn read_usize_measurements(path: &str) -> Vec<usize> {
    read_measurement_strings(path)
        .iter()
        .map(|value| value.parse::<usize>().unwrap())
        .collect()
}

fn read_u128_measurements(path: &str) -> Vec<u128> {
    read_measurement_strings(path)
        .iter()
        .map(|value| value.parse::<u128>().unwrap())
        .collect()
}

fn read_bool_measurements(path: &str) -> Vec<bool> {
    read_measurement_strings(path)
        .iter()
        .map(|value| parse_bool_measurement(value))
        .collect()
}

fn parse_bool_measurement(value: &str) -> bool {
    match value.trim().to_lowercase().as_str() {
        "1" | "true" | "yes" => true,
        "0" | "false" | "no" => false,
        _ => panic!("invalid boolean measurement: {value}; use 0/1 or true/false"),
    }
}

fn read_measurement_strings(path: &str) -> Vec<String> {
    let content = fs::read_to_string(path).unwrap();
    let mut measurements = Vec::new();

    for line in content.lines() {
        let value_part = line.split(':').nth(1).unwrap_or(line).trim();
        for value in value_part.split(',') {
            let value = value.trim();
            if !value.is_empty() {
                measurements.push(value.to_string());
            }
        }
    }

    measurements
}

fn print_result(metric: &str, reports: usize, seconds: f64) {
    let milliseconds = seconds * 1000.0;
    let average_milliseconds = milliseconds / reports as f64;

    println!("Metric: {metric}");
    println!("Reports: {reports}");
    println!("VDAF sharding/proof time ms: {milliseconds:.3}");
    println!("Average VDAF sharding/proof time per report ms: {average_milliseconds:.6}");
}

fn append_result(path: &str, reports: usize, seconds: f64) {
    let milliseconds = seconds * 1000.0;
    let average_milliseconds = milliseconds / reports as f64;

    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .unwrap();

    writeln!(
        file,
        "{} {:.3} {:.6}",
        reports, milliseconds, average_milliseconds
    )
    .unwrap();
}
