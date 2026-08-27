"""PSZ – Encrypted project archive format.

Load a .psz with its paired .psz-data.lor (key file).

Example::

    from psz import open_archive, list_archive_members, create_archive
    from pathlib import Path

    open_archive(Path("demo.psz"), Path("demo.psz-data.lor"), Path("out"))
"""

from .core import (
    SUPPORTED_LANGUAGES,
    create_archive,
    list_archive_members,
    open_archive,
)

__version__ = "1.0.9beta"
__all__ = [
    "__version__",
    "SUPPORTED_LANGUAGES",
    "create_archive",
    "open_archive",
    "list_archive_members",
]
