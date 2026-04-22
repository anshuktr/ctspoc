import os
import json
from dotenv import load_dotenv
from agent.intent_parser  import parse_intent
from agent.code_generator import generate_code
from agent.correction_loop import run_correction_loop

load_dotenv()

def run_agent(user_request: str):
    safe_name = user_request[:40].replace(" ", "_").replace("/", "-")
    workspace = os.path.join(os.getenv("WORKSPACE_DIR", "./workspace"), safe_name)
    max_iter  = int(os.getenv("MAX_CORRECTION_ITERATIONS", 3))

    print("\n========================================")
    print(f"Request: {user_request}")
    print("========================================")

    print("\n[1/3] Parsing intent...")
    spec = parse_intent(user_request)
    print(f"  Resources  : {spec.get('resources')}")
    print(f"  Region     : {spec.get('region')}")
    print(f"  Environment: {spec.get('environment')}")

    print("\n[2/3] Generating Terraform code...")
    code = generate_code(spec)
    print("  Code generated.")

    print("\n[3/3] Running self-correction loop...")
    result = run_correction_loop(code, workspace, max_iter)

    print("\n========================================")
    print(f"Status     : {result['trace']['final_status'].upper()}")
    print(f"Iterations : {result['trace']['iterations']}")
    print(f"Output     : {workspace}/")
    print("========================================")

    trace_path = os.path.join(workspace, "trace.json")
    with open(trace_path, "w") as f:
        json.dump(result["trace"], f, indent=2)
    print(f"Trace log  : {trace_path}")

    return result

if __name__ == "__main__":
    import sys
    request = " ".join(sys.argv[1:]) or \
        "Deploy a VNet with two subnets in East US for a dev environment"
    run_agent(request)