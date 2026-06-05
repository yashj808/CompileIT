from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/api")

@router.get("/runs")
async def get_runs():
    """Get history of compiler runs"""
    return []
