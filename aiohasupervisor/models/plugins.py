"""Models for plugins."""

from enum import StrEnum


class Plugin(StrEnum):
    """Plugin managed by Supervisor."""

    AUDIO = "audio"
    CLI = "cli"
    DNS = "dns"
    MULTICAST = "multicast"
    OBSERVER = "observer"
