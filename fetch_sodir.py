"""Download the public Sodir (Norwegian Offshore Directorate) monthly field production table.
Source: https://factpages.sodir.no  (open government data, NLOD licence). Nothing else is downloaded."""
import urllib.request
from pathlib import Path

URL = ("https://factpages.sodir.no/public?/Factpages/external/tableview/field_production_monthly"
       "&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false")
OUT = Path("data/sodir_field_production_monthly.csv")

if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    with urllib.request.urlopen(URL, timeout=120) as r:
        OUT.write_bytes(r.read())
    print("saved", OUT, OUT.stat().st_size, "bytes")
