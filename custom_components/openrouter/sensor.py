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

ACCOUNT_SENSOR_NAMES: dict[str, str] = {
    "total_credits": "Total Credits",
    "total_usage": "Total Usage",
    "balance": "Balance",
}

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

KEY_SENSOR_NAMES: dict[str, str] = {
    "usage": "Usage",
    "usage_daily": "Daily Usage",
    "usage_weekly": "Weekly Usage",
    "usage_monthly": "Monthly Usage",
    "limit": "Limit",
    "limit_remaining": "Limit Remaining",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OpenRouterCoordinator = hass.data[DOMAIN][entry.entry_id]
    exchange_mode = entry.options.get(CONF_EXCHANGE_RATE_MODE, EXCHANGE_RATE_NONE)
    has_exchange = exchange_mode != EXCHANGE_RATE_NONE
    currency = hass.config.currency

    entities: list[OpenRouterSensor] = []

    for desc in ACCOUNT_SENSORS:
        name = ACCOUNT_SENSOR_NAMES[desc.key]
        entities.append(OpenRouterSensor(coordinator, desc, entry, name=name))
        if has_exchange:
            entities.append(
                OpenRouterSensor(
                    coordinator, desc, entry,
                    name=f"{name} ({currency})",
                    converted=True,
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
            sensor_name = f"{key_label} {KEY_SENSOR_NAMES[desc.key]}"
            entities.append(
                OpenRouterSensor(
                    coordinator, desc, entry,
                    name=sensor_name,
                    key_hash=key_hash,
                )
            )
            if has_exchange:
                entities.append(
                    OpenRouterSensor(
                        coordinator, desc, entry,
                        name=f"{sensor_name} ({currency})",
                        key_hash=key_hash,
                        converted=True,
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
        name: str,
        key_hash: str | None = None,
        converted: bool = False,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._key_hash = key_hash
        self._converted = converted

        id_parts = [entry.entry_id]
        if key_hash:
            id_parts.append(key_hash)
        id_parts.append(description.key)
        if converted:
            id_parts.append("converted")
        self._attr_unique_id = "_".join(id_parts)
        self._attr_name = name

        if converted:
            self._attr_native_unit_of_measurement = coordinator.hass.config.currency
            self._attr_suggested_display_precision = 0
        else:
            self._attr_native_unit_of_measurement = "USD"

    @property
    def device_info(self) -> DeviceInfo:
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
