from datetime import datetime
from helpers import get_cur_date


inn = "7727741653"
time = "2024-01-12 00:00:00"
d = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
print(d)
