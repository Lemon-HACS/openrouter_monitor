"""Config flow for OpenRouter."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .const import (
    API_BASE_URL,
    CONF_API_KEY,
    CONF_EXCHANGE_RATE_ENTITY,
    CONF_EXCHANGE_RATE_MODE,
    CONF_FIXED_EXCHANGE_RATE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    EXCHANGE_RATE_FIXED,
    EXCHANGE_RATE_NONE,
    EXCHANGE_RATE_SENSOR,
)


async def _validate_api_key(hass, api_key: str) -> str | None:
    """Return error key or None if valid."""
    session = async_get_clientsession(hass)
    try:
        async with session.get(
            f"{API_BASE_URL}/credits",
            headers={"Authorization": f"Bearer {api_key}"},
        ) as resp:
            if resp.status in (401, 403):
                return "invalid_auth"
            if resp.status != 200:
                return "cannot_connect"
    except Exception:
        return "cannot_connect"
    return None


class OpenRouterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenRouter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            error = await _validate_api_key(self.hass, user_input[CONF_API_KEY])
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title="OpenRouter",
                    data={CONF_API_KEY: user_input[CONF_API_KEY]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_API_KEY): str}
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return OpenRouterOptionsFlow(config_entry)


class OpenRouterOptionsFlow(OptionsFlow):
    """Handle options for OpenRouter."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            mode = user_input[CONF_EXCHANGE_RATE_MODE]
            if mode == EXCHANGE_RATE_FIXED:
                return await self.async_step_fixed_rate()
            if mode == EXCHANGE_RATE_SENSOR:
                return await self.async_step_sensor_rate()
            self._options.pop(CONF_FIXED_EXCHANGE_RATE, None)
            self._options.pop(CONF_EXCHANGE_RATE_ENTITY, None)
            return self.async_create_entry(data=self._options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self._options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(int, vol.Range(min=1, max=60)),
                    vol.Required(
                        CONF_EXCHANGE_RATE_MODE,
                        default=self._options.get(
                            CONF_EXCHANGE_RATE_MODE, EXCHANGE_RATE_NONE
                        ),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=EXCHANGE_RATE_NONE,
                                    label="None (USD only)",
                                ),
                                selector.SelectOptionDict(
                                    value=EXCHANGE_RATE_FIXED,
                                    label="Fixed rate",
                                ),
                                selector.SelectOptionDict(
                                    value=EXCHANGE_RATE_SENSOR,
                                    label="Sensor",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_fixed_rate(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            self._options.pop(CONF_EXCHANGE_RATE_ENTITY, None)
            return self.async_create_entry(data=self._options)

        return self.async_show_form(
            step_id="fixed_rate",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FIXED_EXCHANGE_RATE,
                        default=self._options.get(CONF_FIXED_EXCHANGE_RATE, 1350.0),
                    ): vol.Coerce(float),
                }
            ),
        )

    async def async_step_sensor_rate(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            self._options.pop(CONF_FIXED_EXCHANGE_RATE, None)
            return self.async_create_entry(data=self._options)

        return self.async_show_form(
            step_id="sensor_rate",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EXCHANGE_RATE_ENTITY,
                        default=self._options.get(CONF_EXCHANGE_RATE_ENTITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                }
            ),
        )
