"""Sensor platform for OpenRouter."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CURRENCY,
    CONF_EXCHANGE_RATE_ENTITY,
    CONF_EXCHANGE_RATE_MODE,
    CONF_FIXED_EXCHANGE_RATE,
    DOMAIN,
    EXCHANGE_RATE_FIXED,
    EXCHANGE_RATE_NONE,
    EXCHANGE_RATE_SENSOR,
)
from .coordinator import OpenRouterCoordinator


@dataclass(frozen=True, kw_only=True)
class OpenRouterSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], float | None]


ACCOUNT_SENSORS: tuple[OpenRouterSensorDescription, ...] = (
    OpenRouterSensorDescription(
        key="total_credits",
        value_fn=lambda d: d.get("credits", {}).get("total_credits"),
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    OpenRouterSensorDescription(
        key="total_usage",
        value_fn=lambda d: d.get("credits", {}).get("total_usage"),
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    OpenRouterSensorDescription(
        key="balance",
        value_fn=lambda d: round(
            (d.get("credits", {}).get("total_credits") or 0)
            - (d.get("credits", {}).get("total_usage") or 0),
            10,
        ),
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
)

KEY_SENSORS: tuple[OpenRouterSensorDescription, ...] = (
    OpenRouterSensorDescription(
        key="usage",
        value_fn=lambda d: d.get("usage"),
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    OpenRouterSensorDescription(
        key="usage_daily",
        value_fn=lambda d: d.get("usage_daily"),
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    OpenRouterSensorDescription(
        key="usage_weekly",
        value_fn=lambda d: d.get("usage_weekly"),
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    OpenRouterSensorDescription(
        key="usage_monthly",
        value_fn=lambda d: d.get("usage_monthly"),
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    OpenRouterSensorDescription(
        key="limit",
        value_fn=lambda d: d.get("limit"),
        state_class=None,
        suggested_display_precision=2,
    ),
    OpenRouterSensorDescription(
        key="limit_remaining",
        value_fn=lambda d: d.get("limit_remaining"),
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OpenRouterCoordinator = hass.data[DOMAIN][entry.entry_id]
    exchange_mode = entry.options.get(CONF_EXCHANGE_RATE_MODE, EXCHANGE_RATE_NONE)
    has_exchange = exchange_mode != EXCHANGE_RATE_NONE
    currency = entry.options.get(CONF_CURRENCY, hass.config.currency)

    entities: list[OpenRouterSensor] = []

    for desc in ACCOUNT_SENSORS:
        entities.append(OpenRouterSensor(coordinator, desc, entry))
        if has_exchange:
            entities.append(
                OpenRouterSensor(
                    coordinator, desc, entry,
                    converted=True, currency=currency,
                )
            )

    for idx, key_data in enumerate(coordinator.data.get("keys", []), 1):
        key_hash = key_data["hash"]
        name = key_data.get("name") or ""
        label = key_data.get("label") or ""
        if name:
            key_label = name
        elif label and not label.startswith("sk-"):
            key_label = label
        else:
            key_label = f"Key {idx}"
        for desc in KEY_SENSORS:
            entities.append(
                OpenRouterSensor(
                    coordinator, desc, entry,
                    key_hash=key_hash, key_label=key_label,
                )
            )
            if has_exchange:
                entities.append(
                    OpenRouterSensor(
                        coordinator, desc, entry,
                        key_hash=key_hash, key_label=key_label,
                        converted=True, currency=currency,
                    )
                )

    async_add_entities(entities)


class OpenRouterSensor(CoordinatorEntity[OpenRouterCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(
        self,
        coordinator: OpenRouterCoordinator,
        description: OpenRouterSensorDescription,
        entry: ConfigEntry,
        *,
        key_hash: str | None = None,
        key_label: str | None = None,
        converted: bool = False,
        currency: str = "USD",
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._key_hash = key_hash
        self._key_label = key_label
        self._converted = converted

        id_parts = [entry.entry_id]
        if key_hash:
            id_parts.append(key_hash)
        id_parts.append(description.key)
        if converted:
            id_parts.append("converted")
        self._attr_unique_id = "_".join(id_parts)

        if converted:
            self._attr_translation_key = f"{description.key}_converted"
            self._attr_translation_placeholders = {"currency": currency}
            self._attr_native_unit_of_measurement = currency
            self._attr_suggested_display_precision = 0
        else:
            self._attr_translation_key = description.key
            self._attr_native_unit_of_measurement = "USD"

    @property
    def device_info(self) -> DeviceInfo:
        if self._key_hash:
            return DeviceInfo(
                identifiers={(DOMAIN, f"{self._entry.entry_id}_{self._key_hash}")},
                name=f"OpenRouter - {self._key_label}",
                manufacturer="OpenRouter",
                entry_type=DeviceEntryType.SERVICE,
                via_device=(DOMAIN, self._entry.entry_id),
            )
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="OpenRouter",
            manufacturer="OpenRouter",
            entry_type=DeviceEntryType.SERVICE,
        )

    def _get_source_data(self) -> dict | None:
        if self.coordinator.data is None:
            return None
        if self._key_hash:
            for key in self.coordinator.data.get("keys", []):
                if key.get("hash") == self._key_hash:
                    return key
            return None
        return self.coordinator.data

    def _get_exchange_rate(self) -> float | None:
        mode = self._entry.options.get(CONF_EXCHANGE_RATE_MODE, EXCHANGE_RATE_NONE)
        if mode == EXCHANGE_RATE_FIXED:
            return self._entry.options.get(CONF_FIXED_EXCHANGE_RATE)
        if mode == EXCHANGE_RATE_SENSOR:
            entity_id = self._entry.options.get(CONF_EXCHANGE_RATE_ENTITY)
            if entity_id:
                state = self.hass.states.get(entity_id)
                if state and state.state not in ("unknown", "unavailable"):
                    try:
                        return float(state.state)
                    except (ValueError, TypeError):
                        pass
        return None

    @property
    def native_value(self) -> float | None:
        data = self._get_source_data()
        if data is None:
            return None
        value = self.entity_description.value_fn(data)
        if value is None:
            return None
        if self._converted:
            rate = self._get_exchange_rate()
            if rate is None:
                return None
            return round(value * rate, 2)
        return value
