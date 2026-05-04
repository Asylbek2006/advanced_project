variable "aws_region" {
  description = "AWS region where the platform will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix used for all AWS resources"
  type        = string
  default     = "qadam-retail-platform"
}

variable "instance_type" {
  description = "EC2 instance type. Use t3.small for normal load, t3.medium for high load"
  type        = string
  default     = "t3.small"
}

variable "key_pair_name" {
  description = "Name of the existing AWS key pair for SSH access"
  type        = string
  default     = "qadam-key"
}
