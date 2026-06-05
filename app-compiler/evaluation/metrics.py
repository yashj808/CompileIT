from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RunMetrics:
    prompt_id: str
    prompt_name: str
    prompt_type: str          # "standard" | "edge"
    success: bool
    total_latency_ms: float
    stage_latencies: dict     # stage_name -> ms
    retries: int
    repair_triggered: bool
    validation_errors_count: int
    fixes_applied_count: int
    execution_confidence: float
    is_executable: bool
    failure_reason: Optional[str]
    
    # Schema completeness metrics
    db_tables_generated: int
    api_endpoints_generated: int
    ui_pages_generated: int
    auth_roles_covered: int
