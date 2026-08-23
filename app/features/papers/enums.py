from enum import Enum


class PaperSortField(str, Enum):
    TITLE = "title"
    PUBLICATION_YEAR = "publication_year"
    CREATED_AT = "created_at"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
    



class DocumentProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"