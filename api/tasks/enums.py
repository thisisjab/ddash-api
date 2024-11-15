import enum


class TaskState(enum.Enum):
    BACKLOG = "Backlog"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"
    CODE_REVIEW = "Code_Review"
    COMPLETED = "Completed"
    IN_PROGRESS = "In_Progress"
    QA = "QA"
    QA_REJECTED = "QA_Rejected"
    REVIEWED = "Reviewed"
    TODO = "Todo"
