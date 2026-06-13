from typing import cast

import httpx

from instances.app_instances import AppIntancesKey, app_instances

DEFAULT_TIMEOUT = 10.0


def get_http_client() -> httpx.AsyncClient:
    client = app_instances.get(AppIntancesKey.HTTP_CLIENT)
    return cast(httpx.AsyncClient, client)


async def init_http_client() -> None:
    app_instances[AppIntancesKey.HTTP_CLIENT] = httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT
    )


async def close_http_client() -> None:
    client = app_instances.pop(AppIntancesKey.HTTP_CLIENT, None)
    if client is not None:
        await client.aclose()
