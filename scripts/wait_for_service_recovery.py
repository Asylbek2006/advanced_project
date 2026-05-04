import sys
import time
import urllib.request
import urllib.error


GATEWAY_BASE_URL = "http://localhost"
MAXIMUM_WAIT_SECONDS = 120
POLL_INTERVAL_SECONDS = 5

SERVICE_HEALTH_ENDPOINTS = {
    "auth_service": f"{GATEWAY_BASE_URL}/api/auth/health",
    "user_service": f"{GATEWAY_BASE_URL}/api/users/health",
    "product_service": f"{GATEWAY_BASE_URL}/api/products/health",
    "order_service": f"{GATEWAY_BASE_URL}/api/orders/health",
    "chat_service": f"{GATEWAY_BASE_URL}/api/messages/health",
}


def check_single_service_health(service_name: str, health_endpoint_url: str) -> bool:
    try:
        with urllib.request.urlopen(health_endpoint_url, timeout=5) as response_stream:
            return response_stream.status == 200
    except Exception:
        return False


def check_all_services_health() -> dict[str, bool]:
    return {
        service_name: check_single_service_health(service_name, health_endpoint_url)
        for service_name, health_endpoint_url in SERVICE_HEALTH_ENDPOINTS.items()
    }


def wait_for_all_services_to_recover() -> bool:
    print("=" * 60)
    print("Qadam Retail Platform - Service Recovery Monitor")
    print("=" * 60)
    print(f"\nWaiting up to {MAXIMUM_WAIT_SECONDS} seconds for all services to become healthy...")

    elapsed_seconds = 0
    while elapsed_seconds < MAXIMUM_WAIT_SECONDS:
        health_results = check_all_services_health()

        healthy_service_names = [name for name, is_healthy in health_results.items() if is_healthy]
        unhealthy_service_names = [name for name, is_healthy in health_results.items() if not is_healthy]

        print(f"\n[{elapsed_seconds}s] Status:")
        for service_name, is_healthy in health_results.items():
            status_label = "UP" if is_healthy else "DOWN"
            print(f"  {service_name:<20} {status_label}")

        if not unhealthy_service_names:
            print(f"\nAll {len(healthy_service_names)} services are healthy. Recovery complete.")
            return True

        print(f"\n  Still waiting for: {', '.join(unhealthy_service_names)}")
        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed_seconds += POLL_INTERVAL_SECONDS

    print(f"\nTimeout after {MAXIMUM_WAIT_SECONDS} seconds. Some services did not recover.")
    return False


def main() -> None:
    all_recovered = wait_for_all_services_to_recover()
    sys.exit(0 if all_recovered else 1)


if __name__ == "__main__":
    main()
