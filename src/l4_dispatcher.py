
def l4_route(text: str):
    t = text.lower()
    if '\\sum' in t or 'zeta' in t or 'series' in t:
        return 'E_Analysis'
    if 'solve' in t or 'algebra' in t:
        return 'E_Algebra'
    return 'E_General'
