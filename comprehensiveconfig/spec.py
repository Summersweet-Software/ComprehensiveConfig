from abc import ABC, ABCMeta, abstractmethod
import enum
from pathlib import Path
import re
import sys
from types import UnionType
import types
from typing import Any, Protocol, Self, Type, Union, overload, override
import typing

from comprehensiveconfig.validators import (
    validate_path_agnostic,
    validate_path_sys_aware,
    validate_path_unix,
    validate_path_windows,
)


class _NoDefaultValueT:
    """Represents not having a default value.
    Cannot be instantiated normally"""

    @classmethod
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError()


# instantiate _NoDefaultValueT using object class's __new__ method
NoDefaultValue = object.__new__(_NoDefaultValueT)


class ConfigurationFieldMeta(type):
    """Provides custom union logic for configuration fields"""

    def __or__[S, T](self: S, value: Type[T] | T) -> S | Type[T]:
        """broaden normal Union behavior so things don't break"""
        if not isinstance(value, type) and not isinstance(
            value, BaseConfigurationField
        ):
            raise TypeError()
        return Union[self, value]


def fix_unions(union: UnionType | Any) -> "ConfigUnion | BaseConfigurationField":
    if not isinstance(union, (typing._UnionGenericAlias, types.UnionType)):
        return union
    left, *right = union.__args__
    output = left
    for typ in right:
        output = ConfigUnion(output, typ)
    return output


class ConfigurationFieldABCMeta(ABCMeta, ConfigurationFieldMeta):
    pass


class BaseConfigurationField(ABC):
    """The base class for a configuration field"""

    __slots__ = ("_field_variable", "_parent", "_value")

    _field_variable: None | str
    """The python variable that this field is attached to"""

    _sorting_order: int
    """The sorting order for dumping the data.
    This is important when sections are taken into account"""

    def __call__[T](self, value: T) -> T:
        self._validate_value(value)
        return value

    @abstractmethod
    def _validate_value(self, value: Any, name: str | None = None, /):
        raise ValueError(value)


class ConfigurationField[T](BaseConfigurationField):
    """The base class for an inline configuration field"""

    __slots__ = (
        "_name",
        "_default_value",
        "_has_default",
        "_nullable",
        "doc",
        "_inline_doc",
    )

    _parent: "ConfigSectionMeta | None"
    """The parent to this node"""
    _name: None | str
    """The actual name used inside the configuration
    This has to be valid for whatever config format you use"""
    _default_value: T | _NoDefaultValueT
    _has_default: bool
    _nullable: bool
    """is this value nullable"""
    doc: str | None
    """Doc comment"""
    inline_doc: bool
    """if a doc comment is present- should we try to put the doc
        comment on the same line as the value?"""

    _holds: T
    """describes what type this field holds"""
    _sorting_order = 0

    def __init__(
        self,
        default_value: T | _NoDefaultValueT = NoDefaultValue,
        /,
        name: str | None = None,
        nullable: bool = False,
        doc: None | str = None,
        inline_doc: bool = True,
    ):
        self._name = name
        self._nullable = nullable
        self._field_variable = None
        self._default_value = default_value
        self._has_default = default_value is not NoDefaultValue
        self.doc = doc
        self._inline_doc = inline_doc

    @abstractmethod
    def _validate_value(self, value: Any, name: str | None = None, /):
        if value is None and not self._nullable:
            raise ValueError(f'Field, "{name or self._name}", is not nullable')

    def __or__(self, value: "ConfigSectionMeta | AnyConfigField") -> "ConfigUnion":
        return ConfigUnion(self, value)

    def __set_name__(self, owner, name):
        # Automatically set the internal storage name (e.g., _age)
        self._field_variable = name
        if self._name is None:
            self._name = name

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> T: ...

    def __get__(self, instance: "Section | None", owner) -> T | Self:
        if instance is None:
            return self
        # Retrieve the value from the instance's dictionary
        return instance._value[self._field_variable]

    def __set__(self, instance, value: T):
        if self._field_variable not in instance._value.keys():
            raise KeyError(self._field_variable)
        instance._value[self._field_variable] = value


type AnyConfigField = ConfigurationField | BaseConfigurationField | UnionType | typing._GenericUnionAlias


