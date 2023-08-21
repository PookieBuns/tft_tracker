from fastapi import APIRouter, Depends

from shared.models import Augment, GamePlayer, GamePlayerAugment

from ..db import get_connection
from ..schemas import (
    AugmentListRequest,
    AugmentListResponse,
    AugmentOrderFields,
    AugmentStat,
    OrderDirection,
)

router = APIRouter(prefix="/augments", tags=["augments"])


@router.get("/")
async def root():
    return {"message": "Welcome to the augments API!"}


@router.get("/list", response_model=AugmentListResponse)
async def get_augments(
    params: AugmentListRequest = Depends(), conn=Depends(get_connection)
):
    from sqlalchemy import case, func, select
    from sqlmodel import col

    augment_name = func.max(Augment.augment_name)
    pick_count = func.count(GamePlayerAugment.id)
    win_rate = func.avg(case([(GamePlayer.placement == 1, 1)], else_=0))
    top_4_rate = func.avg(case([(GamePlayer.placement <= 4, 1)], else_=0))
    avg_place = func.avg(GamePlayer.placement)

    def augment_order_function():
        augment_order_map = {
            AugmentOrderFields.NAME: augment_name,
            AugmentOrderFields.PICK_COUNT: pick_count,
            AugmentOrderFields.WIN_RATE: win_rate,
            AugmentOrderFields.TOP_4_RATE: top_4_rate,
            AugmentOrderFields.AVG_PLACE: avg_place,
        }
        if params.order_direction == OrderDirection.ASC:
            return augment_order_map[params.order_by].asc()
        else:
            return augment_order_map[params.order_by].desc()

    stmt = (
        select(
            augment_name.label("name"),
            pick_count.label("pick_count"),
            win_rate.label("win_rate"),
            top_4_rate.label("top_4_rate"),
            avg_place.label("avg_place"),
        )
        .select_from(
            GamePlayer.__table__.join(  # type: ignore
                GamePlayerAugment, GamePlayer.id == GamePlayerAugment.game_player_id
            ).join(Augment, Augment.id == GamePlayerAugment.augment_id)
        )
        .group_by(Augment.id)
        .order_by(augment_order_function())
        .where(col(Augment.augment_name).ilike(f"%{params.search_term}%"))
        .limit(100)
    )
    res = await conn.execute(stmt)
    response = AugmentListResponse(
        success=True,
        message="ok",
        data=[AugmentStat(**row) for row in res],
    )
    return response
