from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


OUTPUT_PDF_PATH = "/mnt/user-data/outputs/assignment6_report.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 2.5 * cm
RIGHT_MARGIN = 2.5 * cm
TOP_MARGIN = 2.5 * cm
BOTTOM_MARGIN = 2.5 * cm

BASE_STYLES = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "ReportTitle",
    parent=BASE_STYLES["Title"],
    fontSize=22,
    spaceAfter=6,
    textColor=colors.HexColor("#1a1a2e"),
    alignment=TA_CENTER,
)

STYLE_SUBTITLE = ParagraphStyle(
    "ReportSubtitle",
    parent=BASE_STYLES["Normal"],
    fontSize=11,
    spaceAfter=4,
    textColor=colors.HexColor("#4a4a6a"),
    alignment=TA_CENTER,
)

STYLE_HEADING1 = ParagraphStyle(
    "Heading1Custom",
    parent=BASE_STYLES["Heading1"],
    fontSize=15,
    spaceBefore=18,
    spaceAfter=8,
    textColor=colors.HexColor("#1a1a2e"),
    borderPad=4,
)

STYLE_HEADING2 = ParagraphStyle(
    "Heading2Custom",
    parent=BASE_STYLES["Heading2"],
    fontSize=12,
    spaceBefore=12,
    spaceAfter=6,
    textColor=colors.HexColor("#2e4057"),
)

STYLE_BODY = ParagraphStyle(
    "BodyCustom",
    parent=BASE_STYLES["Normal"],
    fontSize=10,
    spaceAfter=6,
    leading=15,
    alignment=TA_JUSTIFY,
)

STYLE_BULLET = ParagraphStyle(
    "BulletCustom",
    parent=BASE_STYLES["Normal"],
    fontSize=10,
    spaceAfter=4,
    leftIndent=16,
    leading=14,
    bulletIndent=4,
)

STYLE_CODE = ParagraphStyle(
    "CodeCustom",
    parent=BASE_STYLES["Code"],
    fontSize=8,
    spaceAfter=8,
    spaceBefore=4,
    leftIndent=12,
    rightIndent=12,
    backColor=colors.HexColor("#f4f4f4"),
    leading=12,
)


def build_cover_page(story):
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("Assignment 6", STYLE_TITLE))
    story.append(Paragraph("Automation and Capacity Planning in a Containerized Microservices System", STYLE_SUBTITLE))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 1 * cm))

    team_data = [
        ["Team Members", "Asylbek Abdibay, Bigali Omarov, Miras Saparov"],
        ["Project", "Qadam Retail Platform"],
        ["Course", "Site Reliability Engineering"],
        ["Builds on", "Assignment 4 (Incident Response) + Assignment 5 (Terraform IaC)"],
    ]
    team_table = Table(team_data, colWidths=[5 * cm, 11 * cm])
    team_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(team_table)
    story.append(PageBreak())


def build_system_context_section(story):
    story.append(Paragraph("1. System Context", STYLE_HEADING1))
    story.append(Paragraph(
        "The Qadam Retail Platform is a containerized microservices system consisting of five "
        "business services, a PostgreSQL database, an Nginx gateway, and a monitoring stack. "
        "This assignment extends Assignment 4 (Incident Response) and Assignment 5 (Terraform IaC) "
        "by adding automation, proactive monitoring, and capacity planning.",
        STYLE_BODY
    ))

    architecture_data = [
        ["Component", "Technology", "Role"],
        ["gateway", "Nginx", "Reverse proxy, routes all traffic"],
        ["auth_service", "FastAPI + PostgreSQL", "Login and token validation"],
        ["user_service", "FastAPI + PostgreSQL", "User profile management"],
        ["product_service", "FastAPI + PostgreSQL", "Product catalog"],
        ["order_service", "FastAPI + PostgreSQL", "Order creation and retrieval"],
        ["chat_service", "FastAPI + PostgreSQL", "Internal messaging"],
        ["prometheus", "Prometheus v2.54", "Metrics collection and alerting"],
        ["grafana", "Grafana v11.1", "Metrics visualization dashboards"],
        ["database", "PostgreSQL 16", "Shared relational database"],
    ]
    arch_table = Table(architecture_data, colWidths=[4.5 * cm, 5 * cm, 6.5 * cm])
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(arch_table)


