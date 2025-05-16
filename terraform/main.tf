resource "azurerm_resource_group" "rg" {
  name     = "${var.image_name}-${var.environment}-rg"
  location = var.location
}

resource "azurerm_service_plan" "asp" {
  name                = "asp-${var.image_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = "${var.image_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.asp.id
  https_only          = true

  site_config {
    application_stack {
      docker_registry_url = "https://${var.registry_name}.azurecr.io"
      docker_image_name   = "${var.image_name}:${var.image_tag}"
    }
    always_on                         = true
    health_check_path                 = "/health"
    health_check_eviction_time_in_min = 2
  }

  app_settings = {
    "FORCE_REDEPLOY"    = timestamp()
  }

  identity {
    type = "SystemAssigned"
  }
}
