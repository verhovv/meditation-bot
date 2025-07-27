import aiohttp
import asyncio
from typing import Optional, Dict, Any
import sys, os, django
from pathlib import Path
import uuid

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.core.settings")
django.setup()

from config import config


class YooKassaAsyncClient:
    BASE_URL = "https://api.yookassa.ru/v3/"

    def __init__(self):
        self.shop_id = config.YOOKASSA_SHOP_ID
        self.secret_key = config.YOOKASSA_API_KEY
        self.auth = aiohttp.BasicAuth(self.shop_id, self.secret_key)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def create_payment(
            self,
            amount: float,
            currency: str = "RUB",
            description: Optional[str] = 'Тестовый платеж',
            return_url: Optional[str] = "https://payments.yookassa.ru",
            metadata: Optional[Dict[str, Any]] = None,
            capture: bool = True,
            payment_method_type: str = "bank_card"
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}payments"

        headers = {
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

        payload = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": currency
            },
            "payment_method": {
                "type": payment_method_type
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": capture,
            "description": description or "Оплата заказа"
        }

        if metadata:
            payload["metadata"] = metadata

        async with self.session.post(
                url,
                json=payload,
                auth=self.auth,
                headers=headers
        ) as response:
            return await response.json()

    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}payments/{payment_id}"
        async with self.session.get(url, auth=self.auth) as response:
            return await response.json()

    async def get_receipt_by_payment(self, payment_id: str):
        url = f"{self.BASE_URL}receipts?payment_id={payment_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Error: {response.status}, {error}")


async def main():
    async with YooKassaAsyncClient() as client:
        payment = await client.create_payment(
            amount=100.00,
            description="Тестовый платеж",
            return_url="https://payments.yookassa.ru",
        )
        print("Создан платеж:", payment)

    await asyncio.sleep(15)

    async with YooKassaAsyncClient() as client:
        status = await client.get_payment_status(payment['id'])
        print("Статус платежа:", status)


if __name__ == "__main__":
    asyncio.run(main())
