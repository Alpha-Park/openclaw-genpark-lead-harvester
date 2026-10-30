# -*- coding: utf-8 -*-
import time
from client import OpenClawGenParkLeadHarvester

harvester = OpenClawGenParkLeadHarvester()

target_icp = {
    "target_headcount": 150,
    "target_arr_usd": 10000000,
    "target_industries": ["AI", "Software", "Fintech"],
    "target_tech_stack": ["Python", "Kubernetes", "PostgreSQL", "React"]
}

company = {
    "name": "Synthetix Labs",
    "headcount": 120,
    "arr_usd": 8500000,
    "industries": ["AI", "Enterprise SaaS"],
    "tech_stack": ["Python", "PostgreSQL", "PyTorch", "Docker"]
}

# 1. Calculate ICP Fit
fit = harvester.calculate_icp_fit(company, target_icp)
print(f"ICP Fit for {company['name']}: {fit['overall_icp_fit_score']} (Qualified: {fit['is_icp_qualified']})")

# 2. Bayesian Buying Intent
now = time.time()
signals = [
    {"signal_type": "WEBSITE_PRICING_VISIT", "timestamp": now - 86400 * 2},
    {"signal_type": "JOB_POSTING_AI_ENGINEERS", "timestamp": now - 86400 * 10},
    {"signal_type": "DOCS_API_KEY_CREATED", "timestamp": now - 3600 * 4}
]
intent = harvester.compute_bayesian_intent_score(signals, prior_prob=0.05, current_timestamp=now)
print(f"\nBayesian Intent Probability: {intent['posterior_intent_probability']*100:.1f}% (Lift: {intent['intent_lift_multiplier']}x)")

# 3. Classify Routing
routing = harvester.classify_lead_tier_and_routing(company, fit['overall_icp_fit_score'], intent['posterior_intent_probability'])
print(f"\nRouting Decision: {routing['lead_tier']} -> {routing['recommended_routing_action']}")
