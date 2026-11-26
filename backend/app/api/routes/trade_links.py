from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_user
from app.models import (
    ParsedTradeUrl,
    ParseTradeUrlRequest,
    TradeLinkRequest,
    TradeLinkResponse,
)
from app.services.trade_link import build_trade_url
from app.services.trade_url_parser import parse_trade_url

router = APIRouter(prefix="/trade-links", tags=["trade-links"])


@router.post("", dependencies=[Depends(get_current_user)])
def create_trade_link(body: TradeLinkRequest) -> TradeLinkResponse:
    return TradeLinkResponse(url=build_trade_url(body.league, body.search))


@router.post("/parse", dependencies=[Depends(get_current_user)])
def parse_trade_link(body: ParseTradeUrlRequest, session: SessionDep) -> ParsedTradeUrl:
    """Read a pasted trade-site search link, to fill in a new template."""
    try:
        return parse_trade_url(body.url, session)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
