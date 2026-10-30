# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Lead Harvester - B2B Multi-Channel Lead Enrichment & Bayesian Intent Pipeline
Standard Library only: math, time, typing.
Calculates firmographic ICP distance, sequential Bayesian buying intent updating with
exponential recency decay, and automated AE/PLG quadrant routing.
"""

import math
import time
from typing import Dict, List, Any

class OpenClawGenParkLeadHarvester:
    def __init__(self, half_life_days: float = 30.0):
        # Decay lambda: lambda = ln(2) / half_life
        self.decay_lambda = math.log(2.0) / max(1.0, half_life_days)
        self.signal_weights = {
            "WEBSITE_PRICING_VISIT": 4.5,
            "COMPETITOR_CHURN_SIGNAL": 5.0,
            "JOB_POSTING_AI_ENGINEERS": 3.2,
            "FUNDING_ROUND_SERIES_B": 2.8,
            "KEY_EXECUTIVE_HIRE": 2.2,
            "WHITEPAPER_DOWNLOAD": 1.8,
            "DOCS_API_KEY_CREATED": 6.0
        }

    def calculate_icp_fit(self, company_profile: Dict[str, Any],
                          icp_target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes normalized firmographic alignment score between company and ICP target.
        Dimensions: Headcount log-distance, Revenue log-distance, Industry match, Tech stack Jaccard.
        """
        # 1. Headcount fit
        h_actual = max(1.0, float(company_profile.get("headcount", 50)))
        h_target = max(1.0, float(icp_target.get("target_headcount", 200)))
        log_diff_h = abs(math.log10(h_actual) - math.log10(h_target))
        headcount_score = max(0.0, 1.0 - (log_diff_h / 2.0))

        # 2. Revenue fit
        r_actual = max(1.0, float(company_profile.get("arr_usd", 1000000)))
        r_target = max(1.0, float(icp_target.get("target_arr_usd", 5000000)))
        log_diff_r = abs(math.log10(r_actual) - math.log10(r_target))
        revenue_score = max(0.0, 1.0 - (log_diff_r / 2.0))

        # 3. Industry match
        c_industries = set(s.lower() for s in company_profile.get("industries", []))
        t_industries = set(s.lower() for s in icp_target.get("target_industries", []))
        ind_intersect = c_industries.intersection(t_industries)
        industry_score = 1.0 if ind_intersect else 0.2

        # 4. Tech stack match (Jaccard similarity)
        c_tech = set(s.lower() for s in company_profile.get("tech_stack", []))
        t_tech = set(s.lower() for s in icp_target.get("target_tech_stack", []))
        union = c_tech.union(t_tech)
        tech_score = len(c_tech.intersection(t_tech)) / len(union) if union else 0.5

        overall_icp_score = round(
            0.25 * headcount_score + 0.25 * revenue_score + 0.25 * industry_score + 0.25 * tech_score,
            3
        )

        return {
            "company_name": company_profile.get("name", "Unknown"),
            "headcount_score": round(headcount_score, 3),
            "revenue_score": round(revenue_score, 3),
            "industry_match_score": round(industry_score, 3),
            "tech_stack_score": round(tech_score, 3),
            "overall_icp_fit_score": overall_icp_score,
            "is_icp_qualified": overall_icp_score >= 0.65
        }

    def compute_bayesian_intent_score(self, buying_signals: List[Dict[str, Any]],
                                      prior_prob: float = 0.05,
                                      current_timestamp: float = None) -> Dict[str, Any]:
        """
        Calculates posterior probability of active purchase intent via sequential Bayesian updating
        with exponential time-decay on aging signals.
        """
        now = current_timestamp if current_timestamp is not None else time.time()
        prior_prob = max(0.001, min(0.999, prior_prob))
        prior_odds = prior_prob / (1.0 - prior_prob)
        current_odds = prior_odds

        signal_audit = []
        for s in buying_signals:
            sig_type = s.get("signal_type", "GENERIC_INTERACTION")
            base_lr = self.signal_weights.get(sig_type, s.get("likelihood_ratio", 1.5))
            
            sig_time = s.get("timestamp", now)
            delta_days = max(0.0, (now - sig_time) / 86400.0)
            decay_factor = math.exp(-self.decay_lambda * delta_days)
            
            # Decayed likelihood ratio: interpolates towards 1.0 (neutral evidence)
            effective_lr = 1.0 + (base_lr - 1.0) * decay_factor
            current_odds *= effective_lr

            signal_audit.append({
                "signal_type": sig_type,
                "base_likelihood_ratio": base_lr,
                "age_days": round(delta_days, 1),
                "decay_factor": round(decay_factor, 3),
                "effective_likelihood_ratio": round(effective_lr, 3)
            })

        posterior_prob = current_odds / (1.0 + current_odds)
        posterior_prob = max(0.0, min(1.0, posterior_prob))

        return {
            "prior_probability": round(prior_prob, 4),
            "posterior_intent_probability": round(posterior_prob, 4),
            "intent_lift_multiplier": round(posterior_prob / prior_prob, 2) if prior_prob > 0 else 1.0,
            "signals_processed_count": len(buying_signals),
            "signal_audit": signal_audit
        }

    def classify_lead_tier_and_routing(self, company_profile: Dict[str, Any],
                                       icp_fit_score: float,
                                       intent_score: float) -> Dict[str, Any]:
        """
        Classifies lead into 4-quadrant routing strategy based on ICP fit and purchase intent.
        """
        if icp_fit_score >= 0.65 and intent_score >= 0.35:
            tier = "TIER_1_HOT"
            action = "DIRECT_ENTERPRISE_AE_OUTREACH"
            priority = "P0_IMMEDIATE_DISPATCH"
        elif icp_fit_score >= 0.65 and intent_score < 0.35:
            tier = "TIER_2_NURTURE"
            action = "ACCOUNT_BASED_MARKETING_DRIP"
            priority = "P2_WEEKLY_CADENCE"
        elif icp_fit_score < 0.65 and intent_score >= 0.35:
            tier = "TIER_3_SELF_SERVE"
            action = "AUTOMATED_PRODUCT_LED_ONBOARDING"
            priority = "P1_HOURLY_AUTO_INVITE"
        else:
            tier = "TIER_4_DISQUALIFIED"
            action = "PASSIVE_NEWSLETTER_ARCHIVE"
            priority = "P3_LOW"

        return {
            "company_name": company_profile.get("name", "Unknown"),
            "lead_tier": tier,
            "recommended_routing_action": action,
            "routing_priority": priority,
            "scores": {
                "icp_fit": icp_fit_score,
                "intent": intent_score
            }
        }
