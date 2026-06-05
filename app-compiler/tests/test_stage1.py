import pytest
from compiler.stages.stage1_intent import run_stage1

@pytest.mark.asyncio
async def test_standard_crm_prompt():
    result = await run_stage1("Build a CRM with login, contacts, and admin panel")
    assert result.has_authentication == True
    assert any(r.is_admin for r in result.user_roles)
    assert len(result.features) >= 2

@pytest.mark.asyncio
async def test_vague_prompt_makes_assumptions():
    result = await run_stage1("Build an app")
    assert len(result.assumptions) > 0
    assert result.app_name is not None

@pytest.mark.asyncio  
async def test_conflicting_prompt_resolves():
    # This might depend on the LLM's interpretation, but we expect it to document something.
    result = await run_stage1("Free app with no payments. Premium users pay $10/month.")
    assert len(result.ambiguities) > 0 or len(result.assumptions) > 0
