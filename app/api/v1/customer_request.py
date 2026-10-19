from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.rate_limit import user_rate_limit
from app.db.session import get_db
from app.schemas.customer_request import CustomerSupportRequest
from app.schemas.customer_support_orchestrator import OrchestratorResponse
from app.services.response_pipeline.customer_support_orchestrator import (
    CustomerSupportOrchestrator,
)

router = APIRouter(
    dependencies=[Depends(user_rate_limit)], prefix="/support", tags=["Support"]
)


@router.post("/messages", response_model=OrchestratorResponse)
def process_customer_support_message(
    request: CustomerSupportRequest,
    session: Session = Depends(get_db),
) -> OrchestratorResponse:
    orchestrator = CustomerSupportOrchestrator()
    return orchestrator.process_customer_message(
        session=session,
        customer_message=request.customer_message,
    )
