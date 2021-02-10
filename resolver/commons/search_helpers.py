def prep_casrn(term: str) -> str:
    term = term.replace("-", "").lstrip("0")
    if len(term) > 4:
        term = term[:-3] + "-" + term[-3:-1] + "-" + term[-1]
    return term
