from enum import Enum


class BoardStatus(Enum):
    draft = "draft"
    published = "published"
    closed = "closed"
    none = "none"