# TODO: Remove duplication of these kinds of descriptors
class SectionName:
    """Descriptor for section names.
    Chooses between class name and instance name automatically"""

    def __get__(self, instance, owner) -> str:
        if instance is None:
            return object.__getattribute__(owner, "_cls_name")
        return object.__getattribute__(instance, "_instance_name")

    def __set__(self, instance, value):
        instance._instance_name = value


class SectionParent:
    """Descriptor for section parents.
    Chooses between class parent and instance parent automatically"""

    def __get__(self, instance, owner):
        if instance is None:
            return object.__getattribute__(owner, "_cls_parent")
        return object.__getattribute__(instance, "_instance_parent")

    def __set__(self, instance, value):
        instance._instance_parent = value


class ConfigSectionMeta(ConfigurationFieldABCMeta):
    _FIELDS: dict[str, ConfigurationField]
    _SECTIONS: dict[str, "ConfigSectionMeta"]
    _ALL_FIELDS: dict[str, "ConfigurationField | ConfigSectionMeta"]
    _FIELD_NAME_MAP: dict[str, str]
    """Maps config names to their actual variable names"""
    _FIELD_VAR_MAP: dict[str, str]
    """Maps variable names to their actual config names"""
    _cls_parent: "BaseConfigurationField | ConfigSectionMeta | None"
    _cls_name: str
    """The name of the class"""
    _field_variable: str
    _has_default: bool
    _default_value: dict[str | None, Any] | _NoDefaultValueT
    _sorting_order: int

    if typing.TYPE_CHECKING:

        _name = SectionName()
        _parent = SectionParent()

        def _validate_value(self, value: Any, name: str | None = None, /): ...


