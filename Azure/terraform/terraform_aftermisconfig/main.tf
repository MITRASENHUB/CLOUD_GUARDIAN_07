resource "azurerm_resource_group" "cloudguardian" {
  name     = "rg-cloudguardian-dev"
  location = "Central India"
}
resource "azurerm_storage_account" "cloudguardianstorage" {
  name                     = "cgstorage2026demo01"
  resource_group_name      = azurerm_resource_group.cloudguardian.name
  location                 = azurerm_resource_group.cloudguardian.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # -------------------------------------------------
  # MC-01
  # Intentional Misconfiguration
  # Public Network Access Enabled
  # -------------------------------------------------

  public_network_access_enabled = true

  ###########################################################
  # MC-02
  # Intentional Misconfiguration
  # Blob Public Access Enabled
  ###########################################################

  allow_nested_items_to_be_public = true

  ###########################################################
  # MC-03
  # Intentional Misconfiguration
  # Shared Key Authentication Enabled
  ###########################################################

  shared_access_key_enabled = true

  ###########################################################
  # MC-04
  # Intentional Misconfiguration
  # Microsoft Entra (OAuth) Authentication Disabled
  ###########################################################

  default_to_oauth_authentication = false
  ###########################################################
  # MC-05
  # Intentional Misconfiguration
  #
  # Blob Soft Delete is NOT configured.
  #
  # Expected Prowler Check:
  # storage_blob_soft_delete_enabled
  ###########################################################

  # No blob delete retention policy configured.

  ###########################################################
  # MC-06
  # Intentional Misconfiguration
  #
  # Blob Versioning is NOT configured.
  #
  # Expected Prowler Check:
  # storage_blob_versioning_enabled
  ###########################################################

  # Blob Versioning intentionally omitted.

 ###########################################################
  # MC-011
  # Intentional Misconfiguration -Storage Account Minimum TLS Version = TLS 1.0
###########################################################
  min_tls_version = "TLS1_0"
}


resource "azurerm_virtual_network" "cloudguardian_vnet" {
  name                = "vnet-cloudguardian-dev"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.cloudguardian.location
  resource_group_name = azurerm_resource_group.cloudguardian.name
}
resource "azurerm_network_security_group" "cloudguardian_nsg" {
  name                = "nsg-cloudguardian-dev"
  location            = azurerm_resource_group.cloudguardian.location
  resource_group_name = azurerm_resource_group.cloudguardian.name
}

