import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv

PATH = '../csv/vehicles.csv'
DAYS = 31
START_DATE = datetime(2019, 8, 5)
END_DATE = START_DATE + timedelta(days=DAYS - 1)

plt.title("TRAFFIC VOLUME\n" + START_DATE.strftime("%d. %b %Y") + " - " + END_DATE.strftime("%d. %b %Y"))
plt.tight_layout()
plt.grid()
traffic = [0] * DAYS
traffic_left = [0] * DAYS
traffic_right = [0] * DAYS
speed = 0

plt.xlabel('Days')
days = []
for i in range(DAYS):
    if i % 3 == 0:
        day = (START_DATE + timedelta(days=i)).strftime("%a (%d.%m.)")
        days.append(day)
    else:
        days.append("")
x_axis = [i for i in range(DAYS)]
plt.xticks(x_axis, days)
plt.gcf().autofmt_xdate()

plt.ylabel('Vehicles')
y_axis = [i for i in range(10000) if i % 500 == 0]
plt.yticks(y_axis)

with open(PATH) as file:
    csv_reader = csv.DictReader(file)
    for vehicle in csv_reader:
        timestamp = float(vehicle['last_seen'])
        date = datetime.fromtimestamp(timestamp)
        if date < START_DATE:
            continue
        elif date < END_DATE:
            index = (date - START_DATE).days
            traffic[index] += 1
            if vehicle['dir'] == 'left':
                traffic_left[index] += 1
            else:
                traffic_right[index] += 1
            try:
                speed += float(vehicle['speed'])
            except ValueError:
                continue
        elif date >= END_DATE:
            break

abs_traffic = sum(traffic)
abs_traffic_left = sum(traffic_left)
abs_traffic_right = sum(traffic_right)
avg_traffic = abs_traffic / DAYS
avg_traffic_week = round(avg_traffic * 7, 2)
avg_speed = round(speed / abs_traffic, 2)

text = "Vehicles total: " + "{:,}".format(abs_traffic) \
       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
       + "\nVehicles per week: " + "{:,}".format(avg_traffic_week) \
       + "\nSpeed avg: " + "{:,}".format(avg_speed) + " km/h"
plt.text(-1, max(traffic) + 3, text, fontweight="bold")

for i, v in enumerate(traffic):
    plt.text(i - 0.35, v + 20, v)

plt.bar(x_axis, traffic_left, label="dir left (k)", hatch="\\", color="green")
plt.bar(x_axis, traffic_right, label="dir right (w)", bottom=traffic_left, hatch="//", color="red")
plt.plot(x_axis, [avg_traffic] * DAYS, label="average", linestyle="--", color="orange")
plt.legend()
plt.show()
