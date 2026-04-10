from faststream.rabbit import RabbitBroker

from core.config import settings


broker = RabbitBroker(settings.rabbitmq_url)