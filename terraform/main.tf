terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # Usa una versión estable
    }
  }
}

provider "azurerm" {
  features {}
}

# 1. Creamos el Grupo de Recursos
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-dev"
  location = var.location
  
  tags = {
    Environment = "Dev"
    Project     = "Prueba Técnica Databricks"
  }
}

# 2. Creamos el Workspace de Databricks
resource "azurerm_databricks_workspace" "workspace" {
  name                        = "dbw-${var.project_name}-dev"
  resource_group_name         = azurerm_resource_group.rg.name
  location                    = azurerm_resource_group.rg.location
  sku                         = "premium" # ¡CRÍTICO! Unity Catalog exige la versión Premium
  managed_resource_group_name = "rg-${var.project_name}-dev-managed"
  
  tags = azurerm_resource_group.rg.tags
}