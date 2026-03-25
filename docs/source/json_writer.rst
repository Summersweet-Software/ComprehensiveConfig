Json Writer
=============

.. py:currentmodule:: comprehensiveconfig.json


This ConfigWriter adds Json export and import support.

Module
********

.. py:class:: JsonWriter

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

    .. py:classmethod:: dump_section(cls, node: spec.Section)

        :param node: The section we are dumping

        dump a section into json format. Running through each k/v pair and ensuring properly json serializable.

    .. py:classmethod:: dump_value(cls, node: spec.AnyConfigField, value)

        :param node: The node of the value we are dumping
        :param value: The value of the node we are dumping.

        Dump a field value as json serializable object.