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
    def dump_section(cls, node) -> list:
        if " " in node._name:
            raise ValueError(node._name)

        if node._parent is not None:
            base = [f"\n[{'.'.join(full_section_name(node)[1:])}]"]
        else:
            base = []

        if node.__doc__:
            for line in node.__doc__.split("\n"):
                base.append(f"# {line}")

        sorted_values: dict[int, dict[str, Any]] = {}
        for name, value in node._value.items():
            field = node._ALL_FIELDS[name]
            if field._sorting_order not in sorted_values.keys():
                sorted_values[field._sorting_order] = {name: value}
                continue
            sorted_values[field._sorting_order][name] = value

        return [
            *base,
            *(
                (
                    "\n".join(cls.dump_section(value))
                    if isinstance(value, spec.Section)
                    else cls.dump_field(node, name, node._FIELD_VAR_MAP[name], value)
                )
                for sub_dict in sorted_values.values()
                for name, value in sub_dict.items()
            ),
        ]

    @classmethod
    def format_value(cls, value):
        match value:
            case int() | float():
                return str(value)
            case str():
                return f'"{escape(value)}"'
            case list():
                return f"[{", ".join([str(cls.format_value(inner_val)) for inner_val in value])}]"
            case dict():
                return f"{{ {", ".join([f"{key} = {cls.format_value(inner_val)}" for key, inner_val in value.items()])} }}"
            case enum.Enum():
                return f"{cls.format_value(value.value)}"
            case _:
                raise ValueError(value)

    @classmethod
    def dump_field(
        cls, node: spec.AnyConfigField, original_name: str, field_name: str, value
    ) -> str:
        if isinstance(node, spec.Section):
            field = node.get_field(original_name)
        else:
            field = node
        match field:
            case spec.Table(spec.Text(), type() | spec.ConfigUnion()) as table_node:
                for name, val in value.items():
                    if not isinstance(val, spec.Section):
                        continue
                    val._name = name
                    val._parent = table_node

                section_name = ".".join(full_section_name(table_node)[1:])

                return f"\n[{section_name}]\n{"\n".join(cls.dumps(val) if isinstance(val, spec.Section) else cls.dump_field(val, key, key, val) for key, val in value.items())}"
            case spec.Section():
                return "\n".join(cls.dump_section(node))
            case spec.ConfigEnum(_, by_name):
                if isinstance(value, spec.Section):
                    return "\n".join(cls.dump_section(value))

                field_doc = "  " if field._inline_doc else "\n"

                if field.doc:
                    field_doc += f"# {"\n# ".join(field.doc.split("\n"))}"

                if field._enum.__doc__:
                    delimeter = "\n##  - "
                    doc_comment = f"# {"\n# ".join(field._enum.__doc__.split("\n"))}\n#"
                else:
                    delimeter = "\n#  - "
                    doc_comment = ""

                doc_comment += f"# Available Options for {field_name}:{delimeter}"
                if by_name:
                    doc_comment += delimeter.join(
                        member for member in field._enum.__members__.keys()
                    )
                    return f"{field_name} = {cls.format_value(value.name)}{field_doc}\n{doc_comment}"
                doc_comment += delimeter.join(
                    str(member.value) for member in field._enum.__members__.values()
                )
                return f"{field_name} = {cls.format_value(value.value)}{field_doc}\n{doc_comment}"
            case _:
                if isinstance(value, spec.Section):
                    return "\n".join(cls.dump_section(value))
                real_field = node._ALL_FIELDS[original_name]
                doc_comment = "  " if real_field._inline_doc else "\n"

                if real_field.doc:
                    doc_comment += f"# {"\n# ".join(real_field.doc.split("\n"))}"
                return f"{field_name} = {cls.format_value(value)}{doc_comment}"

    @classmethod
    def dumps(cls, node) -> str:
        match node:
            case spec.Section():
                return "\n".join(cls.dump_section(node))

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

    # just alias the name
    loads = tomllib.loads
