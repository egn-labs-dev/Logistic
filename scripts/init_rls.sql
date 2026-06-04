-- Скрипт для увімкнення RLS
-- Вмикаємо Row Level Security для таблиці замовлень вантажів
ALTER TABLE cargo_orders ENABLE ROW LEVEL SECURITY;

-- Створюємо політику безпеки: користувач бачить ТІЛЬКИ дані своєї організації
CREATE POLICY cargo_orders_isolation_policy ON cargo_orders
    USING (organization_id = current_setting('app.current_organization_id', true));

-- Так само захищаємо аудит-логи (тільки для читання суперюзером або по org_id)
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_isolation_policy ON audit_logs
    USING (organization_id = current_setting('app.current_organization_id', true));

-- RLS for users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;
CREATE POLICY users_isolation ON users
  USING (organization_id = current_setting('app.current_organization_id', true));
