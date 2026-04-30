terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# 1. Crear Grupo de Recursos
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-dev"
  location = var.location
  
  tags = {
    Environment = "Dev"
    Project     = "Prueba Técnica Databricks"
  }
}

# 2. Crear Workspace de Databricks
resource "azurerm_databricks_workspace" "workspace" {
  name                        = "dbw-${var.project_name}-dev"
  resource_group_name         = azurerm_resource_group.rg.name
  location                    = azurerm_resource_group.rg.location
  sku                         = "premium" 
  managed_resource_group_name = "rg-${var.project_name}-dev-managed"
  
  tags = azurerm_resource_group.rg.tags
}