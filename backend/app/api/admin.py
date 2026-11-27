from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.database.session import get_db
from app.repositories.farmer_repository import FarmerRepository
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse, ContentPayload
from app.schemas.dashboard import FarmerListItem, FarmerPage
from app.services import content_service
from app.services.admin_auth import issue_token, password_is_valid, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=AdminLoginResponse)
def login(body: AdminLoginRequest, settings: Settings = Depends(get_settings)) -> AdminLoginResponse:
    if not password_is_valid(body.password, settings):
        raise HTTPException(status_code=401, detail="Incorrect password")
    token, expires_at = issue_token(settings)
    return AdminLoginResponse(token=token, expires_at=expires_at)


@router.get("/content/{filename}", response_model=ContentPayload, dependencies=[Depends(require_admin)])
def get_content(filename: str) -> ContentPayload:
    return ContentPayload(content=content_service.read(filename))


@router.put("/content/{filename}", response_model=ContentPayload, dependencies=[Depends(require_admin)])
def put_content(filename: str, body: ContentPayload) -> ContentPayload:
    content_service.write(filename, body.content)
    return ContentPayload(content=content_service.read(filename))


@router.get("/farmers", response_model=FarmerPage, dependencies=[Depends(require_admin)])
def farmers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> FarmerPage:
    rows, total = FarmerRepository(db).list_page(offset, limit)
    items = [
        FarmerListItem(
            farmer_id=str(f.farmer_id),
            channel=f.channel,
            language=f.language,
            district=f.district,
            usage_consent=f.usage_consent,
            weekly_updates=f.weekly_updates,
            created_at=f.created_at,
            updated_at=f.updated_at,
        )
        for f in rows
    ]
    return FarmerPage(items=items, total=total, offset=offset, limit=limit)
