import enum
from typing import Type

import comprehensiveconfig


class ExampleEnum(enum.Enum):
    example = 10
    something_cool = 20


class ConfigurationWriterTestCase(
    comprehensiveconfig.ConfigSpec,
    auto_load=False,
    create_file=False,
):
    """A Configuration Spec to be used as a test-case for any user-made config writers."""

    class Bar(comprehensiveconfig.spec.Section, name="burger"):
        """Section comment example"""

        test_section_item = comprehensiveconfig.spec.Text("clean", doc="Example doc 1")

    test_text = comprehensiveconfig.spec.Text(
        "clean", doc="Example doc 2", inline_doc=False
    )
    test_int = comprehensiveconfig.spec.Integer(20)
    test_float = comprehensiveconfig.spec.Float(20.20)
    test_dict = comprehensiveconfig.spec.Table(
        {10: "burgers"},
        key_type=comprehensiveconfig.spec.Integer(),
        value_type=comprehensiveconfig.spec.Text(),
    )
    test_list = comprehensiveconfig.spec.List(
        [10, 20, 30], inner_type=comprehensiveconfig.spec.Integer()
    )

    test_enum_value = comprehensiveconfig.spec.ConfigEnum(
        ExampleEnum, ExampleEnum.example
    )
    test_enum_name = comprehensiveconfig.spec.ConfigEnum(
        ExampleEnum, ExampleEnum.example, by_name=True
    )


def test_writer_dumps(writer: Type[comprehensiveconfig.configio.ConfigurationWriter]):
    """Test the dumps capabilities of a configuration writer"""
    config_value = ConfigurationWriterTestCase(None)

    output: str = writer.dumps(config_value)
    assert output  # ensure an output is created

    for line in output.split("\n"):
        assert not line.endswith(" "), f'"{line}"'  # ensure no trailing whitespace

    # Ensure all nodes are individually writable
    for node in config_value._FIELDS.values():
        assert writer.dumps(node), node
