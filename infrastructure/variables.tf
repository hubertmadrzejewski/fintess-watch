variable "resource_group_name" {
  description = "Name of the resource group"
  default     = "iot-terraform-rg"
}

variable "location" {
  description = "Azure region"
  default     = "uksouth"
}

variable "iot_hub_name" {
  description = "Base name of the IoT Hub (suffix will be added)"
  default     = "tf-iot"
}

variable "storage_account_name" {
  description = "Base name of the Storage Account (suffix will be added)"
  default     = "tfstg"
}

variable "container_name" {
  description = "Base name of the blob container (suffix will be added)"
  default     = "telemetry"
}

