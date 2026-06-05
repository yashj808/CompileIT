from pydantic import BaseModel
from typing import List, Dict, Optional

class DBField(BaseModel):
    name: str
    type: str                          # "string"|"integer"|"boolean"|"datetime"|"float"|"uuid"|"text"
    required: bool = True
    unique: bool = False
    indexed: bool = False
    default: Optional[str] = None
    foreign_key: Optional[str] = None  # e.g., "users.id"

class DBTable(BaseModel):
    name: str                          # snake_case plural: "users", "contacts"
    fields: List[DBField]
    relations: List[str] = []          # e.g., ["belongs_to:users", "has_many:contacts"]

class APIEndpoint(BaseModel):
    path: str                          # e.g., "/api/contacts"
    method: str                        # GET|POST|PUT|DELETE|PATCH
    description: str
    auth_required: bool = True
    roles_allowed: List[str] = []      # empty = all authenticated roles
    request_body: Optional[Dict] = None  # field_name -> type
    response_fields: List[str] = []
    db_table: str                      # which DB table this operates on

class UIPage(BaseModel):
    name: str                          # e.g., "ContactsPage"
    route: str                         # e.g., "/contacts"
    auth_required: bool = True
    roles_allowed: List[str] = []
    layout: str                        # "dashboard"|"form"|"list"|"detail"|"auth"
    api_dependencies: List[str] = []   # endpoint paths used by this page

class AuthConfig(BaseModel):
    strategy: str                      # "jwt"|"session"|"oauth"
    roles: List[str]
    protected_routes: List[str]        # list of UI routes that need auth
    permissions_map: Dict[str, List[str]]  # role -> list of allowed API paths

class ArchitectureModel(BaseModel):
    db_tables: List[DBTable]
    api_endpoints: List[APIEndpoint]
    ui_pages: List[UIPage]
    auth_config: AuthConfig
    has_payment_flow: bool
    payment_provider: Optional[str] = None  # "stripe"|"razorpay"|None
