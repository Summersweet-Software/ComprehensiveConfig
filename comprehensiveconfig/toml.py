import enum
import tomllib
from typing import Any
from . import configio
from . import spec

char_escape_table = {
    "\n": "\\n",
    "\t": "\\t",
    "\r": "\\r",
    '"': '\\"',
    "'": "\\'",
}


def _escape_char(char: str) -> str:
    char = char_escape_table.get(char, char)
    if 8 >= ord(char) >= 0 or 10 >= ord(char) >= 31 or ord(char) == 127:
        return f"\\u{ord(char)}"
    return char


def escape(value: str) -> str:
    return "".join(_escape_char(char) for char in value)


def full_section_name(node) -> list[str]:
    if node._parent is None:
        return [node._name]
    return [*full_section_name(node._parent), node._name]


class TomlWriter(configio.ConfigurationWriter):
    @classmethod
    def dump_section(cls, node) -> list[str]:
        """Dump a spec.Section node and return a list of output lines."""
        if " " in node._name:
            raise ValueError(node._name)

        # "base" is all the junk/lines at the beginning of our section.

        if node._parent is not None:
            base = [f"\n[{'.'.join(full_section_name(node)[1:])}]"]
        else:
            base = []

        if node.__doc__:
            for line in node.__doc__.split("\n"):
                base.append(f"# {line}")

        sorted_values: dict[int, dict[spec.ConfigurationField, Any]] = {}
        for name, value in node._value.items():
            field = node._ALL_FIELDS[name]
            if field._sorting_order not in sorted_values.keys():
                sorted_values[field._sorting_order] = {}
            sorted_values[field._sorting_order][field] = value

        return [
            *base,  # dump all base lines
            *(  # append all of these dumped fields as lines
                (
                    "\n".join(cls.dump_section(value))
                    if isinstance(value, spec.Section)
                    else cls.dump_field(field, value)
                )
                for sub_dict in sorted_values.values()
                for field, value in sub_dict.items()
            ),
        ]

    @classmethod
    def format_value(cls, field, value) -> str:
        """Format individual values into properly represented strings of valid toml values."""
        match value:
            case int() | float():
                return str(value)
            case str():
                return f'"{escape(value)}"'
            case list():
                return f"[{", ".join([str(cls.format_value(field, inner_val)) for inner_val in value])}]"
            case dict():
                return f"{{ {", ".join([f"{key} = {cls.format_value(field, inner_val)}" for key, inner_val in value.items()])} }}"
            case enum.Enum():
                return f"{cls.format_value(field, value.value)}"
            case _:
                # magic method to make writing new field types possible
                if hasattr(value, "__write_toml_value__"):
                    return str(value.__write_toml_value__(field, value))
                # No known way exists to write this field:
                raise ValueError(value)

    @classmethod
    def dump_table(cls, table_node: spec.Table, value) -> str:
        for name, val in value.items():
            if not isinstance(val, spec.Section):
                continue
            val._name = name
            val._parent = table_node

        section_name = ".".join(full_section_name(table_node)[1:])

        return f"\n[{section_name}]\n{"\n".join(cls.dumps(val) for key, val in value.items())}"

    @classmethod
    def create_basic_field_doc(cls, field: spec.ConfigurationField) -> str:
        """generates our basic field_doc"""
        if field._inline_doc and field.doc:
            doc_comment = "  "
        elif field.doc:
            doc_comment = "\n"
        else:
            return ""

        return doc_comment + f"# {"\n# ".join(field.doc.split("\n"))}"

    @classmethod
    def dump_enum(cls, field: spec.ConfigEnum, value):
        if isinstance(value, spec.Section):
            return "\n".join(cls.dump_section(value))

        by_name = field._by_name
        field_doc = "  " if field._inline_doc and field.doc else "\n"

        if field.doc:
            field_doc += f"# {"\n# ".join(field.doc.split("\n"))}"

        if field._enum.__doc__:
            delimeter = "\n##  - "
            doc_comment = f"# {"\n# ".join(field._enum.__doc__.split("\n"))}\n#"
        else:
            delimeter = "\n#  - "
            doc_comment = ""

        doc_comment += f"# Available Options for {field._name}:{delimeter}"
        if by_name:
            doc_comment += delimeter.join(
                member for member in field._enum.__members__.keys()
            )
            return f"{field._name} = {cls.format_value(field, value.name)}{field_doc}\n{doc_comment}"
        doc_comment += delimeter.join(
            str(member.value) for member in field._enum.__members__.values()
        )
        return f"{field._name} = {cls.format_value(field, value.value)}{field_doc}\n{doc_comment}"

    @classmethod
    def dump_field(cls, field: spec.AnyConfigField, value) -> str:
        """dump a field object given its value"""
        match field:
            case spec.Table(spec.Text(), type() | spec.ConfigUnion()) as table_node:
                return cls.dump_table(table_node, value)
            case spec.Section():
                return "\n".join(cls.dump_section(field))
            case spec.ConfigEnum(_, by_name):
                return cls.dump_enum(field, value)
            case spec.ConfigurationField():
                # magic method to make writing new field types possible
                if hasattr(field, "__write_toml_full__"):
                    return str(value.__write_toml_full__(field, value))

                if isinstance(value, spec.Section):
                    return "\n".join(cls.dump_section(value))

                return f"{field._name} = {cls.format_value(field, value)}{cls.create_basic_field_doc(field)}"
            case _:
                # magic method to make writing new field types possible
                if hasattr(field, "__write_toml_full__"):
                    return str(value.__write_toml_full__(field, value))
                # No known way exists to write this field:
                raise ValueError(field)

    @classmethod
    def dumps(cls, node) -> str:
        match node:
            case spec.Section():
                return "\n".join(cls.dump_section(node))
            case spec.ConfigurationField():
                # Dump passed in node to the best of our ability. This typically looks like dumping its default value
                if not node._has_default:
                    raise ValueError("Node does not have a default value")
                return cls.dump_field(
                    node,
                    node._default_value,
                )
            case _:
                raise ValueError(node)

    @classmethod
    def dump(cls, file, node):
        super().dump(file, node)

    @classmethod
    def load(cls, file):
        if isinstance(file, str):
            with open(file, "rb") as f:
                return tomllib.load(f)
        return tomllib.load(file)

    @classmethod
    def loads(cls, data: str) -> dict[str, Any]:
        return tomllib.loads(data)