class Section(BaseConfigurationField, metaclass=ConfigSectionMeta):
    """A baseclass for sections to be defined"""

    __slots__ = "_value"
    _name = SectionName()
    """The name in the configuration file (chooses between _real_name and _cls_name)"""
    _instance_name: str
    """The actual name in the configuration file"""
    _parent = SectionParent()
    _instance_parent: AnyConfigField | None
    _value: dict[str | None, Any]
    _sorting_order = 1

    @classmethod
    def __init_subclass__(cls, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._cls_parent = None
        cls._cls_name = name or cls.__name__
        cls._FIELDS = {
            field_name: field
            for field_name, field in cls.__dict__.items()
            if isinstance(field, ConfigurationField)
        }
        cls._SECTIONS = {
            field_name: field
            for field_name, field in cls.__dict__.items()
            if isinstance(field, ConfigSectionMeta) and Section in field.__mro__
        }
        cls._ALL_FIELDS = cls._FIELDS | cls._SECTIONS
        for name, field in cls._ALL_FIELDS.items():
            field._field_variable = name
            if field._name is None:
                field._name = name
            if isinstance(field, ConfigSectionMeta):
                field._cls_parent = cls
            else:
                field._parent = cls

        cls._FIELD_NAME_MAP = {
            field._name: variable
            for variable, field in cls._ALL_FIELDS.items()
            if field._name is not None
        }

        cls._FIELD_VAR_MAP = {value: key for key, value in cls._FIELD_NAME_MAP.items()}

        # generate default value
        cls._has_default = all(field._has_default for field in cls._ALL_FIELDS.values())
        if cls._has_default:
            cls._default_value = {
                field._name: field._default_value
                for field in cls._ALL_FIELDS.values()
                if field._name is not None
            }
        else:
            cls._default_value = NoDefaultValue

    def __init__(
        self,
        value: dict[str, Any] | _NoDefaultValueT = NoDefaultValue,
        /,
        **kwargs: Any,
    ):
        self._name = self._cls_name
        self._parent = self._cls_parent
        if isinstance(value, _NoDefaultValueT):
            value = {}
        if not isinstance(value, (dict, Section)):
            raise ValueError(value)
        value = value | kwargs
        self._validate_value(value)
        self._value = {
            self._FIELD_NAME_MAP[name]: self._ALL_FIELDS[self._FIELD_NAME_MAP[name]](
                val
            )
            for name, val in value.items()
        }

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Retrieve the value from the instance's dictionary
        return instance._value[self._field_variable]

    def __call__[T](self, value: T) -> T:
        raise NotImplementedError()

    def get_field(self, name):
        return object.__getattribute__(self.__class__, name)

    def __getattribute__(self, name: str) -> Any:
        if name in object.__getattribute__(self, "_ALL_FIELDS").keys():
            return object.__getattribute__(self, "_value")[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        fields = object.__getattribute__(self, "_ALL_FIELDS")
        if name in fields.keys():
            object.__getattribute__(self, "_value")[name] = fields[name](value)
        else:
            super().__setattr__(name, value)

    def __getitem__(self, name):
        return self._value[self._FIELD_VAR_MAP[name]]

    def keys(self):
        return self._value.keys()

    def items(self):
        return self._value.items()

    def values(self):
        return self._value.values()

    def __or__(self, other: dict) -> Self:
        return self.__class__(
            {self._FIELD_NAME_MAP[key]: value for key, value in self._value.items()}
            | other
        )

    @classmethod
    def _validate_value(cls, value: Any, name: str | None = None, /):
        if not isinstance(value, (dict, cls)):
            raise ValueError(value)
        for field in cls._ALL_FIELDS.values():
            if field._name not in value.keys():
                raise KeyError(
                    f'Section, "{name or cls._name}", missing field: {field._name}'
                )  # missing key
            field._validate_value(
                value[field._name], f"{name or cls._name}.{field._name}"
            )

    @property
    def nullable(self):
        return False


class TableSpec(ConfigurationField, metaclass=ConfigSectionMeta):
    """A model/Table"""

    __slots__ = ()

    _cls_name: str
    """The actual name in the configuration file"""
    _cls_has_default: bool
    _cls_default_value: dict[str, Any] | _NoDefaultValueT
    _default_value: dict[str, Any] | _NoDefaultValueT

    _holds: dict[str, Any]

    @classmethod
    def __init_subclass__(cls, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._cls_name = name or cls.__name__
        cls._FIELDS = {
            field_name: field
            for field_name, field in cls.__dict__.items()
            if isinstance(field, ConfigurationField)
        }
        cls._SECTIONS = {
            field_name: field
            for field_name, field in cls.__dict__.items()
            if isinstance(field, ConfigSectionMeta) and Section in field.__mro__
        }
        cls._ALL_FIELDS = cls._FIELDS | cls._SECTIONS
        for name, field in cls._ALL_FIELDS.items():
            field._field_variable = name
            if field._name is None:
                field._name = name
            if isinstance(field, type):
                field._parent = cls

        cls._FIELD_NAME_MAP = {
            field._name: variable
            for variable, field in cls._ALL_FIELDS.items()
            if field._name is not None
        }

        cls._FIELD_VAR_MAP = {value: key for key, value in cls._FIELD_NAME_MAP.items()}
        cls._sorting_order = max(
            field._sorting_order for field in cls._ALL_FIELDS.values()
        )

        # generate default value
        cls._cls_has_default = all(
            field._has_default for field in cls._ALL_FIELDS.values()
        )
        if cls._cls_has_default:
            cls._cls_default_value = {
                field._name: field._default_value
                for field in cls._ALL_FIELDS.values()
                if field._name is not None
            }
        else:
            cls._cls_default_value = NoDefaultValue

    def __init__(
        self,
        default_value: dict[str, Any] | _NoDefaultValueT = NoDefaultValue,
        /,
        *args,
        **kwargs,
    ):
        if default_value is NoDefaultValue:
            default_value = self._cls_default_value
        super().__init__(default_value, *args, **kwargs)

    def _validate_value(self, value: Any, name: str | None = None, /):
        if not isinstance(value, dict):
            raise ValueError(value)
        for field in self._ALL_FIELDS.values():
            if field._name not in value.keys():
                raise KeyError(
                    f'Table, "{name or self._name}", missing field: {field._name}'
                )  # missing key
            field._validate_value(value[field._name])


class Table[K, V](ConfigurationField):
    """A generic Table"""

    __slots__ = ("key_type", "value_type", "_sorting_order")
    __match_args__ = ("key_type", "value_type")

    _holds: dict[K, V]

    def __init__(
        self,
        default_value: dict[K, V] = {},
        /,
        key_type: AnyConfigField | None = None,
        value_type: AnyConfigField | None = None,
        *args,
        **kwargs,
    ):
        if not isinstance(key_type, BaseConfigurationField):
            assert TypeError("key_type must be an instance of `BaseConfigurationField`")
        if not isinstance(value_type, BaseConfigurationField):
            assert TypeError(
                "value_type must be an instance of `BaseConfigurationField`"
            )
        self.key_type = fix_unions(key_type)
        self.value_type = fix_unions(value_type)

        self._sorting_order = max(
            self.key_type._sorting_order, self.value_type._sorting_order
        )

        return super().__init__(default_value, *args, **kwargs)

    def __call__(self, value: dict[K, V]) -> dict[K, V]:
        self._validate_value(value, self._name)
        return {self.key_type(key): self.value_type(val) for key, val in value.items()}

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> dict[K, V]: ...

    def __get__(self, instance: "Section | None", owner) -> dict[K, V] | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: dict[K, V]):
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value)
        if not isinstance(value, dict):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid dict: {value}"
            )

        if self.key_type is not None:
            for c, key in enumerate(value.keys()):
                self.key_type._validate_value(
                    key, f"{name or self._name}[{key}] (keyname)"
                )

        if self.value_type is not None:
            for key, val in value.items():
                self.value_type._validate_value(
                    val, f"{name or self._name}[{key}] (value)"
                )


