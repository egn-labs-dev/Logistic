import { test, expect } from '@playwright/test';

test.describe('Dashboard & Live Feed Chat Lifecycle (Human Intercept)', () => {
  
  test.beforeEach(async ({ page }) => {
    // 0. Мокуємо логін
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk5OTk5OTk5OTl9.signature', // Valid-looking JWT with future exp
          token_type: 'bearer'
        }),
      });
    });

    // 1. Мокуємо авторизацію диспетчера
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-123',
          email: 'dispatcher@zt-dispatch.com',
          role: 'DISPATCHER',
          organization_id: 'org-789'
        }),
      });
    });

    // 2. Мокуємо список алертів/інцидентів
    await page.route('**/api/v1/dispatcher/alerts*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'alert-456',
            session_id: 'alert-456',
            status: 'human_controlled', 
            title: 'Критичний лід: Термінова доставка',
            description: 'Запит на перевезення промислового обладнання Київ-Чернівці',
            created_at: new Date().toISOString()
          }
        ]),
      });
    });

    // 3. Мокуємо порожню історію чату
    await page.route('**/api/v1/dispatcher/history/alert-456', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });
  });

  test('should navigate to dashboard, open modal from live feed, and process message', async ({ page }) => {
    // Крок 0: Заходимо на логін
    await page.goto('/login');
    const emailInput = page.locator('input[type="email"], input[name="username"]').first();
    await expect(emailInput).toBeVisible({ timeout: 5000 });
    await emailInput.fill('dispatcher@zt-dispatch.com');
    await page.locator('input[type="password"]').fill('password');
    await page.locator('button[type="submit"], button:has-text("Увійти"), button:has-text("Login")').first().click();

    // Крок 1: Очікуємо перехід на дашборд
    await expect(page).toHaveURL(/.*\/$/);

    // Крок 2: Знаходимо наш інцидент у списку "Live Feed"
    const liveFeedItem = page.locator(':text("alert-456")');
    await expect(liveFeedItem.first()).toBeVisible({ timeout: 5000 });

    // Крок 3: Клікаємо на кнопку відкриття чату/інциденту
    const openChatButton = page.locator('button:has-text("Переглянути чат"), button:has-text("Відкрити"), button:has-text("chat"), [aria-label*="чат"]').first();
    await openChatButton.click();

    // Крок 4: Очікуємо, що ChatHistoryModal з'явився на екрані
    const modalTitle = page.locator('[role="dialog"] :text("alert-456"), [role="dialog"] :text("Історія"), [role="dialog"] :text("History")').first();
    await expect(modalTitle).toBeVisible({ timeout: 5000 });

    // Крок 5: Перевіряємо наявність textarea
    const chatInput = page.locator('[role="dialog"] input').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });

    // Перехоплюємо POST-запит
    await page.route('**/api/v1/dispatcher/send', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'success',
            order_created: true,
            order_data: {
              id: 'cargo-999',
              status: 'PENDING_DISPATCH',
              details: {
                origin: 'Київ',
                destination: 'Чернівці',
                weight_kg: 4500,
                cargo_type: 'Промислове обладнання'
              }
            }
          }),
        });
      }
    });

    // Крок 6: Вводимо повідомлення
    await chatInput.fill('Підтверджую замовлення Київ-Чернівці на 4.5 тонн.');
    const sendButton = page.locator('[role="dialog"] button:has-text("Відправити"), [role="dialog"] button:has-text("Send"), [role="dialog"] button[type="submit"], [role="dialog"] button svg.lucide-send').first();
    await sendButton.click();

    // Крок 7: Верифікація реакції UI
    await expect(chatInput).toHaveValue('', { timeout: 7000 });
  });
});
