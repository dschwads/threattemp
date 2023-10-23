variable "sysdig_access_key" {
type = string
default = ""
}
variable "sysdig_secure_api_token" {
type = string
default = ""
}
variable "s3_bucket_name" {
type = string
default = ""
}
variable "s3_bucket_region" {
type = string
default = ""
# us-east-1
}
variable "s3_iam_profile" {
type = string
default = ""
}

variable "vpc_id" {
type = string
default = ""
# vpc-123459a
}
variable "subnets" {
type = list
default = [""]
# [subnet-a12345, subnet-b12345]
# two different availability zones
}
variable "orchestrator_host" {
type = string
default = ""
}
# collector.sysdigcloud.com"
variable "orchestrator_port" {
type = number
default = 6443
}

