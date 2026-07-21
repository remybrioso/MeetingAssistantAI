"""Help resource domain model."""

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class HelpLinkType(str, Enum):
    """Supported types of supplementary help resources."""

    ARTICLE = "article"
    VIDEO = "video"
    SUPPORT = "support"
    DOCUMENTATION = "documentation"


@dataclass(frozen=True, slots=True)
class HelpLink:
    """A validated external or internal help resource."""

    label: str
    url: str
    link_type: HelpLinkType = HelpLinkType.ARTICLE

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("HelpLink.label cannot be empty.")

        parsed = urlparse(self.url)
        if parsed.scheme not in {"http", "https", "mai"}:
            raise ValueError(
                "HelpLink.url must use http, https, or the internal mai scheme."
            )
