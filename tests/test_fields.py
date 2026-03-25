import comprehensiveconfig
from tests.conftest import OUTPUT_DIR


def test_blank_spec_create():
    class Foo(comprehensiveconfig.ConfigSpec, auto_load=False):
        """Basic config"""

        pass

    assert True


def test_blank_spec_create_auto_load_failure():
    try:

        class Foo(comprehensiveconfig.ConfigSpec, auto_load=True):
            """Basic config"""

            pass

        assert False
    except ValueError:
        type Foo = object
        assert True


def test_blank_spec_create_auto_load_working():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
        create_file=True,
    ):
        """Basic config"""

        pass

    assert True


def test_int_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
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


def test_float_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
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


def test_text_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
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


def test_list_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
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


def test_table_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
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


def test_section_empty_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section):
            pass

    assert isinstance(Foo.Bar, Foo.Bar.__class__)


def test_section_empty_w_name_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
        create_file=True,
    ):
        """Basic config"""

        class Bar(comprehensiveconfig.spec.Section, name="burger"):
            pass

    assert Foo.Bar.__class__._name == "burger"
    assert isinstance(Foo.Bar, Foo.Bar.__class__)


def test_section_w_field_w_name_field_auto_create():
    class Foo(
        comprehensiveconfig.ConfigSpec,
        auto_load=True,
        writer=comprehensiveconfig.toml.TomlWriter,
        default_file=OUTPUT_DIR + "/test.toml",
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
