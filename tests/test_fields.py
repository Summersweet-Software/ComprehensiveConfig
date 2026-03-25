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
