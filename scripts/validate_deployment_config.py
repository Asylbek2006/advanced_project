import sys
import subprocess
import json


REQUIRED_ENV_VARIABLES_PER_SERVICE = {
    "auth_service": [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
    ],
    "user_service": [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
    ],
    "product_service": [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
    ],
    "order_service": [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "AUTH_SERVICE_URL",
        "USER_SERVICE_URL",
        "PRODUCT_SERVICE_URL",
    ],
    "chat_service": [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "AUTH_SERVICE_URL",
        "USER_SERVICE_URL",
    ],
}

KNOWN_VALID_DATABASE_HOST = "database"
KNOWN_VALID_SERVICE_URL_PREFIX = "http://"


def read_docker_compose_resolved_config() -> dict:
    result = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Could not read docker compose config: {result.stderr}")
        sys.exit(1)
    return json.loads(result.stdout)


def extract_env_variables_for_service(compose_config: dict, service_name: str) -> dict:
    service_config = compose_config.get("services", {}).get(service_name, {})
    return service_config.get("environment", {})


def validate_database_host_is_not_broken(env_variables: dict, service_name: str) -> list[str]:
    found_errors = []
    database_host_value = env_variables.get("DATABASE_HOST", "")
    if database_host_value and database_host_value != KNOWN_VALID_DATABASE_HOST:
        found_errors.append(
            f"{service_name}: DATABASE_HOST is '{database_host_value}' but expected '{KNOWN_VALID_DATABASE_HOST}'"
        )
    return found_errors


def validate_service_urls_use_http(env_variables: dict, service_name: str) -> list[str]:
    found_errors = []
    url_variable_names = ["AUTH_SERVICE_URL", "USER_SERVICE_URL", "PRODUCT_SERVICE_URL"]
    for url_variable_name in url_variable_names:
        url_value = env_variables.get(url_variable_name, "")
        if url_value and not url_value.startswith(KNOWN_VALID_SERVICE_URL_PREFIX):
            found_errors.append(
                f"{service_name}: {url_variable_name} value '{url_value}' does not start with '{KNOWN_VALID_SERVICE_URL_PREFIX}'"
            )
    return found_errors


def validate_required_variables_are_present(env_variables: dict, service_name: str) -> list[str]:
    found_errors = []
    required_variables = REQUIRED_ENV_VARIABLES_PER_SERVICE.get(service_name, [])
    for required_variable_name in required_variables:
        if required_variable_name not in env_variables or not env_variables[required_variable_name]:
            found_errors.append(
                f"{service_name}: required variable '{required_variable_name}' is missing or empty"
            )
    return found_errors


def validate_all_services(compose_config: dict) -> list[str]:
    all_found_errors = []
    for service_name in REQUIRED_ENV_VARIABLES_PER_SERVICE:
        env_variables = extract_env_variables_for_service(compose_config, service_name)
        all_found_errors.extend(validate_required_variables_are_present(env_variables, service_name))
        all_found_errors.extend(validate_database_host_is_not_broken(env_variables, service_name))
        all_found_errors.extend(validate_service_urls_use_http(env_variables, service_name))
    return all_found_errors


def main() -> None:
    print("=" * 60)
    print("Qadam Retail Platform - Pre-Deployment Configuration Validator")
    print("=" * 60)

    print("\nReading resolved docker compose configuration...")
    compose_config = read_docker_compose_resolved_config()
    print("  Configuration loaded successfully.")

    print("\nValidating environment variables for all services...")
    found_errors = validate_all_services(compose_config)

    if not found_errors:
        print("\nAll checks passed. Configuration is valid.")
        print("You may proceed with: docker compose up -d --build")
        sys.exit(0)
    else:
        print(f"\nFound {len(found_errors)} configuration error(s):")
        for error_message in found_errors:
            print(f"  ERROR: {error_message}")
        print("\nFix the errors above before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