def build_automation_section(story):
    story.append(Paragraph("2. Automation in SRE", STYLE_HEADING1))
    story.append(Paragraph(
        "Automation reduces the need for manual intervention and improves system reliability "
        "by making deployments, recovery, and validation consistent and repeatable. "
        "Four key automation mechanisms were implemented in this assignment.",
        STYLE_BODY
    ))

    story.append(Paragraph("2.1 Configuration Validation Before Deployment", STYLE_HEADING2))
    story.append(Paragraph(
        "The root cause of the Assignment 4 incident was an incorrect DATABASE_HOST value "
        "in the order_service environment. To prevent this from happening again, a pre-deployment "
        "validation script was written: scripts/validate_deployment_config.py.",
        STYLE_BODY
    ))
    story.append(Paragraph(
        "This script reads the resolved docker compose configuration and checks every service for:",
        STYLE_BODY
    ))
    for check in [
        "All required environment variables are present and non-empty",
        "DATABASE_HOST value equals 'database' (the correct Docker network hostname)",
        "AUTH_SERVICE_URL, USER_SERVICE_URL, PRODUCT_SERVICE_URL start with 'http://'",
    ]:
        story.append(Paragraph(f"• {check}", STYLE_BULLET))

    story.append(Paragraph("Usage:", STYLE_BODY))
    story.append(Preformatted("python3 scripts/validate_deployment_config.py", STYLE_CODE))
    story.append(Paragraph(
        "The script exits with code 0 if everything is valid, or code 1 and a list of errors if "
        "any check fails. This is designed to be run before every deployment.",
        STYLE_BODY
    ))

    story.append(Paragraph("2.2 Automatic Restart Policy", STYLE_HEADING2))
    story.append(Paragraph(
        "Every container in docker-compose.yml now has restart: unless-stopped. "
        "This means Docker will automatically restart any container that crashes or exits "
        "unexpectedly, without requiring human action. The policy does not restart containers "
        "that are manually stopped with docker compose stop or docker compose down.",
        STYLE_BODY
    ))
    story.append(Preformatted(
        "order_service:\n"
        "  restart: unless-stopped",
        STYLE_CODE
    ))

    story.append(Paragraph("2.3 Docker Health Checks", STYLE_HEADING2))
    story.append(Paragraph(
        "Each service now includes a Docker health check that calls the /health endpoint "
        "using curl every 15 seconds. Docker uses this to report whether a container is "
        "healthy or unhealthy, which is visible in docker compose ps and in Prometheus "
        "via the up metric.",
        STYLE_BODY
    ))
    story.append(Preformatted(
        "healthcheck:\n"
        "  test: [\"CMD-SHELL\", \"curl -sf http://localhost:8000/health || exit 1\"]\n"
        "  interval: 15s\n"
        "  timeout: 5s\n"
        "  retries: 5\n"
        "  start_period: 30s",
        STYLE_CODE
    ))
    story.append(Paragraph(
        "The start_period: 30s gives services time to connect to the database and run "
        "startup migrations before health checks begin. This avoids false failure reports "
        "during the initial startup phase.",
        STYLE_BODY
    ))

    story.append(Paragraph("2.4 Enhanced /health Endpoints", STYLE_HEADING2))
    story.append(Paragraph(
        "In Assignment 4-5, the /health endpoint returned a static JSON response regardless "
        "of actual service state. In Assignment 6, each service now actively tests its database "
        "connection and includes the result in the health response:",
        STYLE_BODY
    ))
    story.append(Preformatted(
        "@application.get(\"/health\")\n"
        "def read_health_status():\n"
        "    try:\n"
        "        with database_engine.connect():\n"
        "            database_status = \"ok\"\n"
        "    except Exception:\n"
        "        database_status = \"unreachable\"\n"
        "    return {\"service\": \"order_service\", \"status\": \"ok\", \"database\": database_status}",
        STYLE_CODE
    ))
    story.append(Paragraph(
        "This means a health check failure now correctly reflects a real problem "
        "(such as a broken database hostname), not just whether the HTTP server is running.",
        STYLE_BODY
    ))

    story.append(Paragraph("2.5 Environment Variable Validation at Startup", STYLE_HEADING2))
    story.append(Paragraph(
        "All five services now validate required environment variables at startup using "
        "read_required_env_variable(). If any required variable is missing or empty, "
        "the service prints a clear error message and exits with code 1 before attempting "
        "to connect to the database. This makes misconfiguration immediately visible "
        "in the container logs.",
        STYLE_BODY
    ))
    story.append(Preformatted(
        "def read_required_env_variable(variable_name: str) -> str:\n"
        "    variable_value = os.getenv(variable_name)\n"
        "    if not variable_value:\n"
        "        print(f\"STARTUP ERROR: required env variable '{variable_name}' is missing\")\n"
        "        sys.exit(1)\n"
        "    return variable_value",
        STYLE_CODE
    ))


