import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv

PATH = '../csv/vehicles.csv'
HOURS = 24
START_DATE = datetime(2019, 8, 1)
END_DATE = START_DATE + timedelta(days=1)

plt.title("TRAFFIC VOLUME\n" + START_DATE.strftime("%d. %b %Y (%a)"))
plt.tight_layout()
plt.grid()
traffic = [0] * HOURS
traffic_left = [0] * HOURS
traffic_right = [0] * HOURS
speed = 0

plt.xlabel('Hours')
hours = []
for i in range(HOURS):
    if i % 2 == 0:
        hour = (START_DATE + timedelta(hours=i)).strftime("%H:%M")
        hours.append(hour)
    else:
        hours.append("")
x_axis = [i for i in range(HOURS)]
plt.xticks(x_axis, hours)
plt.gcf().autofmt_xdate()

plt.ylabel('Vehicles')
y_axis = [i for i in range(600) if i % 50 == 0]
plt.yticks(y_axis)

with open(PATH) as file:
    csv_reader = csv.DictReader(file)
    for vehicle in csv_reader:
        try:
            speed += float(vehicle['speed'])
        except ValueError:
            continue
        timestamp = float(vehicle['last_seen'])
        date = datetime.fromtimestamp(timestamp)
        if date < START_DATE:
            continue
        elif date < END_DATE:
            traffic[date.hour] += 1
            if vehicle['dir'] == 'left':
                traffic_left[date.hour] += 1
            else:
                traffic_right[date.hour] += 1
        elif date >= END_DATE:
            break

abs_traffic = sum(traffic)
abs_traffic_left = sum(traffic_left)
abs_traffic_right = sum(traffic_right)
avg_traffic = round(sum(traffic) / HOURS, 2)
avg_speed = round(speed / abs_traffic, 2)
text = "Vehicles total: " + "{:,}".format(abs_traffic) \
       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
       + "\nVehicles avg: " + "{:,}".format(avg_traffic) \
       + "\nSpeed avg: " + "{:,}".format(avg_speed) + " km/h"
plt.text(-1, max(traffic) + 3, text, fontweight="bold")

plt.plot(x_axis, traffic, label="absolute")
plt.plot(x_axis, traffic_left, label="dir left (k)", linestyle=":", color="green")
plt.plot(x_axis, traffic_right, label="dir right (w)", linestyle="-.", color="red")
plt.plot(x_axis, [avg_traffic] * HOURS, label="average", linestyle="--", color="orange")
plt.legend()
plt.show()
