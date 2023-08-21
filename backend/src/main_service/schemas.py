from enum import StrEnum

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict | list


class AugmentStat(BaseModel):
    name: str
    pick_count: int
    win_rate: float
    top_4_rate: float
    avg_place: float


class AugmentOrderFields(StrEnum):
    NAME = "name"
    PICK_COUNT = "pick_count"
    WIN_RATE = "win_rate"
    TOP_4_RATE = "top_4_rate"
    AVG_PLACE = "avg_place"


class OrderDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class AugmentListResponse(APIResponse):
    data: list[AugmentStat]


class AugmentListRequest(BaseModel):
    order_by: AugmentOrderFields = AugmentOrderFields.PICK_COUNT
    order_direction: OrderDirection = OrderDirection.DESC
    search_term: str = ""
