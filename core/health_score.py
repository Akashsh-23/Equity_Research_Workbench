def calculate_health_score(ratios):
    """
    Calculate a 0-100 Financial Health Score from financial ratios.
    
    Each category is scored independently, then combined using weights.
    Thresholds are based on general Indian market benchmarks.
    
    Args:
        ratios: dict returned by calculate_all_ratios()
    
    Returns:
        dict with overall score, category scores, and grade
    """

    def clamp(value, min_val=0, max_val=100):
        return max(min_val, min(max_val, value))

    # ----------------------------------------------------------------
    # 1. PROFITABILITY SCORE (weight: 30%)
    # How well does the company turn revenue into profit?
    # ----------------------------------------------------------------
    p_score = 0

    net_margin = ratios.get("Net Margin %", 0)
    if   net_margin >= 20: p_score += 40
    elif net_margin >= 10: p_score += 25
    elif net_margin >= 5:  p_score += 10
    else:                  p_score += 0

    roe = ratios.get("ROE %", 0)
    if   roe >= 20: p_score += 35
    elif roe >= 12: p_score += 20
    elif roe >= 5:  p_score += 8
    else:           p_score += 0

    roce = ratios.get("ROCE %", 0)
    if   roce >= 20: p_score += 25
    elif roce >= 12: p_score += 15
    elif roce >= 5:  p_score += 5
    else:            p_score += 0

    profitability_score = clamp(p_score)

    # ----------------------------------------------------------------
    # 2. LIQUIDITY SCORE (weight: 20%)
    # Can it pay its short-term obligations?
    # ----------------------------------------------------------------
    l_score = 0

    current_ratio = ratios.get("Current Ratio", 0)
    if   current_ratio >= 2.0: l_score += 50
    elif current_ratio >= 1.5: l_score += 35
    elif current_ratio >= 1.0: l_score += 15
    else:                      l_score += 0

    quick_ratio = ratios.get("Quick Ratio", 0)
    if   quick_ratio >= 1.5: l_score += 50
    elif quick_ratio >= 1.0: l_score += 35
    elif quick_ratio >= 0.7: l_score += 15
    else:                    l_score += 0

    liquidity_score = clamp(l_score)

    # ----------------------------------------------------------------
    # 3. LEVERAGE SCORE (weight: 20%)
    # Lower debt = higher score
    # ----------------------------------------------------------------
    lev_score = 0

    de_ratio = ratios.get("Debt to Equity", 0)
    if   de_ratio <= 0.3: lev_score += 50
    elif de_ratio <= 0.7: lev_score += 35
    elif de_ratio <= 1.5: lev_score += 15
    else:                 lev_score += 0

    interest_coverage = ratios.get("Interest Coverage", 0)
    if   interest_coverage >= 8: lev_score += 50
    elif interest_coverage >= 4: lev_score += 30
    elif interest_coverage >= 2: lev_score += 10
    else:                        lev_score += 0

    leverage_score = clamp(lev_score)

    # ----------------------------------------------------------------
    # 4. GROWTH SCORE (weight: 15%)
    # Is the business actually expanding?
    # ----------------------------------------------------------------
    g_score = 0

    revenue_growth = ratios.get("Revenue Growth %", 0)
    if   revenue_growth >= 20: g_score += 100
    elif revenue_growth >= 10: g_score += 70
    elif revenue_growth >= 5:  g_score += 40
    elif revenue_growth >= 0:  g_score += 15
    else:                      g_score += 0

    growth_score = clamp(g_score)

    # ----------------------------------------------------------------
    # 5. CASH FLOW SCORE (weight: 15%)
    # Is the profit backed by real cash?
    # ----------------------------------------------------------------
    cf_score = 0

    fcf = ratios.get("Free Cash Flow (Cr)", 0)
    if   fcf >= 5000: cf_score += 100
    elif fcf >= 1000: cf_score += 70
    elif fcf >= 0:    cf_score += 35
    else:             cf_score += 0

    cashflow_score = clamp(cf_score)

    # ----------------------------------------------------------------
    # FINAL WEIGHTED SCORE
    # ----------------------------------------------------------------
    overall = (
        profitability_score * 0.30 +
        liquidity_score     * 0.20 +
        leverage_score      * 0.20 +
        growth_score        * 0.15 +
        cashflow_score      * 0.15
    )
    overall = round(clamp(overall), 1)

    # Grade
    if   overall >= 80: grade = "A — Financially Strong"
    elif overall >= 65: grade = "B — Above Average"
    elif overall >= 50: grade = "C — Average"
    elif overall >= 35: grade = "D — Below Average"
    else:               grade = "E — Financially Weak"

    return {
        "overall_score":      overall,
        "grade":              grade,
        "category_scores": {
            "Profitability":  profitability_score,
            "Liquidity":      liquidity_score,
            "Leverage":       leverage_score,
            "Growth":         growth_score,
            "Cash Flow":      cashflow_score,
        },
        "weights": {
            "Profitability":  "30%",
            "Liquidity":      "20%",
            "Leverage":       "20%",
            "Growth":         "15%",
            "Cash Flow":      "15%",
        }
    }