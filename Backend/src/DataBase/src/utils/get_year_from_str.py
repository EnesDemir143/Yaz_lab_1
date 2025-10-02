import re

def get_year_from_str(year_str: str) -> int:
    sinif_match = re.search(r'(\d+)', year_str) 
    if sinif_match:
        return int(sinif_match.group(1))
    else:
        raise ValueError(f"year string '{year_str}' does not contain a valid year")