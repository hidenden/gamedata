import csv
from typing import List


def insert_header(data:List) -> List:
    data.insert(0, ["begin_date", "end_date", "hw", "units"])
    return data
    
def save_csv(fname: str, data:List):
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

def load_csv(fname) -> List:
    with open(fname, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows
