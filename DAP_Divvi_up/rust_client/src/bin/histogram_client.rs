use janus_messages::{Duration, TaskId};
use prio::vdaf::prio3::Prio3Histogram;
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;
use std::str::FromStr;
use std::time::Instant;
use url::Url;

// Divvi Up task info.
const TASK_ID: &str = "8Vp2PCTxWWON9HpfrK_p78ekfL1lBQIkEoP-yjxsR6Q";
const LEADER_URL: &str = "http://localhost:9001/";
const HELPER_URL: &str = "http://localhost:9002/";
const TIME_PRECISION_SECONDS: u64 = 60;

// Histogram for app usage hours in a day: buckets 0..23.
const BUCKETS: usize = 24;
const CHUNK_LENGTH: usize = 4;


const MEASUREMENTS_FILE: &str = "../measurements_hist.txt";
const RESULTS_FILE: &str = "./results_hist.txt";

#[tokio::main]
async fn main() {
    let measurements = read_measurements(MEASUREMENTS_FILE);
    println!("Loaded {} measurements", measurements.len());
    println!("Expected histogram: {:?}", histogram(&measurements));

    let task = TaskId::from_str(TASK_ID).unwrap();
    let leader_url = Url::parse(LEADER_URL).unwrap();
    let helper_url = Url::parse(HELPER_URL).unwrap();
    let vdaf = Prio3Histogram::new_histogram(2, BUCKETS, CHUNK_LENGTH).unwrap();

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
        // println!("measurement: {}", measurement);
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

fn read_measurements(path: &str) -> Vec<usize> {
    let content = fs::read_to_string(path).unwrap();
    let mut measurements = Vec::new();

    for line in content.lines() {
        let value_part = line.split(':').nth(1).unwrap_or(line).trim();
        for value in value_part.split(',') {
            let value = value.trim();
            if !value.is_empty() {
                measurements.push(value.parse::<usize>().unwrap());
            }
        }
    }

    measurements
}

fn histogram(measurements: &[usize]) -> Vec<usize> {
    let mut counts = vec![0; BUCKETS];
    for measurement in measurements {
        counts[*measurement] += 1;
    }
    counts
}
fn append_results(reports: usize, upload_seconds: f64) {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(RESULTS_FILE)
        .unwrap();

    writeln!(file, "{} {:.6}", reports, upload_seconds).unwrap();
}