def build_monitoring_section(story):
    story.append(Paragraph("3. Monitoring and Alerting", STYLE_HEADING1))
    story.append(Paragraph(
        "Prometheus collects metrics from all five services every 10 seconds via the /metrics "
        "endpoint exposed by prometheus-fastapi-instrumentator. Alert rules evaluate these "
        "metrics and fire when conditions are met.",
        STYLE_BODY
    ))

    story.append(Paragraph("3.1 Alert Rules", STYLE_HEADING2))

    alert_data = [
        ["Alert Name", "Condition", "Severity", "Duration"],
        ["OrderServiceDown", "up{job='order_service'} == 0", "critical", "30s"],
        ["AuthServiceDown", "up{job='auth_service'} == 0", "critical", "30s"],
        ["ProductServiceDown", "up{job='product_service'} == 0", "high", "30s"],
        ["UserServiceDown", "up{job='user_service'} == 0", "high", "30s"],
        ["ChatServiceDown", "up{job='chat_service'} == 0", "medium", "30s"],
        ["HighOrderServiceErrorRate", "5xx rate > 10% over 2m", "critical", "1m"],
        ["HighAuthServiceErrorRate", "5xx rate > 5% over 2m", "high", "1m"],
        ["SlowOrderServiceResponse", "p95 latency > 2.0s", "high", "2m"],
        ["OrderServiceHighRequestRate", "req/s > 50 over 1m", "warning", "2m"],
    ]
    alert_table = Table(alert_data, colWidths=[5.5 * cm, 6.5 * cm, 2.5 * cm, 1.5 * cm])
    alert_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(alert_table)

    story.append(Paragraph("3.2 Grafana Dashboard", STYLE_HEADING2))
    story.append(Paragraph(
        "The Grafana dashboard at http://localhost:3000 (admin / admin12345) displays:",
        STYLE_BODY
    ))
    for panel in [
        "Service health time series (1 = UP, 0 = DOWN) for all five services",
        "Request rate per service in requests per second",
        "Error rate per service (HTTP 5xx responses per second)",
        "p95 response time for order_service and auth_service",
        "Stat panels showing count of healthy and down services",
    ]:
        story.append(Paragraph(f"• {panel}", STYLE_BULLET))

    story.append(Paragraph("3.3 Metrics Collected", STYLE_HEADING2))
    story.append(Paragraph(
        "prometheus-fastapi-instrumentator automatically exposes the following metrics "
        "for every service at /metrics:",
        STYLE_BODY
    ))
    metrics_data = [
        ["Metric Name", "Description"],
        ["http_requests_total", "Total HTTP requests, labelled by method, handler, status"],
        ["http_request_duration_seconds", "Request duration histogram for p50/p95/p99 percentiles"],
        ["up", "1 if the scrape target is reachable, 0 if not"],
    ]
    metrics_table = Table(metrics_data, colWidths=[7 * cm, 9 * cm])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(metrics_table)


