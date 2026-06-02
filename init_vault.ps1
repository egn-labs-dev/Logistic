$env:VAULT_CMD = "docker-compose -f docker-compose.prod.yml exec -T -e VAULT_ADDR=http://127.0.0.1:8200 vault vault"

Invoke-Expression "$env:VAULT_CMD login root"
Invoke-Expression "$env:VAULT_CMD secrets enable -path=secret kv-v2"
Invoke-Expression "$env:VAULT_CMD kv put secret/config database_url='postgresql+asyncpg://db_user:db_password@db:5432/logistics_db' gemini_api_key='AIzaSy_TEST_KEY_GEMINI_837492'"
Invoke-Expression "$env:VAULT_CMD auth enable approle"

"path `"secret/data/config`" { capabilities = [`"read`"] }" | docker-compose -f docker-compose.prod.yml exec -T -e VAULT_ADDR=http://127.0.0.1:8200 vault vault policy write app-policy -

Invoke-Expression "$env:VAULT_CMD write auth/approle/role/fastapi-role token_policies='app-policy' token_ttl=1h token_max_ttl=4h"

docker-compose -f docker-compose.prod.yml exec -T -e VAULT_ADDR=http://127.0.0.1:8200 vault vault read -field=role_id auth/approle/role/fastapi-role/role-id | Out-File -FilePath "config\role_id" -Encoding ASCII -NoNewline
docker-compose -f docker-compose.prod.yml exec -T -e VAULT_ADDR=http://127.0.0.1:8200 vault vault write -f -field=secret_id auth/approle/role/fastapi-role/secret-id | Out-File -FilePath "config\secret_id" -Encoding ASCII -NoNewline

Write-Host "Vault initialized successfully!"