class List[T](ConfigurationField):
    """List field"""

    __slots__ = "inner_type"

    _holds: list[T]

    def __init__(
        self,
        default_value: list[T] = [],
        /,
        inner_type: AnyConfigField | None = None,
        *args,
        **kwargs,
    ):
        self.inner_type = fix_unions(inner_type)

        return super().__init__(default_value, *args, **kwargs)

    def __call__(self, value: list[T]) -> list[T]:
        self._validate_value(value, self._name)
        return [self.inner_type(val) for val in value]

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> list[T]: ...

    def __get__(self, instance: "Section | None", owner) -> list[T] | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: list[T]):
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value, name)
        if not isinstance(value, list):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid list: {value}"
            )

        match self.inner_type:
            case None:
                return
            case type():
                raise ValueError(self.inner_type)

            case BaseConfigurationField():
                for c, item in enumerate(value):
                    self.inner_type._validate_value(item, f"{name or self._name}[{c}]")


class Boolean(ConfigurationField):
    """Boolean (true/false) field"""

    __slots__ = ()

    _holds: bool

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> bool: ...

    def __get__(self, instance: "Section | None", owner) -> bool | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: bool):
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value)
        if not isinstance(value, bool):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid boolean: {repr(value)}"
            )


class Float(ConfigurationField):
    """Floating point field"""

    __slots__ = ()

    _holds: float

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> float: ...

    def __get__(self, instance: "Section | None", owner) -> float | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: float):
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value)
        if not isinstance(value, (float, int)):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid number: {repr(value)}"
            )


class Integer(ConfigurationField):
    """integer field"""

    __slots__ = ()

    _holds: int

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> int: ...

    def __get__(self, instance: "Section | None", owner) -> int | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: int):
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value)
        if not isinstance(value, int):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid integer: {repr(value)}"
            )


type Number = Float
"""More generic number field, just an alias for Float"""


class Text(ConfigurationField):
    """string field (with optional regex validation)"""

    __slots__ = "_regex_pattern"

    _holds: str

    _regex_pattern: str

    def __init__(
        self,
        default_value: str | _NoDefaultValueT = NoDefaultValue,
        /,
        *args,
        regex: str = r".*",
        **kwargs,
    ):
        super().__init__(default_value, *args, **kwargs)
        self._regex_pattern = regex

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> str: ...

    def __get__(self, instance: "Section | None", owner) -> str | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: str):
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value)
        if not isinstance(value, str):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid string: {value}"
            )
        if re.fullmatch(self._regex_pattern, value) is None:
            raise ValueError(
                f'Field: {name or self._name}\n"{value}" did not match regex pattern: {self._regex_pattern}'
            )


