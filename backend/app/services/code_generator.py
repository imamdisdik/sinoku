import secrets
import string
from datetime import datetime

_ALPHABET = string.ascii_uppercase + string.digits


def generate_anonymous_code(year: int | None = None) -> str:
    """Generate kode anonim format SIN-YYYY-XXXX menggunakan CSPRNG."""
    y = year or datetime.now().year
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(4))
    return f"SIN-{y}-{suffix}"
