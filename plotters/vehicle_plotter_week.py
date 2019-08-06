import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv

PATH = '../csv/vehicles.csv'
DAYS = 7
START_DATE = datetime(2019, 8, 5)
END_DATE = START_DATE + timedelta(days=DAYS)

plt.title("TRAFFIC VOLUME\n" + START_DATE.strftime("%d. %b %Y") + " - " + (END_DATE - timedelta(days=1)).strftime(
    "%d. %b %Y"))
plt.tight_layout()
traffic = [0] * DAYS
traffic_left = [0] * DAYS
traffic_right = [0] * DAYS
abs_speed = 0

plt.xlabel('Weekdays')
days = [(START_DATE + timedelta(days=i)).strftime("%a (%d.%m.)") for i in range(DAYS)]
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
                abs_speed += float(vehicle['speed'])
            except ValueError:
                continue
        elif date >= END_DATE:
            break

abs_traffic = sum(traffic)
abs_traffic_left = sum(traffic_left)
abs_traffic_right = sum(traffic_right)
avg_traffic = round(abs_traffic / DAYS, 2)
avg_speed = round(abs_speed / abs_traffic, 2)

text = "Vehicles total: " + "{:,}".format(abs_traffic) \
       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
       + "\nVehicles per day: " + "{:,}".format(avg_traffic) \
       + "\nSpeed avg: " + "{:,}".format(avg_speed) + " km/h"
plt.text(-0.5, max(traffic) + 3, text, fontweight="bold")

for i, v in enumerate(traffic):
    plt.text(i - 0.05, v + 20, "{:,}".format(v))

plt.bar(x_axis, traffic_left, label="dir left (k)", hatch="\\", color="green")
plt.bar(x_axis, traffic_right, label="dir right (w)", bottom=traffic_left, hatch="//", color="red")
plt.plot(x_axis, [avg_traffic] * DAYS, label="average", linestyle="--", color="orange")

plt.legend()
plt.show()
