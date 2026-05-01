# 1. Crear el Grupo de Recursos en Azure
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# 2. Crear el Workspace de Databricks
resource "azurerm_databricks_workspace" "workspace" {
  name                        = var.workspace_name
  resource_group_name         = azurerm_resource_group.rg.name
  location                    = azurerm_resource_group.rg.location
  sku                         = "premium" # Obligatorio para Unity Catalog
  managed_resource_group_name = "${var.resource_group_name}-managed"

  tags = {
    Environment = "Dev"
    Project     = "QUIND_Tech_Test"
  }
}

# 3. Mostrar la URL del Workspace al terminar
output "databricks_workspace_url" {
  value = "https://${azurerm_databricks_workspace.workspace.workspace_url}"
}