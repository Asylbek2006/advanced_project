import sys
import time
import threading
import statistics
import urllib.request
import urllib.error
import json


GATEWAY_BASE_URL = "http://localhost"
NUMBER_OF_CONCURRENT_THREADS = 10
NUMBER_OF_REQUESTS_PER_THREAD = 20
DELAY_BETWEEN_REQUESTS_SECONDS = 0.1


def fetch_auth_token(username: str, password: str) -> str:
    login_payload = json.dumps({"username": username, "password": password}).encode()
    login_request = urllib.request.Request(
        f"{GATEWAY_BASE_URL}/api/auth/login",
        data=login_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(login_request, timeout=10) as response_stream:
        response_body = json.loads(response_stream.read())
    return response_body["access_token"]


def send_single_request(target_url: str, bearer_token: str) -> tuple[int, float]:
    start_time = time.monotonic()
    try:
        http_request = urllib.request.Request(
            target_url,
            headers={"Authorization": f"Bearer {bearer_token}"}
        )
        with urllib.request.urlopen(http_request, timeout=10) as response_stream:
            response_stream.read()
        elapsed_seconds = time.monotonic() - start_time
        return 200, elapsed_seconds
    except urllib.error.HTTPError as http_error:
        elapsed_seconds = time.monotonic() - start_time
        return http_error.code, elapsed_seconds
    except Exception:
        elapsed_seconds = time.monotonic() - start_time
        return 0, elapsed_seconds


def run_load_for_single_thread(
    target_url: str,
    bearer_token: str,
    number_of_requests: int,
    delay_seconds: float,
    collected_results: list
) -> None:
    for _ in range(number_of_requests):
        status_code, elapsed_seconds = send_single_request(target_url, bearer_token)
        collected_results.append((status_code, elapsed_seconds))
        time.sleep(delay_seconds)


def run_load_test_for_endpoint(endpoint_path: str, bearer_token: str) -> dict:
    target_url = f"{GATEWAY_BASE_URL}{endpoint_path}"
    print(f"\nTesting endpoint: {target_url}")
    print(f"  Threads: {NUMBER_OF_CONCURRENT_THREADS}, Requests per thread: {NUMBER_OF_REQUESTS_PER_THREAD}")

    collected_results = []
    active_threads = []

    test_start_time = time.monotonic()

    for _ in range(NUMBER_OF_CONCURRENT_THREADS):
        thread = threading.Thread(
            target=run_load_for_single_thread,
            args=(target_url, bearer_token, NUMBER_OF_REQUESTS_PER_THREAD, DELAY_BETWEEN_REQUESTS_SECONDS, collected_results)
        )
        active_threads.append(thread)
        thread.start()

    for active_thread in active_threads:
        active_thread.join()

    total_elapsed_seconds = time.monotonic() - test_start_time

    successful_responses = [elapsed for status, elapsed in collected_results if status == 200]
    failed_responses = [status for status, elapsed in collected_results if status != 200]
    all_elapsed_times = [elapsed for status, elapsed in collected_results]

    total_requests = len(collected_results)
    requests_per_second = total_requests / total_elapsed_seconds if total_elapsed_seconds > 0 else 0

    result_summary = {
        "endpoint": endpoint_path,
        "total_requests": total_requests,
        "successful_requests": len(successful_responses),
        "failed_requests": len(failed_responses),
        "requests_per_second": round(requests_per_second, 2),
        "average_response_seconds": round(statistics.mean(all_elapsed_times), 3) if all_elapsed_times else 0,
        "p95_response_seconds": round(sorted(all_elapsed_times)[int(len(all_elapsed_times) * 0.95)], 3) if all_elapsed_times else 0,
        "max_response_seconds": round(max(all_elapsed_times), 3) if all_elapsed_times else 0,
    }

    print(f"  Total requests:      {result_summary['total_requests']}")
    print(f"  Successful:          {result_summary['successful_requests']}")
    print(f"  Failed:              {result_summary['failed_requests']}")
    print(f"  Requests per second: {result_summary['requests_per_second']}")
    print(f"  Avg response time:   {result_summary['average_response_seconds']}s")
    print(f"  p95 response time:   {result_summary['p95_response_seconds']}s")
    print(f"  Max response time:   {result_summary['max_response_seconds']}s")

    return result_summary


def main() -> None:
    print("=" * 60)
    print("Qadam Retail Platform - Load Simulation for Capacity Planning")
    print("=" * 60)

    print("\nStep 1: Authenticating with auth service...")
    try:
        bearer_token = fetch_auth_token("asylbek", "asylbek123")
        print(f"  Authentication successful. Token: {bearer_token[:20]}...")
    except Exception as auth_error:
        print(f"  Authentication failed: {auth_error}")
        print("  Make sure the platform is running: docker compose up -d")
        sys.exit(1)

    endpoints_to_test = [
        "/api/products",
        "/api/orders",
        "/api/users",
        "/api/messages",
    ]

    all_results = []
    for endpoint_path in endpoints_to_test:
        endpoint_result = run_load_test_for_endpoint(endpoint_path, bearer_token)
        all_results.append(endpoint_result)
        time.sleep(1)

    print("\n" + "=" * 60)
    print("CAPACITY PLANNING SUMMARY")
    print("=" * 60)
    print(f"{'Endpoint':<20} {'RPS':>8} {'Avg(s)':>8} {'p95(s)':>8} {'Errors':>8}")
    print("-" * 60)
    for result in all_results:
        print(
            f"{result['endpoint']:<20}"
            f"{result['requests_per_second']:>8}"
            f"{result['average_response_seconds']:>8}"
            f"{result['p95_response_seconds']:>8}"
            f"{result['failed_requests']:>8}"
        )

    print("\nObservations:")
    for result in all_results:
        if result["p95_response_seconds"] > 1.0:
            print(f"  WARNING: {result['endpoint']} p95 latency {result['p95_response_seconds']}s exceeds 1 second threshold")
        if result["failed_requests"] > 0:
            print(f"  ERROR: {result['endpoint']} had {result['failed_requests']} failed requests")

    print("\nLoad simulation complete.")


if __name__ == "__main__":
    main()
