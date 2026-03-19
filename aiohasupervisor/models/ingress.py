"""Models for ingress APIs."""

from dataclasses import dataclass

from .base import Request, ResponseData


@dataclass(frozen=True, slots=True)
class IngressPanel(ResponseData):
    """IngressPanel model."""

    title: str
    icon: str
    admin: bool
    enable: bool | None


@dataclass(frozen=True, slots=True)
class IngressPanels(ResponseData):
    """IngressPanels model."""

    panels: dict[str, IngressPanel]


@dataclass(frozen=True, slots=True)
class CreateSessionOptions(Request):
    """CreateSessionOptions model."""

    user_id: str


@dataclass(frozen=True, slots=True)
class Session(ResponseData):
    """Session model."""

    session: str
