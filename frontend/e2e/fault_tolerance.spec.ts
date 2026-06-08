import { test, expect } from '@playwright/test';

test.describe('Chat Engine Fault Tolerance & Error Handling', () => {
  
  test.beforeEach(async ({ page }) => {
    // Мокуємо логін
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk5OTk5OTk5OTl9.signature',
          token_type: 'bearer'
        }),
      });
    });

    // Мокуємо авторизацію
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'user-123', role: 'DISPATCHER', organization_id: 'org-789' }),
      });
    });

    // Повертаємо активний інцидент для роботи диспетчера
    await page.route('**/api/v1/dispatcher/alerts*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'alert-error-test',
            session_id: 'alert-error-test',
            status: 'human_controlled',
            title: 'Тест стійкості до збоїв',
            description: 'Перевірка обробки 500-ї помилки API',
            created_at: new Date().toISOString()
          }
        ]),
      });
    });

    // Порожня історія чату
    await page.route('**/api/v1/dispatcher/history/*', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
    });
  });

  test('should display descriptive error alert and retry button when API fails', async ({ page }) => {
    // Логінимось
    await page.goto('/login');
    const emailInput = page.locator('input[type="email"], input[name="username"]').first();
    await expect(emailInput).toBeVisible({ timeout: 5000 });
    await emailInput.fill('dispatcher@zt-dispatch.com');
    await page.locator('input[type="password"]').fill('password');
    await page.locator('button[type="submit"], button:has-text("Увійти"), button:has-text("Login")').first().click();

    // Очікуємо дашборд
    await expect(page).toHaveURL(/.*\/$/);

    // Відкриваємо модалку чату (клікаємо по інциденту)
    const liveFeedItem = page.locator(':text("alert-error-test")');
    await expect(liveFeedItem.first()).toBeVisible({ timeout: 5000 });

    const openChatButton = page.locator('button:has-text("Переглянути чат"), button:has-text("Відкрити"), button:has-text("chat"), [aria-label*="чат"]').first();
    await openChatButton.click();
    
    const chatInput = page.locator('[role="dialog"] input').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });

    // НАЛАШТУВАННЯ ЗБОЮ: Мокуємо критичну помилку сервера
    await page.route('**/api/v1/dispatcher/send', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Gemini API is temporarily unavailable or rate limited.' }),
      });
    });

    // Відправляємо текст
    const testMessage = 'Тестове повідомлення для симуляції збою системи.';
    await chatInput.fill(testMessage);
    const sendButton = page.locator('[role="dialog"] button:has-text("Відправити"), [role="dialog"] button:has-text("Send"), [role="dialog"] button[type="submit"], [role="dialog"] button svg.lucide-send').first();
    await sendButton.click();

    // ВЕРИФІКАЦІЯ: Інтерфейс не впав, текст не зник, вивелося сповіщення
    await expect(chatInput).toHaveValue(testMessage);

    const errorAlert = page.locator('[role="dialog"] :text("Помилка відправки")');
    await expect(errorAlert.first()).toBeVisible({ timeout: 5000 });

    // Перевіряємо наявність кнопки «Повторити»
    const retryButton = page.locator('[role="dialog"] button:has-text("Повторити спробу")');
    await expect(retryButton.first()).toBeVisible();
  });
});