class PathField(ConfigurationField):
    """A Folder/file Path that is validated to ensure it is a valid* filepath
    validity does not mean the path exists.

    __This is not a bug__

    This is to allow users of this class to decide how *they*
    want to handle file/folders not existing.
    For example, they might want to create the folder themselves.
    A user might also be referencing a file on a *different* filesystem!
    """

    __slots__ = "_path_type", "_path_validator"

    class PathType(enum.IntEnum):
        """Determines what you want the path's to point to (files or directories)"""

        directory = enum.auto()
        file = enum.auto()
        directory_or_file = enum.auto()
        """Disables this type of check"""

    class PathValidator(enum.IntEnum):
        """Determines which validation strategy for the path"""

        windows = enum.auto()
        unix = enum.auto()
        agnostic = enum.auto()
        """Doesn't care if the path is for windows or unix/linux"""
        current_system = enum.auto()
        """ensures that the path is valid for the current system/os."""

    _holds: Path

    _path_type: PathType
    _path_validator: PathValidator

    def __init__(
        self,
        default_value: str | Path | _NoDefaultValueT = NoDefaultValue,
        /,
        path_type: PathType = PathType.directory_or_file,
        path_validator: PathValidator = PathValidator.agnostic,
        *args,
        **kwargs,
    ):
        super().__init__(default_value, *args, **kwargs)
        self._path_type = path_type
        self._path_validator = path_validator

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> Path: ...

    def __get__(self, instance: "Section | None", owner) -> Path | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: str | Path):
        if isinstance(value, str):
            value = Path(value)
        super().__set__(instance, value)

    def _validate_value(self, value: Any, name: str | None = None, /):
        super()._validate_value(value)

        if isinstance(value, str):
            value = Path(value)

        if not isinstance(value, Path):
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid Path object: {value}"
            )

        is_valid = True
        path_type_name = ""

        # Validate the file path for the specified system
        match self._path_validator:
            case PathField.PathValidator.windows:
                is_valid = validate_path_windows(str(value))
                path_type_name = "windows "
            case PathField.PathValidator.unix:
                is_valid = validate_path_unix(str(value))
                path_type_name = "unix "
            case PathField.PathValidator.agnostic:
                is_valid = validate_path_agnostic(str(value))
            case PathField.PathValidator.current_system:
                is_valid = validate_path_sys_aware(str(value))
                path_type_name = "windows " if sys.platform == "win32" else "unix "

        if not is_valid:
            raise ValueError(
                f"Field: {name or self._name}\nValue was not a valid {path_type_name}path: {value}"
            )

        # verify the type of object the path points to is what we expect.
        match self._path_type:
            case PathField.PathType.directory:
                if value.is_file():
                    raise ValueError(
                        f"Field: {name or self._name}\nValue was not a valid directory: {value}"
                    )
            case PathField.PathType.file:
                if value.is_dir():
                    raise ValueError(
                        f"Field: {name or self._name}\nValue was not a valid file: {value}"
                    )


class ConfigUnion[L, R](ConfigurationField):
    """union field"""

    __slots__ = ("_left_type", "_right_type", "_sorting_order")

    _holds: L | R

    _left_type: BaseConfigurationField | ConfigSectionMeta
    _right_type: BaseConfigurationField | ConfigSectionMeta

    def __init__(
        self,
        left_type: AnyConfigField | ConfigSectionMeta,
        right_type: AnyConfigField | ConfigSectionMeta,
        *args,
        **kwargs,
    ):
        super().__init__(NoDefaultValue, *args, **kwargs)
        self._left_type = fix_unions(left_type)
        self._right_type = fix_unions(right_type)
        self._sorting_order = max(
            self._left_type._sorting_order, self._right_type._sorting_order
        )

    def __call__(self, *args, **kwargs):
        try:
            return self._left_type(*args, **kwargs)
        except ValueError:  # if left side fails, try the right
            return self._right_type(*args, **kwargs)

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> L | R: ...

    def __get__(self, instance: "Section | None", owner) -> L | R | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: L | R):
        super().__set__(instance, value)

    def _validate_value(self, value: L | R, name: str | None = None, /):
        super()._validate_value(value)
        try:
            self._left_type._validate_value(value, name)
        except ValueError:  # if left side fails, try the right
            self._right_type._validate_value(value, name)


