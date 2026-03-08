"""Health route."""
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request):
    db = request.app.state.db
    count_row = db.fetch_one("SELECT COUNT(*) AS count FROM master_agents")
    return {"status": "ok", "db": "connected", "agents": count_row["count"] if count_row else 0}
