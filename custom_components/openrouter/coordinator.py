"""DataUpdateCoordinator for OpenRouter."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class OpenRouterCoordinator(DataUpdateCoordinator):
    """Fetch OpenRouter credits and key usage data."""

    def __init__(
        self, hass: HomeAssistant, api_key: str, update_interval: int
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="OpenRouter",
            update_interval=timedelta(minutes=update_interval),
        )
        self._api_key = api_key

    async def _fetch(self, session, path: str):
        async with session.get(
            f"{API_BASE_URL}/{path}",
            headers={"Authorization": f"Bearer {self._api_key}"},
        ) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"API /{path} returned {resp.status}")
            return (await resp.json()).get("data")

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            credits_data, keys_data = await asyncio.gather(
                self._fetch(session, "credits"),
                self._fetch(session, "keys"),
            )
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with OpenRouter: {err}"
            ) from err

        return {
            "credits": credits_data or {},
            "keys": keys_data or [],
            "last_fetched": dt_util.utcnow(),
        }
