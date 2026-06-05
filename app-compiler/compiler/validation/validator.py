"""
Validation Engine — pure Python, no LLM.
Checks every cross-layer consistency rule programmatically.
Returns list of ValidationError objects.
"""
from dataclasses import dataclass
from typing import List
from ..schemas.app_schema import AppSchemaModel

@dataclass
class ValidationError:
    layer: str           # "ui"|"api"|"db"|"auth"
    error_type: str      # "missing_field"|"dangling_ref"|"type_mismatch"|"missing_table"
    message: str
    location: str        # e.g., "ui_config[0].components[1].fields_displayed[3]"
    severity: str        # "critical"|"warning"
    suggested_fix: str

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

def validate_schema(schema: AppSchemaModel) -> ValidationResult:
    errors = []
    errors.extend(_check_db_table_completeness(schema))
    errors.extend(_check_api_db_alignment(schema))
    errors.extend(_check_ui_api_alignment(schema))
    errors.extend(_check_ui_field_db_alignment(schema))
    errors.extend(_check_auth_endpoint_refs(schema))
    errors.extend(_check_required_tables(schema))

    criticals = [e for e in errors if e.severity == "critical"]
    warnings = [e for e in errors if e.severity == "warning"]

    return ValidationResult(
        is_valid=len(criticals) == 0,
        errors=criticals,
        warnings=warnings
    )

def _check_db_table_completeness(schema: AppSchemaModel) -> List[ValidationError]:
    errors = []
    for table in schema.db_config:
        if not table.fields:
            errors.append(ValidationError(
                layer="db",
                error_type="missing_field",
                message=f"Table '{table.table_name}' has no fields defined",
                location=f"db_config.{table.table_name}",
                severity="critical",
                suggested_fix=f"Add fields to table '{table.table_name}'"
            ))
    return errors

def _check_api_db_alignment(schema: AppSchemaModel) -> List[ValidationError]:
    """Every API endpoint's db_table must exist in db_config"""
    errors = []
    db_names = {t.table_name for t in schema.db_config}
    for ep in schema.api_config:
        if ep.db_table not in db_names:
            errors.append(ValidationError(
                layer="api",
                error_type="dangling_ref",
                message=f"Endpoint {ep.path} references table '{ep.db_table}' which does not exist",
                location=f"api_config[{ep.endpoint_id}].db_table",
                severity="critical",
                suggested_fix=f"Add table '{ep.db_table}' to db_config or update endpoint db_table"
            ))
    return errors

def _check_ui_api_alignment(schema: AppSchemaModel) -> List[ValidationError]:
    """Every UIComponent.api_endpoint must exist in api_config"""
    errors = []
    ep_paths = {ep.path for ep in schema.api_config}
    for page in schema.ui_config:
        for comp in page.components:
            if comp.api_endpoint and comp.api_endpoint not in ep_paths:
                errors.append(ValidationError(
                    layer="ui",
                    error_type="dangling_ref",
                    message=f"Component {comp.component_id} references unknown endpoint {comp.api_endpoint}",
                    location=f"ui_config[{page.page_name}].components[{comp.component_id}]",
                    severity="critical",
                    suggested_fix=f"Add endpoint '{comp.api_endpoint}' to api_config"
                ))
    return errors

def _check_ui_field_db_alignment(schema: AppSchemaModel) -> List[ValidationError]:
    """Every field in UIComponent.fields_displayed must exist in the corresponding DB table"""
    errors = []
    # Build: endpoint_path -> db_table_name
    ep_to_table = {ep.path: ep.db_table for ep in schema.api_config}
    # Build: table_name -> set of field names
    table_to_fields = {
        t.table_name: {f["name"] for f in t.fields}
        for t in schema.db_config
    }
    for page in schema.ui_config:
        for comp in page.components:
            if not comp.api_endpoint or not comp.fields_displayed:
                continue
            table_name = ep_to_table.get(comp.api_endpoint)
            if not table_name:
                continue
            valid_fields = table_to_fields.get(table_name, set())
            for field in comp.fields_displayed:
                if field not in valid_fields:
                    errors.append(ValidationError(
                        layer="ui",
                        error_type="missing_field",
                        message=f"UI component {comp.component_id} displays field '{field}' not in table '{table_name}'",
                        location=f"ui_config.{page.page_name}.{comp.component_id}.fields_displayed",
                        severity="critical",
                        suggested_fix=f"Remove '{field}' from fields_displayed or add it to table '{table_name}'"
                    ))
    return errors

def _check_auth_endpoint_refs(schema: AppSchemaModel) -> List[ValidationError]:
    """Auth rules must only reference endpoints that exist"""
    errors = []
    valid_paths = {ep.path for ep in schema.api_config}
    for rule in schema.auth_rules:
        for path in rule.can_call_endpoints:
            if path not in valid_paths:
                errors.append(ValidationError(
                    layer="auth",
                    error_type="dangling_ref",
                    message=f"Role '{rule.role}' references nonexistent endpoint '{path}'",
                    location=f"auth_rules[{rule.role}].can_call_endpoints",
                    severity="warning",
                    suggested_fix=f"Remove '{path}' from role '{rule.role}' permissions"
                ))
    return errors

def _check_required_tables(schema: AppSchemaModel) -> List[ValidationError]:
    """Always require a 'users' table"""
    errors = []
    table_names = {t.table_name for t in schema.db_config}
    if "users" not in table_names:
        errors.append(ValidationError(
            layer="db",
            error_type="missing_table",
            message="'users' table is required for auth but not found",
            location="db_config",
            severity="critical",
            suggested_fix="Add users table with: id, email, password_hash, role, created_at"
        ))
    return errors
