pid_file = "/tmp/pidfile"

vault {
  address = "http://vault:8200" # Адреса локального Vault сервісу
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path = "/vault/role_id"
      secret_id_file_path = "/vault/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }
  sink "file" {
    config = { path = "/vault/secrets/token" }
  }
}

template {
  source      = "/config/secrets.ctmpl"
  destination = "/vault/secrets/config.json"
}
