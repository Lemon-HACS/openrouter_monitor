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
    CONF_CURRENCY,
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

EXCHANGE_RATE_OPTIONS = [EXCHANGE_RATE_NONE, EXCHANGE_RATE_FIXED, EXCHANGE_RATE_SENSOR]

CURRENCY_OPTIONS = [
    "USD", "EUR", "GBP", "JPY", "KRW", "CNY", "CAD", "AUD",
    "CHF", "HKD", "SGD", "TWD", "INR", "THB", "VND",
]


def _settings_schema(
    update_interval: int = DEFAULT_UPDATE_INTERVAL,
    exchange_rate_mode: str = EXCHANGE_RATE_NONE,
    currency: str = "USD",
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_UPDATE_INTERVAL, default=update_interval
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, max=60, step=1, mode=selector.NumberSelectorMode.BOX
                )
            ),
            vol.Required(
                CONF_EXCHANGE_RATE_MODE, default=exchange_rate_mode
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=EXCHANGE_RATE_OPTIONS,
                    translation_key="exchange_rate_mode",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_CURRENCY, default=currency
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=CURRENCY_OPTIONS,
                    translation_key="currency",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _fixed_rate_schema(default: float = 1450.0) -> vol.Schema:
    return vol.Schema(
        {vol.Required(CONF_FIXED_EXCHANGE_RATE, default=default): vol.Coerce(float)}
    )


def _sensor_rate_schema(default: str | None = None) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_EXCHANGE_RATE_ENTITY, default=default
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
        }
    )


async def _validate_api_key(hass, api_key: str) -> str | None:
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

    def __init__(self) -> None:
        self._api_key: str = ""
        self._options: dict = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            error = await _validate_api_key(self.hass, user_input[CONF_API_KEY])
            if error:
                errors["base"] = error
            else:
                self._api_key = user_input[CONF_API_KEY]
                return await self.async_step_settings()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_settings(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            mode = user_input[CONF_EXCHANGE_RATE_MODE]
            if mode == EXCHANGE_RATE_FIXED:
                return await self.async_step_fixed_rate()
            if mode == EXCHANGE_RATE_SENSOR:
                return await self.async_step_sensor_rate()
            return self._create_entry()

        return self.async_show_form(
            step_id="settings",
            data_schema=_settings_schema(
                currency=self.hass.config.currency,
            ),
        )

    async def async_step_fixed_rate(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            return self._create_entry()

        return self.async_show_form(
            step_id="fixed_rate",
            data_schema=_fixed_rate_schema(),
        )

    async def async_step_sensor_rate(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            return self._create_entry()

        return self.async_show_form(
            step_id="sensor_rate",
            data_schema=_sensor_rate_schema(),
        )

    def _create_entry(self):
        return self.async_create_entry(
            title="OpenRouter Monitor",
            data={CONF_API_KEY: self._api_key},
            options=self._options,
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
            data_schema=_settings_schema(
                update_interval=self._options.get(
                    CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                ),
                exchange_rate_mode=self._options.get(
                    CONF_EXCHANGE_RATE_MODE, EXCHANGE_RATE_NONE
                ),
                currency=self._options.get(
                    CONF_CURRENCY, self.hass.config.currency
                ),
            ),
        )

    async def async_step_fixed_rate(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            self._options.pop(CONF_EXCHANGE_RATE_ENTITY, None)
            return self.async_create_entry(data=self._options)

        return self.async_show_form(
            step_id="fixed_rate",
            data_schema=_fixed_rate_schema(
                default=self._options.get(CONF_FIXED_EXCHANGE_RATE, 1450.0)
            ),
        )

    async def async_step_sensor_rate(self, user_input=None):
        if user_input is not None:
            self._options.update(user_input)
            self._options.pop(CONF_FIXED_EXCHANGE_RATE, None)
            return self.async_create_entry(data=self._options)

        return self.async_show_form(
            step_id="sensor_rate",
            data_schema=_sensor_rate_schema(
                default=self._options.get(CONF_EXCHANGE_RATE_ENTITY)
            ),
        )
