import random
import string
from datetime import datetime


def generate_anonymous_code(year: int | None = None) -> str:
    """Generate kode anonim format SIN-YYYY-XXXX."""
    y = year or datetime.now().year
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SIN-{y}-{suffix}"
