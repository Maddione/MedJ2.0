def generate_local_summary(data: dict) -> str:
    notes = []
    for k, v in data.items():
        if k == "date":
            continue
        status = v.get("status")
        ref = v.get("reference")
        val = v.get("value")
        if status == "High":
            notes.append(f"{k} е повишен (стойност {val} вместо {ref}).")
        elif status == "Low":
            notes.append(f"{k} е понижен (стойност {val} вместо {ref}).")
    if not notes:
        return "Всички показатели са в референтните граници."
    return " ".join(notes)
