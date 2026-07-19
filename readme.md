[![PyPI - Downloads](https://img.shields.io/pypi/dm/comprehensiveconfig?style=for-the-badge)](https://pypi.org/project/comprehensiveconfig/)

# Comprehensive Configuration

A simple configuration library that lets you create a pydantic-like model for your configuration.

# Autoloaded Configuration Classes (Typing Issues in Mypy)

There is one particular pitfall I have yet to develop around. Mypy is missing a few essential checks that improve type checking on autoloaded configuration classes. For the time being, I recommend avoiding using mypy with this project until class-decorator annotations work [(something that hasn't worked since 2017)](https://github.com/python/mypy/issues/3135) or until I can manage to create a mypy plugin to work around the issue. Pyright doesn't seem believe anything is wrong. Pyright is the default typechecker used in vscode's pylance extension.

If type checking issues occur on your autoloaded config classes, try using this temporary decorator as a fix:
```python
@autoloaded # makes your type checker think `MyConfig` is an instance of itself. (or at least it *should* do that.)
class MyConfig(ConfigSpec, default_file="test.toml", writer=TomlWriter, create_file=True):
    ... # impl here
```

The other option is to just manually load your configuration.

```python
class MyConfig(ConfigSpec, auto_load=False):
    ...

config = MyConfig.load("test.toml", TomlWriter, create_file=True) # load and/or create our config file
```

# Installation

`pip install comprehensiveconfig`

# Features

- [x] Supports static type checking
- [x] toml writer
- [x] json writer
- [x] Number fields
- [x] Text fields (with regex filtering)
- [x] File/Folder path fields (`PathField`)
  - [x] Ability to change validator (unix/linux, windows, agnostic, and current system)
  - [x] Validate for only files, folder, or accept both.
- [x] List fields
- [x] Table fields
- [x] TableSpec (Model) fields
- [x] Sections
- [x] Include doc comments in Section
- [x] auto loading
- [x] initialize default config (with auto loader)
- [N/a] yaml writer (This will likely be moved to a different library as an extension of comprehensiveconfig!)
- [ ] Tests targetting mypy and other static type checkers to ensure EVERYTHING looks good across IDE's
- [x] section list (via a Table field)
- [x] Field type unions (overwriting normal union syntax)
- [x] per attribute doc comments (inline and noninline)
- [x] enum support (Via `spec.ConfigEnum` and python's `enum.Enum`)
- [x] fully supported string escapes

# Example (Python)

```python
# example.py
from comprehensiveconfig import ConfigSpec
from comprehensiveconfig.spec import Section, Integer, Float, Text, List
from comprehensiveconfig.toml import TomlWriter

class MyConfigSpec(ConfigSpec,
                   default_file="myconfig.toml",
                   writer=TomlWriter,
                   create_file=True):
    class MySection(Section, name="My_Section"):
        some_field = Integer(10)
        other_field = Text("Some Default Text")

        class SubSection(Section):
            '''An example Sub Section'''
            x = Integer(10)

    class Credentials(Section):
        '''Example credentials section'''
        email = Text("example@email.com", regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        password = Text("MyPassword")

    some_field = Float(6.9)
    list_of_stuff = List(["12", "13", "14"], inner_type=Text())


# Accessing values from globally loaded config (if one exists, otherwise it accesses the actual Field class)
print(MyConfigSpec.some_field)
print(MyConfigSpec.MySection.other_field)

# Another way to open configuration
second_config = MyConfigSpec.load("another_config.toml", TomlWriter)
```

# Example (toml output)

```toml
some_field = 6.9
list_of_stuff = ["12", "13", "14"]

[My_Section]
some_field = 10
other_field = "Some Default Text"

[My_Section.SubSection]
# An example Sub Section
x = 10

[Credentials]
# Example credentials section
email = "example@email.com"
password = "MyPassword"
```
