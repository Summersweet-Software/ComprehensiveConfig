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
    Foo.test = 11  # manually set instance value
    assert Foo.test == 11

    try:
        Foo.test = 12.12
        assert Foo.test == 11
    except ValueError:
        assert Foo.test == 11