def build_capacity_planning_section(story):
    story.append(Paragraph("4. Capacity Planning", STYLE_HEADING1))
    story.append(Paragraph(
        "Capacity planning determines how much load the system can handle before performance "
        "degrades and what actions should be taken when limits are reached. "
        "The analysis was performed by running a load simulation script against the running platform.",
        STYLE_BODY
    ))

    story.append(Paragraph("4.1 Load Simulation Method", STYLE_HEADING2))
    story.append(Paragraph(
        "The script scripts/run_load_simulation.py sends concurrent HTTP requests to all "
        "service endpoints and measures response times and error rates. "
        "The simulation parameters are:",
        STYLE_BODY
    ))
    sim_data = [
        ["Parameter", "Value"],
        ["Concurrent threads", "10"],
        ["Requests per thread", "20"],
        ["Total requests per endpoint", "200"],
        ["Delay between requests", "0.1 seconds"],
        ["Endpoints tested", "/api/products, /api/orders, /api/users, /api/messages"],
    ]
    sim_table = Table(sim_data, colWidths=[7 * cm, 9 * cm])
    sim_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(sim_table)

    story.append(Paragraph("4.2 Expected Observations Under Load", STYLE_HEADING2))
    story.append(Paragraph(
        "Based on the architecture and the incident from Assignment 4, the following "
        "behavior is expected under increased load:",
        STYLE_BODY
    ))
    for observation in [
        "order_service shows the highest response times because each request calls three "
        "other services (auth, user, product) plus performs a database write",
        "auth_service becomes a shared bottleneck because every order and chat request "
        "validates its token through auth_service",
        "product_service and user_service have lower latency as they only read from the database",
        "The PostgreSQL database is a single point of contention for all five services "
        "since they share one instance",
        "Error rates remain near zero until the database connection pool is exhausted",
    ]:
        story.append(Paragraph(f"• {observation}", STYLE_BULLET))

    story.append(Paragraph("4.3 Capacity Thresholds and Scaling Strategies", STYLE_HEADING2))

    scaling_data = [
        ["Scenario", "Threshold", "Strategy"],
        [
            "order_service p95 > 2s",
            "> 30 concurrent users",
            "Increase container CPU limit via Terraform instance_type upgrade"
        ],
        [
            "auth_service becomes bottleneck",
            "> 50 req/s total platform",
            "Scale auth_service horizontally with a load balancer in front"
        ],
        [
            "Database connection errors",
            "> 100 simultaneous connections",
            "Enable connection pooling (PgBouncer) in front of PostgreSQL"
        ],
        [
            "Overall platform slowdown",
            "p95 across all services > 1s",
            "Migrate to Kubernetes with HorizontalPodAutoscaler"
        ],
    ]
    scaling_table = Table(scaling_data, colWidths=[4.5 * cm, 4 * cm, 7.5 * cm])
    scaling_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(scaling_table)

    story.append(Paragraph("4.4 Vertical Scaling via Terraform", STYLE_HEADING2))
    story.append(Paragraph(
        "The Terraform configuration allows vertical scaling by changing the instance_type "
        "variable. No code changes are needed:",
        STYLE_BODY
    ))
    story.append(Preformatted(
        "terraform apply -var=\"instance_type=t3.medium\"",
        STYLE_CODE
    ))
    story.append(Paragraph(
        "Available instance types for this platform:",
        STYLE_BODY
    ))
    instance_data = [
        ["Instance Type", "vCPU", "RAM", "Suitable For"],
        ["t3.small", "2", "2 GB", "Development, light testing"],
        ["t3.medium", "2", "4 GB", "Normal production load"],
        ["t3.large", "2", "8 GB", "High load, all services under stress"],
        ["t3.xlarge", "4", "16 GB", "Heavy load with database under pressure"],
    ]
    instance_table = Table(instance_data, colWidths=[3.5 * cm, 2 * cm, 2.5 * cm, 8 * cm])
    instance_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(instance_table)

    story.append(Paragraph("4.5 Horizontal Scaling Proposal", STYLE_HEADING2))
    story.append(Paragraph(
        "Although horizontal scaling is not fully implemented in docker compose, "
        "the following approach is proposed for production environments using Kubernetes:",
        STYLE_BODY
    ))
    for step in [
        "Deploy each microservice as a Kubernetes Deployment with multiple replicas",
        "Use a Kubernetes Service (ClusterIP) as an internal load balancer in front of each service",
        "Configure a HorizontalPodAutoscaler targeting 70% CPU utilization",
        "Use Kubernetes Ingress as a replacement for the current Nginx gateway container",
        "Move PostgreSQL to a managed service (AWS RDS) to avoid single-instance database bottleneck",
    ]:
        story.append(Paragraph(f"• {step}", STYLE_BULLET))


