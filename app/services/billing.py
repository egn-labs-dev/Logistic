import logging
import os

import stripe
from sqlalchemy import select

from app.db.database import async_session_maker
from app.db.models import OrganizationSetting

logger = logging.getLogger(__name__)

# Беремо ключ з середовища (починається з sk_test_... або sk_live_...)
stripe.api_key = os.getenv("STRIPE_API_KEY")

async def report_successful_lead_to_stripe(tenant_id: str, session_id: str):
    """Відправляє подію використання (Usage Record) у Stripe для Pay-per-Lead."""
    if not stripe.api_key:
        logger.warning("Stripe API key is not configured. Billing skipped.")
        return

    # Відкриваємо нову сесію для фонової задачі
    async with async_session_maker() as db:
        try:
            # Отримуємо Stripe ID клієнта
            result = await db.execute(
                select(OrganizationSetting.stripe_item_id)
                .where(OrganizationSetting.organization_id == tenant_id)
            )
            stripe_item_id = result.scalar_one_or_none()

            if not stripe_item_id:
                logger.error(f"No Stripe Item ID configured for tenant {tenant_id}. Cannot bill.")
                return

            # Відправляємо +1 успішний лід у Stripe (асинхронно)
            await stripe.SubscriptionItem.create_usage_record_async(
                stripe_item_id,
                quantity=1,
                timestamp="now",
                action="increment",
            )
            
            logger.info(f"BILLING SUCCESS: Billed tenant {tenant_id} for lead {session_id}.")

        except stripe.StripeError as e:
            # Специфічні помилки платіжної системи
            logger.error(f"Stripe billing failed for tenant {tenant_id}, session {session_id}: {e.user_message}")
        except Exception as e:
            logger.error(f"Unexpected billing error: {str(e)}")
