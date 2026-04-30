variable "project_name" {
  description = "Nombre base para los recursos"
  type        = string
  default     = "nyctaxi-etl"
}

variable "location" {
  description = "Región de Azure donde se desplegará"
  type        = string
  default     = "East US" 
}