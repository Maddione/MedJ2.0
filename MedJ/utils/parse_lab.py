import re
from datetime import datetime

def parse_lab_report(text: str) -> dict:
    lines = text.splitlines()
    data = {}

    # 1) Дата
    for line in lines:
        m = re.search(r'\b(\d{2}\.\d{2}\.\d{4})\b', line)
        if m:
            data["date"] = datetime.strptime(m.group(1), "%d.%m.%Y").strftime("%d-%m-%Y")
            break

    # 2) Лабораторни показатели
    pattern = re.compile(
        r'[-–]\s*(?P<name>[^\s][^0-9%]+?)\s+'
        r'(?P<unit>[^\d\s]+)\s+'
        r'(?P<value>[-+]?\d+[\.,]?\d*)\s*'
        r'(?P<status>High|Low|Normal|)\s*'
        r'(?P<ref>[\d\.\-–\s]+)'
    )
    results = {}
    for line in lines:
        m = pattern.search(line)
        if m:
            name = m.group("name").strip().rstrip(':')
            val = float(m.group("value").replace(',', '.'))
            results[name] = {
                "unit": m.group("unit"),
                "value": val,
                "status": m.group("status") or None,
                "reference": m.group("ref").strip().replace('–', '-')
            }
    data.update(results)
    return data
