Validators
===========

This file primarily contains various validators used throughout the spec.

.. py:currentmodule:: comprehensiveconfig.validators


Module
********

.. py:function:: validate_path_unix(path: str) -> bool

    This function takes a string path and validates whether or not it would be valid on a Unix system.
    This is a simple check to see if the path contains a null byte (:code:`\x00`).

    :param str path: The path as a :bold:`string`. Path objects do not work here!


.. py:function:: validate_path_windows(path: str) -> bool

    This function takes a string path and validates whether or not it would be valid on a windows system.
    This is a muchmore complex function than the one for Unix systems.

    :param str path: The path as a :bold:`string`. Path objects do not work here!


.. py:function:: validate_path_agnostic(path: str) -> bool

    This function checks if a path would be valid on Unix OR Windows. It first runs the check for Unix (its less expensive) before then checking for validity on Windows.

    :param str path: The path as a :bold:`string`. Path objects do not work here!

.. py:function:: validate_path_sys_aware(path: str) -> bool

    Another path validator function but this one determines the system you are currently on before choosing which validator to use.

    :param str path: The path as a :bold:`string`. Path objects do not work here!