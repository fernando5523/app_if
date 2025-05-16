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


variable "app_workers" {
description = "Número de procesos workers de la aplicación"
type        = number
}

variable "app_db_host" {
description = "Host de la base de datos principal"
type        = string
}

variable "app_db_name" {
description = "Nombre de la base de datos principal"
type        = string
}

variable "app_db_user" {
description = "Usuario de la base de datos principal"
type        = string
}

variable "app_db_pass" {
description = "Contraseña de la base de datos principal"
type        = string
sensitive   = true
}

variable "app_db_token_host" {
description = "Host de la base de datos de tokens"
type        = string
}

variable "app_db_token_name" {
description = "Nombre de la base de datos de tokens"
type        = string
}

variable "app_db_token_user" {
description = "Usuario de la base de datos de tokens"
type        = string
}

variable "app_db_token_pass" {
description = "Contraseña de la base de datos de tokens"
type        = string
sensitive   = true
}

variable "app_db_token_port" {
description = "Puerto de la base de datos de tokens"
type        = number
}

variable "erp_client_id" {
description = "Client ID para autenticación en Dynamics"
type        = string
}

variable "erp_client_secret" {
description = "Client Secret para autenticación en Dynamics"
type        = string
sensitive   = true
}

variable "app_mode" {
description = "Modo de la aplicación (Produccion, Staging, etc.)"
type        = string
}

variable "erp_debug" {
description = "URL de entorno sandbox de Dynamics"
type        = string
}

variable "erp_production" {
description = "URL de entorno producción de Dynamics"
type        = string
}

variable "base_url_rrhh" {
description = "URL base del servicio de RRHH"
type        = string
}