import comprehensiveconfig.validators as validators


def test_run_passing_unix_validator():
    assert validators.validate_path_unix(
        'some/kind-of/example..../*/1234567890/?&^%$#@!!!<>":: \n  []{}/test.txt'
    )


def test_run_failing_unix_validator():
    assert not validators.validate_path_unix(
        'some/kind-of/example..../*/1234567890/?&^%$#@!!!<>":: \n  []{}/test.txt\x00'
    )


# * windows
def test_run_passing_windows_validator():
    assert validators.validate_path_windows("D:/Windows/System32/WoahThatsCool.md")

    assert validators.validate_path_windows(
        "\\\\?\\D:/Windows/System32/WoahThatsCool.md"
    )
    assert validators.validate_path_windows(
        "\\\\.\\D:/Windows/System32/WoahThatsCool.md"
    )

    assert validators.validate_path_windows("/Windows/System32/WoahThatsCool.md")
    assert validators.validate_path_windows("/Windows/System32/WoahThatsCool.md/")
    assert validators.validate_path_windows("//Windows/System32/WoahThatsCool.md/")
    assert validators.validate_path_windows("//Windows/System32/WoahThatsCool.md/../")
    assert validators.validate_path_windows("//Windows/System32/WoahThatsCool.md/.././")
    assert validators.validate_path_windows(
        "//Windows/System32/WoahThatsCool.md/.././   x"
    )


def test_run_failing_windows_validator():
    # trailing spaces
    assert not validators.validate_path_windows(
        "D:/Windows/System32   /WoahThatsCool.md"
    )
    assert not validators.validate_path_windows(
        "D:/Windows/System32/WoahThatsCool.md    "
    )

    # invalid chars
    assert not validators.validate_path_windows("D:/Windows/System32/WoahThatsCool<.md")
    assert not validators.validate_path_windows("D:/Windows/System32/WoahThatsCool>.md")
    assert not validators.validate_path_windows('D:/Windows/System32/WoahThatsCool".md')
    assert not validators.validate_path_windows("D:/Windows/System32/WoahThatsCool?.md")
    assert not validators.validate_path_windows("D:/Windows/System32/WoahThatsCool*.md")
    assert not validators.validate_path_windows(
        "D:/Windows/System32/WoahThatsCool.md\n"
    )
    assert not validators.validate_path_windows(
        "D:/Windows/System32/WoahThatsCool.md\t"
    )
    assert not validators.validate_path_windows(
        "D:/Windows/System32/WoahThatsCool.md\x00"
    )

    # single/leading colon
    assert not validators.validate_path_windows(":/Windows/System32/WoahThatsCool.md")
    assert not validators.validate_path_windows(
        "/balls/:er/Windows/System32/WoahThatsCool.md"
    )
    assert not validators.validate_path_windows(
        "/balls/:/Windows/System32/WoahThatsCool.md"
    )

    # illegal names
    assert not validators.validate_path_windows(
        "D:/Windows/System32/WoahThatsCool.md/CON/"
    )

    # individual folder/file name too large
    assert not validators.validate_path_windows("C:/Windows/" + "x" * 256)

    # path too long
    assert not validators.validate_path_windows("x" * 32_768)

    # trailing dots
    assert not validators.validate_path_windows(
        "D:/Windows/System32/WoahThatsCool.md/thing./"
    )
