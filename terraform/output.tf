output "databricks_workspace_url" {
  value       = azurerm_databricks_workspace.workspace.workspace_url
  description = "La URL para acceder a tu nuevo entorno de Databricks"
}