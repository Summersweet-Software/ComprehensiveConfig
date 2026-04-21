Toml Writer
=============

.. py:currentmodule:: comprehensiveconfig.toml


This ConfigWriter adds Toml export and import support.

Module
********

.. py:class:: TomlWriter

    .. py:classmethod:: dumps(cls, node) -> str

        :param AnyConfigField node: The configuration object we are writing.

        Dumps a string output from a given config

    .. py:classmethod:: dump(cls, file, node) -> str

        :param file: The file name or object we are writing to.
        :param AnyConfigField node: The configuration object we are writing.

        Dumps a to a configuration section to a given file

    .. py:classmethod:: loads(cls, data: str)

        :param str data: The configuration object we are writing.

        Load the given configuration string as

        .. :important::

            Output is not validated. This is done by the configuration fields themselves.
            This should not be used directly unless necessary.

    .. py:classmethod:: load(cls, file)

        :param file: The file name or object we are writing to.

        Load a given file and create a configuration object

        .. :important::

            Output is not validated. This is done by the configuration fields themselves.
            This should not be used directly unless necessary.

    Private Methods
    -----------------

    .. py:classmethod:: dump_section(cls, node) -> list

        :meta private:
        :param node: The :py:class:`comprehensiveconfig.spec.Section` instance being dumped

        Dumps a section to a list of lines to write

    .. py:classmethod:: format_value(cls, value) -> str

        :meta private:
        :param value: The object we are formatting into valid toml.

        Dump a value or node into the appropriate formatting for toml.

    .. py:classmethod:: dump_field(cls, node: spec.AnyConfigField, original_name: str, field_name: str, value) -> str

        :meta private:
        :param AnyConfigField node: The parent node containing this field
        :param str original_name: Name of the python class attribute attributed to the field
        :param str field_name: The true field name being used (this could be mutated)
        :param value: The value of this field

        Dump a field into valid toml
