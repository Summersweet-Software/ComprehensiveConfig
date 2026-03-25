Fields
=======

Fields are the most basic unit in Comprehensive Config. They are used to define named values in your configuration file.

For example- in toml:

.. code-block:: TOML

    x = "foo"

Code
*****

.. py:module:: comprehensiveconfig.spec

    .. py:data:: NoDefaultValue
        :type: _NoDefaultValueT

        A sentinel value representing that no default value has been provided to some field

    .. py:class:: _NoDefaultValueT

        Non instantiable type for :py:const:`NoDefaultValue`

    .. py:class:: ConfigurationFieldMeta

        .. py:method:: __or__[S, T](self: S, value: Type[T] | T) -> S | Type[T]:

            Overwrite default type union behavior

    .. py:class:: BaseConfigurationField
        :abstract:

        Abstract base class for all configuration fields 

        .. py:method:: def _validate_value(self, value: Any, name: str | None = None, /):
            :abstractmethod:

            The in-built validator for a given field.


    .. py:class:: ConfigurationField[T](default_value: T | _NoDefaultValueT = NoDefaultValue, /, name: str | None = None, nullable: bool = False, doc: None | str = None, inline_doc: bool = True)
        :abstract:

        Abstract base class for all configuration fields 

        .. py:method:: def _validate_value(self, value: Any, name: str | None = None, /):
            :abstractmethod:

            The in-built validator for a given field.

        