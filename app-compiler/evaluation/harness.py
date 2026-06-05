"""
Run full evaluation suite.
Usage: python -m evaluation.harness --dataset standard --output results/run_001.json
"""
import asyncio
import json
import argparse
import time
from pathlib import Path
from compiler.pipeline import run_pipeline
from .metrics import RunMetrics

def extract_metrics(prompt_data: dict, result: any, total_latency: float) -> dict:
    if not result.success:
        return {
            "prompt_id": prompt_data["id"],
            "prompt_name": prompt_data["name"],
            "success": False,
            "failure_reason": result.failure_reason,
            "total_latency_ms": total_latency * 1000
        }
    
    refined = result.refined_schema
    schema = refined.schema
    
    return {
        "prompt_id": prompt_data["id"],
        "prompt_name": prompt_data["name"],
        "success": True,
        "total_latency_ms": total_latency * 1000,
        "stage_latencies": {k: v * 1000 for k, v in result.stage_timings.items()},
        "retries": result.retries,
        "repair_triggered": "repair" in result.stage_timings,
        "validation_errors_count": 0, # Assuming success means errors were fixed or none existed
        "fixes_applied_count": len(refined.fixes_applied),
        "execution_confidence": refined.execution_confidence,
        "is_executable": refined.is_executable,
        "db_tables_generated": len(schema.db_config),
        "api_endpoints_generated": len(schema.api_config),
        "ui_pages_generated": len(schema.ui_config),
        "auth_roles_covered": len(schema.auth_rules)
    }

def compute_summary(results: list) -> dict:
    total = len(results)
    successful = [r for r in results if r["success"]]
    if not results:
        return {}
        
    return {
        "total_runs": total,
        "success_rate": len(successful) / total,
        "avg_latency_ms": sum(r["total_latency_ms"] for r in results) / total,
        "avg_retries": sum(r.get("retries", 0) for r in results) / total,
        "avg_confidence": sum(r.get("execution_confidence", 0) for r in successful) / max(len(successful), 1),
        "repair_rate": sum(1 for r in results if r.get("repair_triggered", False)) / total
    }

async def run_evaluation(dataset: str = "standard") -> dict:
    dataset_path = Path(f"evaluation/dataset/{dataset}_prompts.json")
    if not dataset_path.exists():
        print(f"Dataset {dataset_path} not found.")
        return {}
        
    prompts = json.loads(dataset_path.read_text())
    
    results = []
    for p in prompts:
        print(f"Running {p['id']}: {p['name']}...")
        t0 = time.time()
        try:
            result = await run_pipeline(p["prompt"])
            latency = time.time() - t0
            metrics = extract_metrics(p, result, latency)
            results.append(metrics)
            print(f"  {'✓' if result.success else '✗'} | {latency:.2f}s")
        except Exception as e:
            print(f"  ✗ | Error: {str(e)}")
            results.append({
                "prompt_id": p["id"],
                "prompt_name": p["name"],
                "success": False,
                "failure_reason": str(e)
            })
    
    summary = compute_summary(results)
    return {"results": results, "summary": summary}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="standard", choices=["standard", "edge_cases"])
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    
    async def main():
        report = await run_evaluation(args.dataset)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(report, indent=2))
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(report["summary"], indent=2))
            
    asyncio.run(main())
