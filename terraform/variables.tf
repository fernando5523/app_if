variable "environment" {
  description = "Entorno de despliegue: staging o production"
  type        = string
}

variable "location" {
  description = "Región de Azure"
  type        = string
  default     = "westus"
}

variable "registry_name" {
  description = "Nombre de tu Azure Container Registry"
  type        = string
}

variable "image_name" {
  description = "Nombre de la imagen Docker"
  type        = string
}

variable "image_tag" {
  description = "Tag de la imagen Docker"
  type        = string
}