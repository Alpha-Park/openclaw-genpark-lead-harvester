# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkLeadHarvester

client = OpenClawGenParkLeadHarvester()

TOOLS = [
    {
        "name": "calculate_icp_fit",
        "description": "Calculates firmographic distance and ICP fit score across headcount, revenue, and tech stack.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_profile": {"type": "object"},
                "icp_target": {"type": "object"}
            },
            "required": ["company_profile", "icp_target"]
        }
    },
    {
        "name": "compute_bayesian_intent_score",
        "description": "Calculates Bayesian buying intent posterior probability with exponential time-decay.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buying_signals": {"type": "array", "items": {"type": "object"}},
                "prior_prob": {"type": "number"},
                "current_timestamp": {"type": "number"}
            },
            "required": ["buying_signals"]
        }
    },
    {
        "name": "classify_lead_tier_and_routing",
        "description": "Classifies lead into 4-quadrant routing strategy (AE outbound, ABM nurture, PLG auto).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_profile": {"type": "object"},
                "icp_fit_score": {"type": "number"},
                "intent_score": {"type": "number"}
            },
            "required": ["company_profile", "icp_fit_score", "intent_score"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "calculate_icp_fit":
            res = client.calculate_icp_fit(args["company_profile"], args["icp_target"])
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "compute_bayesian_intent_score":
            res = client.compute_bayesian_intent_score(args["buying_signals"], args.get("prior_prob", 0.05), args.get("current_timestamp"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "classify_lead_tier_and_routing":
            res = client.classify_lead_tier_and_routing(args["company_profile"], args["icp_fit_score"], args["intent_score"])
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            try:
                req = json.loads(line)
            except json.JSONDecodeError as exc:
                print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}), flush=True)
                continue
            if not isinstance(req, dict) or req.get("jsonrpc") != "2.0" or not isinstance(req.get("method"), str):
                print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}), flush=True)
                continue
            # JSON-RPC notifications never receive a response or execute request-only tools.
            if "id" not in req:
                continue
            if req["method"] == "initialize":
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {
                    "protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                    "serverInfo": {"name": 'openclaw-genpark-lead-harvester', "version": "1.0.0"}
                }}), flush=True)
                continue
            if req["method"] == "ping":
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {}}), flush=True)
                continue
            if req["method"] not in ("tools/list", "tools/call"):
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": "Method not found"}}), flush=True)
                continue
            if req["method"] == "tools/call":
                params = req.get("params")
                if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict) or params.get("name") not in ('calculate_icp_fit', 'compute_bayesian_intent_score', 'classify_lead_tier_and_routing'):
                    print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32602, "message": "Unknown tool or invalid arguments"}}), flush=True)
                    continue
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req.get("id") if isinstance(req, dict) else None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
