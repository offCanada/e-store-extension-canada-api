from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    strategy="fixed-window",
    storage_uri="memory://"    # use redis, when multiple server workers are used or when users increases
)