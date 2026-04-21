Utilities
===========

.. py:currentmodule:: comprehensiveconfig.utility


This module is additional utility functions that are useful for building/extending functionality on top of this library.

.. important::
    This module is NOT included in the `__init__.py` for comprehensiveconfig.

    This means you must import it like this: :code:`import comprehensiveconfig.utility`

Module
********

.. py:function:: test_writer_dumps(writer: Type[ConfigurationWriter])

    :param Type[ConfigurationWriter] writer: The writer we are testing the dumping functionality of.

    Test that a writer is functioning properly.
    This currently means:
        - no trailing whitespace
        - being able to dump ALL node types (Not just :py:class:`comprehensiveconfig.spec.Section`)

    .. warning::

        This is NOT a full test suite. This runs a simple case to ensure that what you are using is *mostly* working.
        This just makes writing smaller custom writer's easier. If you plan to publish a larger writer on pypi or github, then write more tests! 