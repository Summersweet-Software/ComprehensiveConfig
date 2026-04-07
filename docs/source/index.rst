Comprehensive Config
=====================

.. py:currentmodule:: comprehensiveconfig.json


Comprehensive config is a python configuration library that aims to be extraordinarily pythonic and easy to use.
It takes heavy inspiration from pydantic models.

Comprehensive config includes automatic config file creation and/or
loading as well as complex validators for incoming configuration values.


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Contents:

   self

.. toctree::
   :glob:
   :maxdepth: 3
   :caption: Fields:

   fields.rst


.. toctree::
   :glob:
   :maxdepth: 3
   :caption: Writers:

   writers.rst
   json_writer.rst
   toml_writer.rst

Module
********

.. py:class:: _ConfigSpecMeta(cls, name, bases, attrs, default_file: str | None = None, writer=None, create_file: bool = False, auto_load: bool = True, **kwargs,)

   Used to automatically load config and overwrite get/set attribute methods to allow direct access to data.

   .. py:attribute:: _WRITER
      :type: Type[configio.ConfigurationWriter] | None

   .. py:attribute:: _DEFAULT_FILE
      :type: str | None

   .. py:attribute:: _AUTO_LOAD
      :type: bool

   .. py:attribute:: _CREATE_FILE
      :type: bool

   .. py:attribute:: _INST
      :type: Union["ConfigSpec", None]

.. py:class:: _ConfigSpecABCMeta

   Combines :py:class:`ABCMeta` and :py:class:`_ConfigSpecMeta`

.. py:class:: ConfigSpec(cls, **kwargs)

   .. important::

      Not meant to be used directly: instead subclass and pass :py:class:`_ConfigSpecMeta` keyword arguments.

      .. code-block:: python

         class MyConfig(ConfigSpec, writer=JsonWriter, auto_load=False, ...):
            pass # fields here

   .. py:classmethod:: load(cls, file=None, writer=None, /) -> Self

      Load a specified file (or load default file with default writer)

   .. py:method:: save(file=None, writer=None, /)

      Save a specified file (or save default file with default writer)

   .. py:method:: reset()

      Reset configuration using default values of all fields

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`