class ConfigEnum[T](ConfigurationField):
    """enumeration field"""

    __slots__ = ("_enum", "_enum_members_reversed", "_by_name")
    __match_args__ = ("_enum", "_by_name")

    _holds: T

    _enum: Type[T]
    """The enumeration type"""
    _enum_members_reversed: dict[Any, T]
    """A reversed mapping of values  and enum variants in the enumeration type"""
    _by_name: bool
    """whether or not the field value is using the
       enum variants' name or value"""

    def __init__(
        self,
        enum_type: Type[T],
        default_value: T | _NoDefaultValueT = NoDefaultValue,
        /,
        *args,
        by_name=False,
        **kwargs,
    ):
        self._enum = enum_type
        if not isinstance(enum_type, enum.EnumMeta):
            raise ValueError("Type must be an enumerator")
        self._enum_members_reversed = {
            v.value: v for v in enum_type.__members__.values()
        }
        self._by_name = by_name

        return super().__init__(default_value, *args, **kwargs)

    def get_value(self, value: Any):
        if isinstance(value, self._enum):
            return value
        if self._by_name:
            if value not in self._enum.__members__.keys():
                raise ValueError(f"Invalid Enum Variant: {value}")
            return self._enum.__members__[value]
        if value not in self._enum_members_reversed.keys():
            raise ValueError(f"Invalid Enum Variant: {value}")
        return self._enum_members_reversed[value]

    def __call__(self, value: Any):
        return self.get_value(value)

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> T: ...

    def __get__(self, instance: "Section | None", owner) -> T | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: T | Any):
        if isinstance(value, self._enum):
            return super().__set__(instance, value)
        super().__set__(instance, self.get_value(value))

    def _validate_value(self, value: Any, name: str | None = None, /):
        if isinstance(value, self._enum):
            super()._validate_value(value, name)
        super()._validate_value(self.get_value(value), name)


class ConfigObjectType[T](Protocol):
    """A protocol to define necessary methods for a ConfigObject field's type"""

    @classmethod
    def from_config(cls, config_value: Any) -> T:
        """A constructor for this object if the value we are using comes from configuration"""
        ...


class ConfigObject[T: ConfigObjectType](ConfigurationField):
    """A custom object field allowing you to write arbitrary objects that are supported by the writer you are using.
    This can also be used for objects that implement writer-specific magic-methods.

    These include:
        - `__write_toml_value__(field, value) -> str` (writing a regular toml-parsable value as a string)
        - `__write_toml_full__(field, value) -> str` (Directly write line(s) of toml when encountering this object)
        - `__write_json_value__(field, value) -> int | float | datetime | str | None` \
            (When encountering this object- convert it to a json serializable format)
    """

    __slots__ = "_type"
    __match_args__ = ("_type", "_by_name")

    _holds: T

    _type: Type[T]
    """The object type"""

    def __init__(
        self,
        _type: Type[T],
        default_value: T | _NoDefaultValueT = NoDefaultValue,
        /,
        *args,
        **kwargs,
    ):
        self._type = _type
        return super().__init__(default_value, *args, **kwargs)

    def get_value(self, value: Any):
        if isinstance(value, self._type):
            return value
        return self.__call__(value)

    def __call__(self, value: Any):
        if isinstance(value, self._type):
            return value
        return self._type.from_config(value)

    @overload
    def __get__(self, instance: None, owner) -> Self: ...

    @overload
    def __get__(self, instance: "Section", owner) -> T: ...

    def __get__(self, instance: "Section | None", owner) -> T | Self:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: T | Any):
        if isinstance(value, self._type):
            return super().__set__(instance, value)
        super().__set__(instance, self.get_value(value))

    def _validate_value(self, value: Any, name: str | None = None, /):
        if isinstance(value, self._type):
            super()._validate_value(value, name)
        super()._validate_value(self.get_value(value), name)


__all__ = [
    "ConfigurationField",
    "NoDefaultValue",
    "_NoDefaultValueT",
    "Section",
    "Boolean",
    "Float",
    "Integer",
    "Number",
    "Text",
    "Table",
    "TableSpec",
    "List",
    "PathField",
    "ConfigEnum",
    "ConfigObject",
]
