from datetime import datetime
import json
from typing import Any
from . import configio
from . import spec


class JsonWriter(configio.ConfigurationWriter):
    @classmethod
    def dump_section(cls, node: spec.Section):
        return {
            node._FIELD_VAR_MAP[name]: (cls.dump_value(node.get_field(name), value))
            for name, value in node._value.items()
        }

    @classmethod
    def dump_value(cls, node: spec.AnyConfigField, value):
        """convert value into json_serializable object that can be used as a key or value"""
        match node:
            case spec.ConfigurationFieldABCMeta() | spec.Section():
                return cls.dump_section(value)
            case spec.Table(
                _,
                spec.ConfigurationFieldABCMeta() | spec.Section() | spec.ConfigUnion(),
            ):
                return {
                    cls.dump_value(key, key): cls.dump_value(val, val)
                    for key, val in value.items()
                }
            case spec.ConfigEnum(_, True):
                return value.name
            case spec.ConfigEnum(_, False):
                return value.value
            case str() | int() | float() | datetime() | dict() | None:
                return value
            case _:
                # magic method to make writing new field types possible
                if hasattr(node, "__write_json_value__"):
                    return value.__write_json_value__(
                        node, value
                    )  # return a json serializable object

    @classmethod
    def dumps(cls, node) -> str:
        match node:
            case spec.Section():
                return json.dumps(cls.dump_section(node), indent=4)
            case spec.ConfigurationField():
                if not node._has_default:
                    raise ValueError("Field has no default value")

                dumped_value = cls.dump_value(node, node._default_value)
                if isinstance(dumped_value, dict):
                    return json.dumps(dumped_value)
                return str(dumped_value)
            case _:
                raise ValueError(node)

    @classmethod
    def dump(cls, file, node):
        super().dump(file, node)

    @classmethod
    def load(cls, file):
        if isinstance(file, str):
            with open(file, "r") as f:
                return json.load(f)
        return json.load(file)

    @classmethod
    def loads(cls, data: str) -> dict[str, Any]:
        return json.loads(data)
