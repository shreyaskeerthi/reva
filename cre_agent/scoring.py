"""
CRE deal scoring and buy-box evaluation
"""
from typing import Dict, List, Optional


def score_deal(struct: Dict, buybox: Dict) -> Dict:
    """
    Score a CRE deal against buy-box criteria

    Args:
        struct: Structured deal data
        buybox: Buy-box criteria with keys:
            - min_cap_rate: float
            - max_cap_rate: float (optional)
            - max_ltv: float (as decimal, e.g., 0.75 for 75%)
            - preferred_markets: list of city names
            - min_deal_size: float (dollars)
            - max_deal_size: float (dollars)
            - preferred_property_types: list of property types (optional)

    Returns:
        Dictionary with:
            - score: int (0-100)
            - verdict: str ("Pass", "Watch", "Hard Pass")
            - reasons: list of str
            - metrics: dict with computed metrics
    """
    score = 100
    reasons = []
    metrics = {}

    # Extract values from struct
    purchase_price = struct.get("purchase_price") or struct.get("asking_price")
    noi = struct.get("noi")
    cap_rate = struct.get("cap_rate")
    location = struct.get("location", {})
    city = location.get("city") if isinstance(location, dict) else None
    property_type = struct.get("property_type")
    units = struct.get("units")
    square_feet = struct.get("square_feet")

    # Compute derived metrics
    if purchase_price and noi and not cap_rate:
        cap_rate = (noi / purchase_price) * 100
        metrics["cap_rate_computed"] = cap_rate

    if purchase_price and units:
        metrics["price_per_unit"] = purchase_price / units

    if purchase_price and square_feet:
        metrics["price_per_sf"] = purchase_price / square_feet

    metrics["cap_rate"] = cap_rate
    metrics["deal_size"] = purchase_price

    # Buy-box evaluation
    min_cap = buybox.get("min_cap_rate", 0)
    max_cap = buybox.get("max_cap_rate", 100)
    max_ltv = buybox.get("max_ltv", 1.0)
    preferred_markets = buybox.get("preferred_markets", [])
    min_size = buybox.get("min_deal_size", 0)
    max_size = buybox.get("max_deal_size", float('inf'))
    preferred_types = buybox.get("preferred_property_types", [])

    # 1. Cap Rate Check
    if cap_rate:
        if cap_rate < min_cap:
            penalty = min(30, (min_cap - cap_rate) * 5)
            score -= penalty
            reasons.append(f"Cap rate {cap_rate:.2f}% below minimum {min_cap}% (−{penalty:.0f} pts)")
        elif cap_rate > max_cap:
            penalty = min(20, (cap_rate - max_cap) * 3)
            score -= penalty
            reasons.append(f"Cap rate {cap_rate:.2f}% above maximum {max_cap}% (−{penalty:.0f} pts)")
        else:
            reasons.append(f"✓ Cap rate {cap_rate:.2f}% within target range")
    else:
        score -= 10
        reasons.append("Missing cap rate data (−10 pts)")

    # 2. Deal Size Check
    if purchase_price:
        if purchase_price < min_size:
            penalty = 20
            score -= penalty
            reasons.append(f"Deal size ${purchase_price:,.0f} below minimum ${min_size:,.0f} (−{penalty} pts)")
        elif purchase_price > max_size:
            penalty = 25
            score -= penalty
            reasons.append(f"Deal size ${purchase_price:,.0f} above maximum ${max_size:,.0f} (−{penalty} pts)")
        else:
            reasons.append(f"✓ Deal size ${purchase_price:,.0f} within range")
    else:
        score -= 15
        reasons.append("Missing purchase price (−15 pts)")

    # 3. Market Check
    if preferred_markets and city:
        if city not in preferred_markets:
            penalty = 15
            score -= penalty
            reasons.append(f"Market {city} not in preferred list (−{penalty} pts)")
        else:
            reasons.append(f"✓ Market {city} is preferred")
    elif preferred_markets and not city:
        score -= 10
        reasons.append("Missing location data (−10 pts)")

    # 4. Property Type Check
    if preferred_types and property_type:
        if property_type not in preferred_types:
            penalty = 10
            score -= penalty
            reasons.append(f"Property type {property_type} not preferred (−{penalty} pts)")
        else:
            reasons.append(f"✓ Property type {property_type} is preferred")

    # 5. LTV Check (if we can compute it)
    # For simplicity, assume 75% of purchase price is debt if NOI exists
    if noi and purchase_price:
        assumed_debt = purchase_price * 0.75
        ltv = assumed_debt / purchase_price
        metrics["assumed_ltv"] = ltv

        if ltv > max_ltv:
            penalty = min(20, (ltv - max_ltv) * 100)
            score -= penalty
            reasons.append(f"Assumed LTV {ltv:.1%} exceeds max {max_ltv:.1%} (−{penalty:.0f} pts)")
            metrics["ltv_flag"] = True
        else:
            metrics["ltv_flag"] = False

    # Ensure score stays in bounds
    score = max(0, min(100, score))

    # Determine verdict
    if score >= 75:
        verdict = "Pass"
    elif score >= 50:
        verdict = "Watch"
    else:
        verdict = "Hard Pass"

    return {
        "score": int(score),
        "verdict": verdict,
        "reasons": reasons,
        "metrics": metrics
    }


def get_default_buybox() -> Dict:
    """
    Get default buy-box criteria for CRE deals

    Returns:
        Default buy-box dictionary
    """
    return {
        "min_cap_rate": 5.0,
        "max_cap_rate": 8.0,
        "max_ltv": 0.75,
        "preferred_markets": ["Austin", "Dallas", "Phoenix", "Atlanta", "Denver"],
        "min_deal_size": 5_000_000,
        "max_deal_size": 50_000_000,
        "preferred_property_types": ["multifamily", "industrial"]
    }