# -----------------------------
# MC-08: Insecure SSH Rule
# -----------------------------
resource "azurerm_network_security_rule" "allow_ssh_from_anywhere" {
  name      = "Allow-SSH-From-Internet"
  priority  = 100
  direction = "Inbound"
  access    = "Allow"
  protocol  = "Tcp"

  source_port_range      = "*"
  destination_port_range = "22"

  source_address_prefix      = "*"
  destination_address_prefix = "*"

  resource_group_name         = azurerm_resource_group.cloudguardian.name
  network_security_group_name = azurerm_network_security_group.cloudguardian_nsg.name
}
# -----------------------------
# MC-09: HTTP (Port 80) Open to the Internet
# -----------------------------
resource "azurerm_network_security_rule" "allow_http_from_anywhere" {

  name      = "Allow-HTTP-From-Internet"
  priority  = 110
  direction = "Inbound"
  access    = "Allow"
  protocol  = "Tcp"

  source_port_range      = "*"
  destination_port_range = "80"

  source_address_prefix      = "*"
  destination_address_prefix = "*"

  resource_group_name         = azurerm_resource_group.cloudguardian.name
  network_security_group_name = azurerm_network_security_group.cloudguardian_nsg.name
}
resource "azurerm_subnet" "cloudguardian_subnet" {
  name                 = "subnet-cloudguardian-dev"
  resource_group_name  = azurerm_resource_group.cloudguardian.name
  virtual_network_name = azurerm_virtual_network.cloudguardian_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# -----------------------------
# Introduced as NSG is currently not associated with anything. In that state, the new SSH rule exists in Azure but will not affect traffic, and Prowler may not flag it as an exposed VM.
# -----------------------------
resource "azurerm_subnet_network_security_group_association" "cloudguardian_nsg_assoc" {
  subnet_id                 = azurerm_subnet.cloudguardian_subnet.id
  network_security_group_id = azurerm_network_security_group.cloudguardian_nsg.id
}

resource "azurerm_public_ip" "cloudguardian_public_ip" {
  name                = "pip-cloudguardian-dev"
  location            = azurerm_resource_group.cloudguardian.location
  resource_group_name = azurerm_resource_group.cloudguardian.name
  allocation_method   = "Static"
  sku                 = "Standard"
}
resource "azurerm_subnet" "cloudguardian_db_subnet" {
  name                 = "subnet-db-cloudguardian-dev"
  resource_group_name  = azurerm_resource_group.cloudguardian.name
  virtual_network_name = azurerm_virtual_network.cloudguardian_vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}
resource "azurerm_network_interface" "cloudguardian_nic" {
  name                = "nic-cloudguardian-web"
  location            = azurerm_resource_group.cloudguardian.location
  resource_group_name = azurerm_resource_group.cloudguardian.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.cloudguardian_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.cloudguardian_public_ip.id
  }
}
resource "azurerm_linux_virtual_machine" "cloudguardian_vm" {
  name                = "vm-cloudguardian-web"
  resource_group_name = azurerm_resource_group.cloudguardian.name
  location            = azurerm_resource_group.cloudguardian.location
  size                = "Standard_B2ats_v2"

  admin_username = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.cloudguardian_nic.id
  ]

  disable_password_authentication = true

  admin_ssh_key {
    username   = "azureuser"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCreX4pH1etrsMMfaUUAc2I5mmNKdF//Tz4o7jalqgo7H+kY/hlUHL6eUGCfM6d8K4IQqxwYpFc/t0TTwCj9LwszWE+pD5DzC8zPMCw/yshs7i5hqiD4N/oZmXuuPqLtfvvegeJCbriyaWsesYgp7DCtrYDp6PPPakw2NLeX9c3hzj9+1lIU7V07sPRhLlU7FlJGzwynlKzIIJkanLYvKicUktWTqWLK3wcdr3O7d6INehouZfO6MzsjE+CmC+fXTdSky+tbStlQUmYnVy23VneoPXftyWNgYfgb9TAhkRx2Fm5ZPQLrI3WaWOwgX0gan3X1obQOA5i5TCejQF1Pt7ntFjORIDu0a4/euLgon+0YTu88wUXjj/lr1YYZ5eTUEEeL2Py5+RE7RA0/wpV1UcB2DDegw4sSlZTGZjQqGMl0mxX2oAcL1qyFQ3nEuQaPDNHV/vAYO8ohmEhw6kIXRP8mYpKMTlg/bZ89P38RDPhoUaGTTsKslWoueGfyh2SYJoIRHWA+n2XuKT5OmqhLIGxdhXYyKOceCbRYO/lbu89x3lPqHAtJ3r5svt9PUjVqhwHh2gMjmkH+XVQHbeo1zk0xFASz/cZOik9AOayPEojp41LsusAb3Q/IuvVEOA18YDVNAeo1AthhbOZobWZMMciqcA2jppCecMlB1geIQMHvw== artly@ARTLY_1"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  computer_name = "cloudguardian"

  tags = {
    Environment = "Development"
    Project     = "CloudGuardian"
  }
}
resource "azurerm_mssql_server" "cloudguardian_sql_server" {
  name                = "sqlcgserver2026"
  resource_group_name = azurerm_resource_group.cloudguardian.name
  location            = azurerm_resource_group.cloudguardian.location
  version             = "12.0"
  ###########################################################
  # MC-07
  # Intentional Misconfiguration
  # SQL Server Public Network Access Enabled
  ###########################################################

  public_network_access_enabled = true
  administrator_login           = "sqladminuser"
  administrator_login_password  = "CloudGuardian@1234"

  minimum_tls_version = "1.2"

  tags = {
    Environment = "Development"
    Project     = "CloudGuardian"
  }
}
resource "azurerm_mssql_database" "cloudguardian_database" {
  name      = "CloudGuardianDB"
  server_id = azurerm_mssql_server.cloudguardian_sql_server.id

  sku_name = "Basic"

  tags = {
    Environment = "Development"
    Project     = "CloudGuardian"
  }
}
###########################################################
# MC-10 – SQL Server Firewall Allows Public Access (0.0.0.0)
###########################################################
resource "azurerm_mssql_firewall_rule" "allow_all_azure" {
  name      = "AllowAllAzureServices"
  server_id = azurerm_mssql_server.cloudguardian_sql_server.id

  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
###########################################################
# MC-12 – added new Activity Log Diagnostic Setting and commenting it out to introduce failure
###########################################################
/*
resource "azurerm_monitor_diagnostic_setting" "subscription_logs" {
  name               = "ActivityLogExport"
  target_resource_id = data.azurerm_subscription.current.id

  storage_account_id = azurerm_storage_account.cloudguardianstorage.id

  enabled_log {
    category = "Administrative"
  }

  enabled_log {
    category = "Security"
  }

  enabled_log {
    category = "Policy"
  }

  enabled_log {
    category = "Alert"
  }
}

data "azurerm_subscription" "current" {}
*/