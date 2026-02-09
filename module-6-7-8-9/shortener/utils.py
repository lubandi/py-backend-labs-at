import random
import string


def generate_short_code(length=6):
    """
    Generate a random alphanumeric string of fixed length.
    """
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
