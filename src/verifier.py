
def adaptive_verify(result: dict, domain: str):
    base = result.get('output_complexity', 0) / 100000.0
    score = min(0.5, base)
    out_text = result.get('out','').lower()
    if domain=='math' and 'zeta' in out_text:
        score += 0.45
    if domain=='bio' and 'align' in out_text:
        score += 0.3
    return round(min(1.0, score),4)
