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
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
