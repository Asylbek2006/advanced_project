output "platform_server_public_ip" {
  description = "Public IP address of the platform server"
  value       = aws_instance.platform_server.public_ip
}

output "platform_web_url" {
  description = "URL to access the web frontend"
  value       = "http://${aws_instance.platform_server.public_ip}"
}

output "grafana_dashboard_url" {
  description = "URL to access Grafana monitoring dashboard"
  value       = "http://${aws_instance.platform_server.public_ip}:3000"
}

output "prometheus_url" {
  description = "URL to access Prometheus metrics"
  value       = "http://${aws_instance.platform_server.public_ip}:9090"
}
