import enum

import pytest

import comprehensiveconfig
from tests.conftest import OUTPUT_DIR, parameterize_values, toml_config


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_blank_spec_create(filename, writer):
    class Foo(comprehensiveconfig.ConfigSpec, auto_load=False):
        """Basic config"""

        pass

    assert True


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_blank_spec_create_auto_load_failure(filename, writer):
    try:

        class Foo(comprehensiveconfig.ConfigSpec, auto_load=True):
            """Basic config"""

            pass

        assert False
    except ValueError:
        type Foo = object
        assert True


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_blank_spec_create_auto_load_working(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        pass

    assert True


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_int_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        test = comprehensiveconfig.spec.Integer(10)

    assert Foo.test == 10
    Foo.test = 11
    assert Foo.test == 11

    try:
        Foo.test = 12.12
        assert False
    except ValueError:
        assert Foo.test == 11


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_float_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        test = comprehensiveconfig.spec.Float(10.12)

    assert Foo.test == 10.12
    Foo.test = 11
    assert Foo.test == 11

    try:
        Foo.test = "chumpus"
        assert False
    except ValueError:
        assert Foo.test == 11


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_text_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        test = comprehensiveconfig.spec.Text("clean")

    assert Foo.test == "clean"
    Foo.test = "bean"
    assert Foo.test == "bean"

    try:
        Foo.test = 12
        assert False
    except ValueError:
        assert Foo.test == "bean"


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_list_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        test = comprehensiveconfig.spec.List(
            ["12", "13", "14"], inner_type=comprehensiveconfig.spec.Text()
        )

    assert Foo.test == ["12", "13", "14"]
    Foo.test = ["fee", "fi", "foh"]
    assert Foo.test == ["fee", "fi", "foh"]

    try:
        Foo.test = ["fee", 0, "foh"]
        assert False
    except ValueError:
        assert Foo.test == ["fee", "fi", "foh"]

    try:
        Foo.test = "hi"
        assert False
    except ValueError:
        assert Foo.test == ["fee", "fi", "foh"]


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_table_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        test = comprehensiveconfig.spec.Table(
            {"x": 12, "y": 23},
            key_type=comprehensiveconfig.spec.Text(),
            value_type=comprehensiveconfig.spec.Float(),
        )

    assert Foo.test == {"x": 12, "y": 23}
    Foo.test = {"x": 12, "y": 23, "we": 123}
    assert Foo.test == {"x": 12, "y": 23, "we": 123}

    try:
        Foo.test = {"x": 12, "y": [], "we": 123}
        assert False
    except ValueError:
        assert Foo.test == {"x": 12, "y": 23, "we": 123}

    try:
        Foo.test = "hi"
        assert False
    except ValueError:
        assert Foo.test == {"x": 12, "y": 23, "we": 123}


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_section_empty_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section):
            pass

    assert isinstance(Foo.Bar, Foo.Bar.__class__)


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_section_empty_w_name_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section, name="burger"):
            pass

    assert Foo.Bar.__class__._name == "burger"
    assert isinstance(Foo.Bar, Foo.Bar.__class__)


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_section_w_field_w_name_field_auto_create(filename, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section, name="burger"):
            test = comprehensiveconfig.spec.Text("clean")

    assert Foo.Bar.__class__._name == "burger"
    assert isinstance(Foo.Bar, Foo.Bar.__class__)

    assert Foo.Bar.test == "clean"
    Foo.Bar.test = "bean"
    assert Foo.Bar.test == "bean"

    try:
        Foo.Bar.test = 12
        assert False
    except ValueError:
        assert Foo.Bar.test == "bean"


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_enum(filename, writer):
    class ExampleEnum(enum.Enum):
        example = 10
        something_cool = 20

    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        bar = comprehensiveconfig.spec.ConfigEnum(ExampleEnum, ExampleEnum.example)
        baz = comprehensiveconfig.spec.ConfigEnum(
            ExampleEnum, ExampleEnum.example, by_name=True
        )

    assert Foo.bar == ExampleEnum.example
    Foo.bar = ExampleEnum.something_cool
    assert Foo.bar == ExampleEnum.something_cool

    assert Foo.baz == ExampleEnum.example
    Foo.baz = ExampleEnum.something_cool
    assert Foo.baz == ExampleEnum.something_cool

    try:
        Foo.bar = 12.20
        assert False
    except ValueError:
        assert Foo.bar == ExampleEnum.something_cool

    try:
        Foo.baz = 12.20
        assert False
    except ValueError:
        assert Foo.baz == ExampleEnum.something_cool


@pytest.mark.parametrize(("filename", "writer"), [toml_config])
def test_comments_appear_in_output(filename: str, writer):
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section, name="burger"):
            """Section comment example"""

            test = comprehensiveconfig.spec.Text("clean", doc="Example doc 1")

        test2 = comprehensiveconfig.spec.Text(
            "clean", doc="Example doc 2", inline_doc=False
        )

    toml_output: str = writer.dumps(Foo._INST)
    assert toml_output

    assert toml_output.startswith("# ")
    assert "[burger]\n# Section comment example\n" in toml_output
    assert "\n# Example doc 2\n" in toml_output  # ensure this exists and is not inlined
    assert '"clean"  # Example doc 1' in toml_output  # ensure exists and *is* inlined


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_trailing_spaces(filename: str, writer):
    """ensure final outputs have NO trailing spaces"""

    class ExampleEnum(enum.Enum):
        example = 10
        something_cool = 20

    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=writer,
        default_file=filename,
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section, name="burger"):
            """Section comment example"""

            test_section_item = comprehensiveconfig.spec.Text(
                "clean", doc="Example doc 1"
            )

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

    output: str = writer.dumps(Foo._INST)
    assert output

    for line in output.split("\n"):
        assert not line.endswith(" "), f'"{line}"'
