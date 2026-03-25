Fields
=======

.. py:currentmodule:: comprehensiveconfig.spec



Fields are the most basic unit in Comprehensive Config. They are used to define named values in your configuration file.

For example- in toml:

.. code-block:: TOML

    x = "foo"

Module
*******

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

    :param T | _NoDefaultValueT default_value: The default value used for this configuration file
    :param str name: The name of the field in our configuration file
    :param bool nullable: Defines if the value of the field can be :py:const:`None`
    :param str | None doc: The documentation/comment for this field (only exported in config formats that support comments)
    :param bool inline_doc: Defines if the doc comment is on the same line as the field


    Abstract base class for all configuration fields

    .. py:method:: def _validate_value(self, value: Any, name: str | None = None, /):
        :abstractmethod:

        :param value: The value we are validating
        :param name: The transformed name of the field (used in error messages)

        The in-built validator for a given field.

    .. py:attribute:: _holds
        :type: T

        The type of data this field holds (used purely for annotation and IDE static type checking)

    .. py:attribute:: _name
        :type: str

        The actual name used inside of your configuration file

    .. py:attribute:: _default_value
        :type: T | NoDefaultValue

        The actual name used inside of your configuration file

    .. py:attribute:: _has_default
        :type: bool

    .. py:attribute:: _nullable
        :type: bool

    .. py:attribute:: doc
        :type: str | None
        :value: None

        A doc comment added for configuration formats that support it

    .. py:attribute:: inline_doc
        :type: bool
        :value: True

        Whether a doc comment should be rendered on the same line as the field (on formats that support comments)

.. py:class:: comprehensiveconfig.spec.Integer(*args, **kwargs)

    .. py:attribute:: _holds
        :type: int

.. py:class:: comprehensiveconfig.spec.Float(*args, **kwargs)

    .. py:attribute:: _holds
        :type: float | int

.. py:class:: comprehensiveconfig.spec.Text(*args, regex: str = r".*", **kwargs)

    :param str regex: Defines a regex pattern to validate against. Useful for email fields, ips, and other structured data.

    .. py:attribute:: _holds
        :type: float | int


.. py:class:: comprehensiveconfig.spec.List[T](default_value: list[T] = [], /, inner_type: AnyConfigField | None = None, **kwargs)

    :param list[T] default_value: The default value of the field. This always default to an empty list (required for static type checking)
    :param AnyConfigField | None inner_type: The inner type used in the list. This is any field in the spec. This allows you to further validate the inner data.

    .. py:attribute:: _holds
        :type: list[T]

    .. note::

        Might require manual annotation if your default value remains an empty list

.. py:class:: comprehensiveconfig.spec.Table[K, V](default_value: dict[K, V] = {}, /, key_type: AnyConfigField | None = None, value_type: AnyConfigField | None = None, **kwargs)

    :param list[T] default_value: The default value of the field. This always default to an empty dict (required for static type checking)
    :param AnyConfigField | None key_type: The type of the keys used in the dict. This is any field in the spec. This allows you to further validate the inner data.
    :param AnyConfigField | None value_type: The type of the values used in the dict. This is any field in the spec. This allows you to further validate the inner data.

    .. py:attribute:: _holds
        :type: list[T]

    .. note::

        Might require manual annotation if your default value remains an empty dict

.. py:class:: comprehensiveconfig.spec.TableSpec(cls, name: str | None = None, **kwargs)

    .. important::
        This is meant to only be used as a baseclass. The arguments provided above are for subclassing
        usage:


        .. code-block:: python

            class MySpec(TableSpec, name="Something"):
                '''Instantiate to create a field'''
                pass

    .. py:method:: __init__(self, default_value: dict | NoDefaultValue = NoDefaultValue, /, *args, **kwargs)

        :param dict | NoDefaultValue default_value: Default Value for a field of this type.

.. py:class:: comprehensiveconfig.spec.Section(cls, name: str | None = None, **kwargs)

    .. important::
        This is meant to only be used as a baseclass. The arguments provided above are for subclassing
        usage:


        .. code-block:: python

            class SomeSection(Section, name="Something"):
                pass

    .. py:attribute:: _FIELDS
        :type: dict[str, AnyConfigField]

    .. py:attribute:: _SECTIONS
        :type: dict[str, Type]

    .. py:attribute:: _ALL_FIELDS
        :type: dict[str, AnyConfigField | Type]

    .. py:attribute:: _FIELD_NAME_MAP
        :type: dict[str, str]

    .. py:attribute:: _FIELD_VAR_MAP
        :type: dict[str, str]

    .. py:attribute:: _cls_name
        :type: str

    .. py:attribute:: _instance_name
        :type: str

    .. py:attribute:: _has_default
        :type: bool

    .. py:attribute:: _default_value
        :type: dict[str, Any] | _NoDefaultValueT

    .. py:attribute:: _parent
        :type: SectionParent

    .. py:attribute:: _instance_parent
        :type: AnyConfigField | None

    .. py:attribute:: _cls_parent
        :type: AnyConfigField | None


.. py:class:: comprehensiveconfig.spec.ConfigUnion[L, R](left_type: AnyConfigField | Type, right_type: AnyConfigField | Type, *args, **kwargs,)

    .. important::
        This should not be instantiated directly! Instead do the following:


        .. code-block:: python

            Integer() | Text(regex="...")

        Also important to note that validation is done Left-to-Right. That means it will always try to match against the left-most types first

    .. py:attribute:: _holds
        :type: L | R

.. py:class:: comprehensiveconfig.spec.ConfigEnum[T](enum_type: Type[T], default_value: T | _NoDefaultValueT = NoDefaultValue, /, *args, by_name=False, **kwargs)

    :param Type[T] enum_type: The class of the enum we want to represent in this field.
    :param T | NoDefaultValue default_value: Default value of our field
    :param bool by_name: Choose whether or not we should have variants use their value's or their name's when we validate configuration.

    This is a way to use an existing python enum (:py:class:`enum.Enum`) as a validated field.

    .. py:attribute:: _holds
        :type: T

    .. py:attribute:: _enum_type
        :type: Type[T]

    .. py:attribute:: _enum_members_reversed
        :type: dict[Any, T]

        A reversed mapping of values and enum variants (instances) in the enumeration type
