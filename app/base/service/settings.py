from asgiref.sync import sync_to_async
from base.models import Settings


@sync_to_async
def get_setting(key: str) -> str:
    setting = Settings.objects.filter(key=key).first()
    return setting.value