def build_improvements_section(story):
    story.append(Paragraph("5. Improvements Over Previous Assignments", STYLE_HEADING1))

    improvements_data = [
        ["Area", "Assignment 4-5 State", "Assignment 6 Improvement"],
        [
            "Configuration validation",
            "No validation before deployment",
            "validate_deployment_config.py checks all env vars before deploy"
        ],
        [
            "Container restart",
            "Containers stayed down after crash",
            "restart: unless-stopped on all containers"
        ],
        [
            "Health check depth",
            "/health returned static JSON",
            "/health now tests actual database connection"
        ],
        [
            "Environment variables",
            "Single DATABASE_URL string, no validation",
            "Separate variables per component, validated at startup with sys.exit(1)"
        ],
        [
            "Alert coverage",
            "Only OrderServiceDown alert",
            "9 alert rules covering all services, error rates, latency, and volume"
        ],
        [
            "Capacity analysis",
            "Not performed",
            "Load simulation script with RPS, p95, error rate measurements"
        ],
        [
            "Recovery verification",
            "Manual curl commands",
            "wait_for_service_recovery.py polls all /health endpoints automatically"
        ],
        [
            "Dockerfile",
            "No curl available in container",
            "curl installed in all images for Docker health check support"
        ],
    ]
    table = Table(improvements_data, colWidths=[4 * cm, 5 * cm, 7 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)


def build_usage_guide_section(story):
    story.append(Paragraph("6. Step-by-Step Usage Guide", STYLE_HEADING1))

    story.append(Paragraph("6.1 Starting the Platform", STYLE_HEADING2))
    steps_start = [
        ("Clone or copy the project", "cp -r assignment6/ ~/qadam-retail/"),
        ("Validate configuration before deploying", "python3 scripts/validate_deployment_config.py"),
        ("Build and start all containers", "docker compose up -d --build"),
        ("Check all containers are running", "docker compose ps"),
        ("Wait for all services to become healthy", "python3 scripts/wait_for_service_recovery.py"),
        ("Open the web frontend", "http://localhost (login: asylbek / asylbek123)"),
        ("Open Prometheus targets", "http://localhost:9090/targets"),
        ("Open Grafana dashboard", "http://localhost:3000 (admin / admin12345)"),
    ]
    for step_number, (step_description, step_command) in enumerate(steps_start, 1):
        story.append(Paragraph(f"{step_number}. {step_description}", STYLE_BODY))
        story.append(Preformatted(step_command, STYLE_CODE))

    story.append(Paragraph("6.2 Running the Incident Scenario (from Assignment 4)", STYLE_HEADING2))
    incident_steps = [
        ("Start the broken configuration", "docker compose -f docker-compose.yml -f docker-compose.incident.yml up -d --build"),
        ("Watch order_service fail", "docker compose logs -f order_service"),
        ("Check Prometheus target status", "http://localhost:9090/targets  ->  order_service should be DOWN"),
        ("Restore correct configuration", "docker compose down && docker compose up -d --build"),
        ("Verify recovery automatically", "python3 scripts/wait_for_service_recovery.py"),
    ]
    for step_number, (step_description, step_command) in enumerate(incident_steps, 1):
        story.append(Paragraph(f"{step_number}. {step_description}", STYLE_BODY))
        story.append(Preformatted(step_command, STYLE_CODE))

    story.append(Paragraph("6.3 Running Capacity Planning Load Simulation", STYLE_HEADING2))
    story.append(Paragraph(
        "Make sure the platform is running before executing the load simulation:",
        STYLE_BODY
    ))
    story.append(Preformatted("python3 scripts/run_load_simulation.py", STYLE_CODE))
    story.append(Paragraph(
        "The script will print a capacity planning summary table showing RPS, "
        "average response time, p95 response time, and error count for each endpoint. "
        "While the simulation runs, observe the request rate graphs in Grafana.",
        STYLE_BODY
    ))

    story.append(Paragraph("6.4 Useful Diagnostic Commands", STYLE_HEADING2))
    diag_commands = [
        ("View logs for a specific service", "docker compose logs -f order_service"),
        ("Check container health status", "docker compose ps"),
        ("Inspect env variables in a running container", "docker compose exec order_service env"),
        ("Restart a single service", "docker compose restart order_service"),
        ("Stop everything and remove volumes", "docker compose down -v"),
    ]
    for command_description, command_text in diag_commands:
        story.append(Paragraph(f"• {command_description}:", STYLE_BULLET))
        story.append(Preformatted(command_text, STYLE_CODE))


def build_file_structure_section(story):
    story.append(Paragraph("7. Project File Structure", STYLE_HEADING1))
    story.append(Preformatted(
        "assignment6/\n"
        "├── docker-compose.yml              Main deployment with restart + healthchecks\n"
        "├── docker-compose.incident.yml     Override to simulate order_service failure\n"
        "├── services/\n"
        "│   ├── auth_service/app/main.py    Auth with env validation + DB health check\n"
        "│   ├── user_service/app/main.py    User with env validation + DB health check\n"
        "│   ├── product_service/app/main.py Product with env validation + DB health check\n"
        "│   ├── order_service/app/main.py   Order with env validation + DB health check\n"
        "│   └── chat_service/app/main.py    Chat with env validation + DB health check\n"
        "├── monitoring/\n"
        "│   ├── prometheus.yml              Scrape config for all 5 services\n"
        "│   ├── alert_rules.yml             9 alert rules across 3 groups\n"
        "│   └── grafana/dashboards/         Services overview dashboard JSON\n"
        "├── scripts/\n"
        "│   ├── validate_deployment_config.py  Pre-deployment config checker\n"
        "│   ├── run_load_simulation.py         Capacity planning load test\n"
        "│   └── wait_for_service_recovery.py   Automated recovery verifier\n"
        "├── terraform/\n"
        "│   ├── main.tf                     EC2 + security group + Docker install\n"
        "│   ├── variables.tf                instance_type, region, project_name\n"
        "│   └── outputs.tf                  Public IP, web URL, Grafana URL\n"
        "└── docs/\n"
        "    └── generate_report.py          This PDF report generator",
        STYLE_CODE
    ))


def generate_assignment6_pdf_report(output_path: str) -> None:
    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="Assignment 6 - Automation and Capacity Planning",
        author="Asylbek Abdibay, Bigali Omarov, Miras Saparov"
    )

    story = []

    build_cover_page(story)
    build_system_context_section(story)
    story.append(PageBreak())
    build_automation_section(story)
    story.append(PageBreak())
    build_monitoring_section(story)
    story.append(PageBreak())
    build_capacity_planning_section(story)
    story.append(PageBreak())
    build_improvements_section(story)
    story.append(PageBreak())
    build_usage_guide_section(story)
    story.append(PageBreak())
    build_file_structure_section(story)

    document.build(story)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    generate_assignment6_pdf_report(OUTPUT_PDF_PATH)
