from compiler.validation.validator import validate_schema
from compiler.schemas.app_schema import AppSchemaModel

def build_schema_without_users_table():
    return AppSchemaModel(
        app_name="TestApp",
        app_type="crm",
        ui_config=[],
        api_config=[],
        db_config=[
            {
                "table_name": "contacts",
                "fields": [{"name": "id", "type": "integer"}]
            }
        ],
        auth_rules=[]
    )

def build_schema_with_dangling_endpoint():
    return AppSchemaModel(
        app_name="TestApp",
        app_type="crm",
        ui_config=[],
        api_config=[
            {
                "endpoint_id": "ep1",
                "path": "/api/contacts",
                "method": "GET",
                "auth_required": True,
                "roles_allowed": [],
                "request_schema": {},
                "response_schema": {},
                "db_table": "contacts",
                "operation": "list"
            }
        ],
        db_config=[], # Missing contacts table
        auth_rules=[]
    )

def build_valid_crm_schema():
    return AppSchemaModel(
        app_name="TestApp",
        app_type="crm",
        ui_config=[],
        api_config=[],
        db_config=[
            {
                "table_name": "users",
                "fields": [{"name": "id", "type": "integer"}]
            }
        ],
        auth_rules=[]
    )

def test_missing_users_table_is_critical():
    schema = build_schema_without_users_table()
    result = validate_schema(schema)
    assert not result.is_valid
    assert any(e.error_type == "missing_table" for e in result.errors)

def test_dangling_api_endpoint_reference():
    schema = build_schema_with_dangling_endpoint()
    result = validate_schema(schema)
    assert not result.is_valid
    assert any(e.layer == "api" for e in result.errors)

def test_clean_schema_passes():
    schema = build_valid_crm_schema()
    result = validate_schema(schema)
    assert result.is_valid
