use janus_messages::{Duration, TaskId};
use prio::vdaf::prio3::Prio3Count;
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;
use std::str::FromStr;
use std::time::Instant;
use url::Url;

// Divvi Up task info.
const TASK_ID: &str = "_pZxfsABHN01DThomdMpysEUcIFLlQ09orBvKE_RUDg";
const LEADER_URL: &str = "http://localhost:9001/";
const HELPER_URL: &str = "http://localhost:9002/";
const TIME_PRECISION_SECONDS: u64 = 60;


const MEASUREMENTS_FILE: &str = "../measurements_count.txt";
const RESULTS_FILE: &str = "./results_count.txt";

#[tokio::main]
async fn main() {
    let measurements = read_measurements(MEASUREMENTS_FILE);
    let expected_count = measurements.iter().filter(|value| **value).count();

    println!("Loaded {} measurements", measurements.len());
    println!("Expected count: {}", expected_count);

    let task = TaskId::from_str(TASK_ID).unwrap();
    let leader_url = Url::parse(LEADER_URL).unwrap();
    let helper_url = Url::parse(HELPER_URL).unwrap();
    let vdaf = Prio3Count::new_count(2).unwrap();

    let setup_start = Instant::now();
    let client = janus_client::Client::new(
        task,
        leader_url,
        helper_url,
        Duration::from_seconds(TIME_PRECISION_SECONDS),
        vdaf,
    )
    .await
    .unwrap();
    let setup_seconds = setup_start.elapsed().as_secs_f64();

    let upload_start = Instant::now();
    for measurement in &measurements {
        client.upload(measurement).await.unwrap();
    }
    let upload_seconds = upload_start.elapsed().as_secs_f64();

    println!("Setup time seconds: {:.6}", setup_seconds);
    println!("Upload completion time seconds: {:.6}", upload_seconds);
    println!(
        "Average upload time per report seconds: {:.6}",
        upload_seconds / measurements.len() as f64
    );
    println!("Uploaded reports: {}", measurements.len());

    append_results(measurements.len(), upload_seconds);
}

fn read_measurements(path: &str) -> Vec<bool> {
    let content = fs::read_to_string(path).unwrap();
    let mut measurements = Vec::new();

    for line in content.lines() {
        let value_part = line.split(':').nth(1).unwrap_or(line).trim();
        for value in value_part.split(',') {
            let value = value.trim().to_lowercase();
            if !value.is_empty() {
                measurements.push(parse_bool_measurement(&value));
            }
        }
    }

    measurements
}

fn parse_bool_measurement(value: &str) -> bool {
    match value {
        "1" | "true" | "yes" => true,
        "0" | "false" | "no" => false,
        _ => panic!("invalid boolean measurement: {value}; use 0/1 or true/false"),
    }
}

fn append_results(reports: usize, upload_seconds: f64) {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(RESULTS_FILE)
        .unwrap();

    writeln!(file, "{} {:.6}", reports, upload_seconds).unwrap();
}
