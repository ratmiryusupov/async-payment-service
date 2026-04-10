from models.payment import Payment


def build_payment_webhook_payload(payment: Payment) -> dict:
    return {
        "payment_id": str(payment.id),
        "status": payment.status.value,
        "amount": str(payment.amount),
        "currency": payment.currency.value,
        "description": payment.description,
        "metadata": payment.metadata_json,
        "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
    }