from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import TradeLinkRequest, TradeLinkResponse
from app.services.trade_link import build_trade_url

router = APIRouter(prefix="/trade-links", tags=["trade-links"])


@router.post("", dependencies=[Depends(get_current_user)])
def create_trade_link(body: TradeLinkRequest) -> TradeLinkResponse:
    return TradeLinkResponse(url=build_trade_url(body.league, body.search))
