from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UIComponent(BaseModel):
    component_id: str                  # unique: "contacts_table_01"
    component_type: str                # "table"|"form"|"chart"|"navbar"|"sidebar"|"card"|"modal"
    props: Dict[str, Any]              # component-specific config
    api_endpoint: Optional[str] = None # which endpoint feeds this component
    fields_displayed: List[str] = []   # DB field names shown in this component

class UIPageConfig(BaseModel):
    page_name: str
    route: str
    auth_required: bool
    roles_allowed: List[str]
    layout: str
    components: List[UIComponent]
    title: str

class APIEndpointConfig(BaseModel):
    endpoint_id: str                   # unique: "get_contacts_01"
    path: str
    method: str
    auth_required: bool
    roles_allowed: List[str]
    request_schema: Dict[str, str]     # field_name -> type string
    response_schema: Dict[str, str]    # field_name -> type string
    db_table: str
    operation: str                     # "list"|"create"|"read"|"update"|"delete"
    filters: List[str] = []            # filterable fields

class DBTableConfig(BaseModel):
    table_name: str
    fields: List[Dict[str, Any]]       # full field definitions
    indexes: List[str] = []
    constraints: List[str] = []

class AuthRuleConfig(BaseModel):
    role: str
    can_access_routes: List[str]
    can_call_endpoints: List[str]
    can_read_tables: List[str]
    can_write_tables: List[str]

class AppSchemaModel(BaseModel):
    schema_version: str = "1.0"
    app_name: str
    app_type: str
    ui_config: List[UIPageConfig]
    api_config: List[APIEndpointConfig]
    db_config: List[DBTableConfig]
    auth_rules: List[AuthRuleConfig]
    payment_config: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
