import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv

PATH = '../csv/vehicles.csv'
DAYS = 7
START_DATE = datetime(2019, 8, 19)
END_DATE = START_DATE + timedelta(days=DAYS)

traffic = [0] * DAYS
traffic_left = [0] * DAYS
traffic_right = [0] * DAYS

speed = [0] * DAYS
max_speeds = [0] * 100
abs_speed = 0

plt.title("TRAFFIC VOLUME\n" + START_DATE.strftime("%d. %b %Y") + " - " + (END_DATE - timedelta(days=1)).strftime(
    "%d. %b %Y"))
plt.tight_layout()

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
                vehicle_speed = float(vehicle['speed'])
                if vehicle_speed > 40:
                    speed[index] += vehicle_speed
                    abs_speed += 1
                min_speed = min(max_speeds)
                if min_speed < vehicle_speed < 200:
                    for i in range(len(max_speeds)):
                        if max_speeds[i] == min_speed:
                            max_speeds[i] = vehicle_speed
                            break
            except ValueError:
                continue
        elif date >= END_DATE:
            break

abs_traffic = sum(traffic)
avg_traffic_day = int(abs_traffic / DAYS)
if abs_traffic != 0:
    abs_traffic_left = sum(traffic_left)
    abs_traffic_right = sum(traffic_right)
    text_traffic = "Vehicles total: " + "{:,}".format(abs_traffic) \
                   + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
                   + "\nVehicles per day: " + "{:,}".format(avg_traffic_day)
    plt.text(-0.5, max(traffic) + 300, text_traffic, fontweight="bold")

    avg_speed = round(sum(speed) / abs_speed, 2)
    avg_speed_max = round(sum(max_speeds) / len(max_speeds), 2)
    text_speed = "Speed avg: " + "{:,}".format(avg_speed) + " km/h" \
                 + "\nSpeed max: " + "{:,}".format(avg_speed_max) + " km/h"
    plt.text(0.5, max(traffic) + 300, text_speed, fontweight="bold")

for i, v in enumerate(traffic):
    plt.text(i - 0.05, v + 20, "{:,}".format(v))

plt.bar(x_axis, traffic_left, label="dir left (k)", hatch="\\", color="green")
plt.bar(x_axis, traffic_right, label="dir right (w)", bottom=traffic_left, hatch="//", color="red")
plt.plot(x_axis, [avg_traffic_day] * DAYS, label="average", linestyle="--", color="orange")

plt.legend()
plt.show()
