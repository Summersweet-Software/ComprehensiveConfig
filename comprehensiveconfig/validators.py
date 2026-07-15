"""Additional validators used in more specialty field classes"""

import sys

# unix
NULL_BYTE = "\x00"
# windows
DEVICE_PATH_PREFIX = "\\\\?\\"
DEVICE_PATH_NORMALIZED_PREFIX = "\\\\.\\"
BANNED_WINDOWS_NAMES = (
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM0",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT0",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
)


def validate_path_unix(path: str) -> bool:
    """Takes in a str filepath and validates whether or not it is valid on unix/linux"""
    return NULL_BYTE not in path


def validate_path_windows(path: str) -> bool:
    """Takes in a str filepath and validates whether or not it is valid on windows.
    Allows absolute, relative, device, and normalized device paths.
    """

    # Start seperating text/tokenize it into sections for verification
    current_text = ""
    tokens: list[str] = []

    if len(path) > 32_767:  # Maximum path size check
        return False

    if path.startswith(DEVICE_PATH_PREFIX):
        path = path.removeprefix(DEVICE_PATH_PREFIX)

    if path.startswith(DEVICE_PATH_NORMALIZED_PREFIX):
        path = path.removeprefix(DEVICE_PATH_NORMALIZED_PREFIX)

    for char in path:
        if char == "\\" or char == "/":
            if len(current_text) > 0:
                tokens.append(current_text)
            current_text = ""
            continue
        if char == ":":
            if len(current_text) == 0:
                return False
            tokens.append(current_text + char)
            current_text = ""
            continue
        if char in '<>"|?*':
            return False  # all of these are invalid characters.
        if ord(char) <= 31:
            return False
        current_text += char
    tokens.append(current_text)

    # iterate over our tokens and validate them.
    for c, token in enumerate(tokens):
        if ":" in token:  # Disallow use of the colon character
            if (
                token.count(":") == 1 and token.endswith(":") and c == 0
            ):  # only allow a trailing colon on the first token. (drive letter typically)
                continue
            return False
        if token.endswith(".") and token != ".." and token != ".":
            return False
        if len(token) > 255:
            return False
        if token in BANNED_WINDOWS_NAMES:
            return False
        if token.endswith(" "):
            return False
    return True


def validate_path_agnostic(path: str) -> bool:
    """Takes in a str filepath and validates whether or not it is valid on any operating system"""
    return validate_path_unix(path) or validate_path_windows(path)


def validate_path_sys_aware(path: str) -> bool:
    """Takes in a str filepath and validates whether or not it is valid on the *current* operating system"""
    if sys.platform == "win32":
        return validate_path_windows(path)
    else:
        return validate_path_unix(path)


__all__ = [
    "validate_path_unix",
    "validate_path_windows",
    "validate_path_agnostic",
    "validate_path_sys_aware",
]
