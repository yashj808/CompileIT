from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class AppType(str, Enum):
    crm = "crm"
    ecommerce = "ecommerce"
    saas = "saas"
    marketplace = "marketplace"
    internal_tool = "internal_tool"
    social = "social"
    analytics = "analytics"
    other = "other"

class Feature(BaseModel):
    name: str                          # e.g., "role_based_access"
    description: str                   # human-readable
    priority: str = Field(pattern="^(must_have|nice_to_have|optional)$")
    requires_auth: bool = False
    requires_payment: bool = False

class UserRole(BaseModel):
    name: str                          # e.g., "admin", "user", "viewer"
    permissions: List[str]             # e.g., ["read:all", "write:own"]
    is_admin: bool = False

class IntentModel(BaseModel):
    app_name: str
    app_type: AppType
    description: str
    features: List[Feature]
    user_roles: List[UserRole]
    has_authentication: bool
    has_payments: bool
    has_analytics: bool
    ambiguities: List[str] = []        # Things that were unclear
    assumptions: List[str] = []        # Decisions made for underspecified areas
