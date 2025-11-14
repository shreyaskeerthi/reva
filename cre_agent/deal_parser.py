"""
CRE deal parser - extracts numbers and structured data from free-form text
"""
import re
from typing import Dict, Optional, List


def parse_currency(text: str) -> Optional[float]:
    """
    Extract currency values from text

    Examples:
        "$6.5M" -> 6500000.0
        "$18,500,000" -> 18500000.0
        "6.5 million" -> 6500000.0
    """
    # Remove commas
    text = text.replace(",", "")

    # Pattern: $X.XM or $X.XB or $XXX,XXX
    patterns = [
        r'\$?\s*(\d+\.?\d*)\s*[Mm]illion',  # X million or X M
        r'\$?\s*(\d+\.?\d*)\s*M\b',          # X M
        r'\$?\s*(\d+\.?\d*)\s*[Bb]illion',   # X billion
        r'\$?\s*(\d+\.?\d*)\s*B\b',          # X B
        r'\$\s*(\d+\.?\d*)\s*[Kk]',          # $X K
        r'\$\s*(\d+)',                        # $XXX
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 'illion' in text.lower() or ' M' in text or 'M ' in text:
                if 'b' in text.lower():
                    return value * 1_000_000_000
                else:
                    return value * 1_000_000
            elif 'K' in text or 'k' in text:
                return value * 1_000
            else:
                return value

    return None


def parse_percentage(text: str) -> Optional[float]:
    """
    Extract percentage values from text

    Examples:
        "5.25% cap" -> 5.25
        "92% occupied" -> 92.0
    """
    pattern = r'(\d+\.?\d*)\s*%'
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    return None


def parse_units(text: str) -> Optional[int]:
    """
    Extract unit count from text

    Examples:
        "148-unit" -> 148
        "32 units" -> 32
    """
    patterns = [
        r'(\d+)[-\s]unit',
        r'(\d+)\s+units',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None


def parse_square_feet(text: str) -> Optional[int]:
    """
    Extract square footage from text

    Examples:
        "20k SF" -> 20000
        "20,000 SF" -> 20000
        "950 square feet" -> 950
    """
    text = text.replace(",", "")

    patterns = [
        r'(\d+\.?\d*)\s*[Kk]\s*[Ss][Ff]',      # 20k SF
        r'(\d+)\s*[Ss][Ff]',                    # 20000 SF
        r'(\d+)\s*square\s*feet',               # 950 square feet
        r'(\d+)\s*sq\s*ft',                     # 950 sq ft
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 'k' in text.lower() or 'K' in text:
                return int(value * 1_000)
            else:
                return int(value)

    return None


def extract_property_type(text: str) -> Optional[str]:
    """Extract property type from text"""
    text_lower = text.lower()

    property_types = {
        "multifamily": ["multifamily", "multi-family", "apartment", "unit"],
        "office": ["office"],
        "industrial": ["industrial", "warehouse", "distribution"],
        "retail": ["retail", "shopping center", "mall"],
        "mixed_use": ["mixed use", "mixed-use"],
    }

    for prop_type, keywords in property_types.items():
        for keyword in keywords:
            if keyword in text_lower:
                return prop_type

    return None


def extract_location(text: str) -> Dict[str, Optional[str]]:
    """
    Extract city and state from text

    Returns:
        Dictionary with 'city' and 'state' keys
    """
    # Pattern: City, State or City, XX
    pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)'
    match = re.search(pattern, text)

    if match:
        city = match.group(1)
        state = match.group(2)
        return {"city": city, "state": state}

    # Try common city names without state
    common_cities = [
        "Austin", "Dallas", "Houston", "San Antonio", "Phoenix", "Los Angeles",
        "San Francisco", "Seattle", "Portland", "Denver", "Atlanta", "Miami",
        "New York", "Boston", "Chicago", "Philadelphia"
    ]

    for city in common_cities:
        if city.lower() in text.lower():
            return {"city": city, "state": None}

    return {"city": None, "state": None}


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    # Allow "at" and " at " to be used instead of @
    text = re.sub(r'\s+at\s+', '@', text, flags=re.IGNORECASE)

    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None


def extract_broker_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract broker name, email, and company from text

    Returns:
        Dictionary with 'name', 'email', 'company' keys
    """
    broker_info = {
        "name": None,
        "email": None,
        "company": None
    }

    # Extract email
    broker_info["email"] = extract_email(text)

    # Common CRE firms
    firms = ["JLL", "CBRE", "Cushman", "Colliers", "Marcus & Millichap", "Newmark"]
    for firm in firms:
        if firm.lower() in text.lower():
            broker_info["company"] = firm
            break

    # Try to extract name (simple heuristic: look for capital name before "from" or "at" or "with")
    name_patterns = [
        r'with\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'broker\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            broker_info["name"] = match.group(1)
            break

    return broker_info


def heuristic_parse(text: str) -> Dict:
    """
    Parse CRE deal text using regex and heuristics

    Args:
        text: Raw deal text

    Returns:
        Dictionary with extracted deal fields
    """
    # Look for specific keywords and extract associated numbers
    result = {
        "property_type": extract_property_type(text),
        "location": extract_location(text),
        "purchase_price": None,
        "asking_price": None,
        "noi": None,
        "cap_rate": None,
        "units": parse_units(text),
        "square_feet": parse_square_feet(text),
        "year_built": None,
        "occupancy": None,
        "broker_name": None,
        "broker_email": None,
        "broker_company": None,
        "seller_name": None,
        "notes": text[:500] if text else None
    }

    # Extract broker info
    broker_info = extract_broker_info(text)
    result["broker_name"] = broker_info["name"]
    result["broker_email"] = broker_info["email"]
    result["broker_company"] = broker_info["company"]

    # NOI extraction
    noi_match = re.search(r'NOI[^\d]*(\$?[\d,.]+\s*(?:million|M|K)?)', text, re.IGNORECASE)
    if noi_match:
        result["noi"] = parse_currency(noi_match.group(1))

    # Cap rate extraction
    cap_match = re.search(r'(\d+\.?\d*)\s*%?\s*cap', text, re.IGNORECASE)
    if cap_match:
        result["cap_rate"] = float(cap_match.group(1))

    # Price extraction (asking or purchase)
    asking_match = re.search(r'asking[^\d]*(\$[\d,.]+\s*(?:million|M)?)', text, re.IGNORECASE)
    if asking_match:
        result["asking_price"] = parse_currency(asking_match.group(1))

    # Purchase price (if not asking)
    if not result["asking_price"]:
        # Find first large currency amount
        all_text = text
        for sentence in all_text.split('.'):
            price = parse_currency(sentence)
            if price and price > 100000:  # At least $100k
                result["purchase_price"] = price
                break

    # If we found asking price but not purchase, copy it
    if result["asking_price"] and not result["purchase_price"]:
        result["purchase_price"] = result["asking_price"]

    # Occupancy
    occupancy_match = re.search(r'(\d+)\s*%\s*occup', text, re.IGNORECASE)
    if occupancy_match:
        result["occupancy"] = float(occupancy_match.group(1)) / 100.0

    # Year built
    year_match = re.search(r'built\s+(?:in\s+)?(\d{4})', text, re.IGNORECASE)
    if year_match:
        result["year_built"] = int(year_match.group(1))

    return result
