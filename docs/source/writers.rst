Config Writers
================

.. py:currentmodule:: comprehensiveconfig.configio



Config writers are what ComprehensiveConfig uses to load and dump configuration objects.
These are a basic interface that can be extended and used for any format!



Module
********

.. py:class:: ConfigurationWriter
    :abstract:

    .. py:method:: dumps(cls, node: spec.AnyConfigField) -> str
        :abstract:
        :classmethod:

        :param AnyConfigField node: The configuration object we are writing.

        Dumps a string output from a given config

    .. py:method:: dump(cls, file, node: spec.AnyConfigField)
        :abstract:
        :classmethod:

        :param file: The file name or object we are writing to.
        :param AnyConfigField node: The configuration object we are writing.

        Dumps a to a configuration section to a given file

    .. py:method:: loads(cls, data: str) -> dict[str, Any]
        :abstract:
        :classmethod:

        :param str data: The configuration object we are writing.

        Load the given configuration string as

        .. :important::

            Output is not validated. This is done by the configuration fields themselves.
            This should not be used directly unless necessary.

    .. py:method:: load(cls, file) -> dict[str, Any]
        :abstract:
        :classmethod:

        :param file: The file name or object we are writing to.

        Load a given file and create a configuration object

        .. :important::

            Output is not validated. This is done by the configuration fields themselves.
            This should not be used directly unless necessary.