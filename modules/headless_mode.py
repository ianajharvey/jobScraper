import os

def get_headless_mode():
    """
    Returns True for headless (CI / GitHub),
    False for local debugging.
    """
    env = os.getenv("JOBSCRAPER_ENV", "local").lower()

    # GitHub Actions always runs headless
    if env == "github":
        return True

    # Local default: headed
    return False
