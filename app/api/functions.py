from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, get_warehouse, DBManager
from app.services.auth import AuthBearer

from app.services.custom_function_handler import CustomFunctionHandler, build_schemas
from dataclasses import asdict

router = APIRouter(prefix="/v1/functions")

from app.schemas.batches import BatchIn, BatchOut
from app.schemas.user import User

auth_bearer = AuthBearer()


@router.post("/", status_code=status.HTTP_200_OK, response_model=BatchOut)
async def xqf_batch(payload: BatchIn,
                    request: Request,
                    token: User = Depends(auth_bearer),
                    db_session: AsyncSession = Depends(get_db),
                    db_manager: DBManager = Depends(get_warehouse),
                    ):
    try:
        async with db_session.begin():
            schemas = await build_schemas(db_session, request.state.user['tenant_id'])
            q = CustomFunctionHandler(db_manager, payload.platform, payload.request_batch, schemas,
                                      request.state.user['tenant_db'], request.app.state.redis)
            results = await q.execute()
            results = [asdict(result) for result in results]

        return BatchOut(response_batch=results)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
