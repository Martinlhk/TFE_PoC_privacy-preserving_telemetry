import ast, os, time
import re
import subprocess
from urllib.parse import quote
from urllib.request import Request, urlopen


USAGE_TIME_TASK_ID = "8Vp2PCTxWWON9HpfrK_p78ekfL1lBQIkEoP-yjxsR6Q"
BRACELET_SYNC_TASK_ID = "aNBSTYx9AV-wxgIqldGarAK6noonkOIV8UimovxmvhE"
COLLECTOR_CREDENTIAL_FILE = "./collector-credential-102.json"
PUSHGATEWAY_URL = "http://localhost:9091"


def collect_current_batch(task_id, metric_name):
    result = subprocess.run(
        [
            "./divviup",
            "dap-client",
            "collect",
            "--task-id",
            task_id,
            "--collector-credential-file",
            COLLECTOR_CREDENTIAL_FILE,
            "--current-batch"
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    
    print(result)
    if result.returncode != 0:
        print(f"Divvi Up collect failed for {metric_name}. Skipping this metric.")
        if result.stdout:
            print("stdout:")
            print(result.stdout)
        if result.stderr:
            print("stderr:")
            print(result.stderr)
        return None

    return result.stdout


def parse_collect_output(output):
    reports_match = re.search(r"Number of reports: (\d+)", output)
    result_match = re.search(r"Aggregation result: (.+)", output)

    if reports_match is None or result_match is None:
        raise ValueError("Cannot parse divviup collect output")

    reports = int(reports_match.group(1))
    aggregate_result = ast.literal_eval(result_match.group(1))

    return reports, aggregate_result


def build_prometheus_metrics(usage_data=None, sync_data=None):
    lines = []

    if usage_data is not None:
        usage_reports, usage_histogram = usage_data
        lines.extend(
            [
                "# TYPE divviup_usage_time_reports_total gauge",
                f"divviup_usage_time_reports_total {usage_reports}",
                "# TYPE divviup_usage_time_bucket gauge",
            ]
        )

        for bucket, value in enumerate(usage_histogram):
            lines.append(f'divviup_usage_time_bucket{{bucket="{bucket:02d}h"}} {value}')

    if sync_data is not None:
        sync_reports, sync_sum = sync_data
        sync_mean = sync_sum / sync_reports
        lines.extend(
            [
                "# TYPE divviup_bracelet_sync_reports_total gauge",
                f"divviup_bracelet_sync_reports_total {sync_reports}",
                "# TYPE divviup_bracelet_sync_sum gauge",
                f"divviup_bracelet_sync_sum {sync_sum}",
                "# TYPE divviup_bracelet_sync_mean gauge",
                f"divviup_bracelet_sync_mean {sync_mean}",
            ]
        )

    return "\n".join(lines) + "\n"


def push_to_prometheus(metrics):
    job_url = quote("divviup_collect", safe="")
    url = f"{PUSHGATEWAY_URL}/metrics/job/{job_url}"

    request = Request(
        url,
        data=metrics.encode("utf-8"),
        method="PUT",
        headers={"Content-Type": "text/plain; version=0.0.4"},
    )

    with urlopen(request) as response:
        return response.status


if __name__ == "__main__":
    os.environ['DIVVIUP_API_URL'] = 'http://localhost:8080'
    os.environ['DIVVIUP_ACCOUNT_ID'] = 'd7e4cef8-684a-4747-884f-5dbe179293e4'
    os.environ['DIVVIUP_TOKEN'] = ''
    usage_data = None
    sync_data = None

    start_time_usage = time.time()
    while (True):
        usage_output = collect_current_batch(USAGE_TIME_TASK_ID, "usage_time")
        if usage_output is not None:
            print(f"Execution time for usage_data : {(time.time() - start_time_usage):.2f} sec")
            usage_data = parse_collect_output(usage_output)
        else: 
            break

    start_time_sync = time.time()
    sync_output = collect_current_batch(BRACELET_SYNC_TASK_ID, "bracelet_sync")
    if sync_output is not None:
        print(f"Execution time for sync_data : {(time.time() - start_time_sync):.2f} sec")
        sync_data = parse_collect_output(sync_output)

    if usage_data is None and sync_data is None:
        print("No metric was collected. Nothing to push to Prometheus.")
        raise SystemExit(1)

    metrics = build_prometheus_metrics(usage_data, sync_data)
    status = push_to_prometheus(metrics)

    if usage_data is not None:
        usage_reports, usage_histogram = usage_data
        print("Usage time reports:", usage_reports)
        print("Usage time histogram:", usage_histogram)

    if sync_data is not None:
        sync_reports, sync_sum = sync_data
        print("Bracelet sync reports:", sync_reports)
        print("Bracelet sync sum:", sync_sum)
        print("Bracelet sync mean:", sync_sum / sync_reports)

    print("Pushgateway status:", status)
