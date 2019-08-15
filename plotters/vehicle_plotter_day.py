import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv

PATH = '../csv/vehicles.csv'
HOURS = 24
START_DATE = datetime(2019, 8, 14)
END_DATE = START_DATE + timedelta(days=1)

plt.title("TRAFFIC VOLUME\n" + START_DATE.strftime("%d. %b %Y (%a)"))
plt.tight_layout()
plt.grid()

traffic = [0] * HOURS
traffic_left = [0] * HOURS
traffic_right = [0] * HOURS

speed = [0] * HOURS
traffic_speed = [0] * HOURS
max_speed = [0] * 50

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
        timestamp = float(vehicle['last_seen'])
        date = datetime.fromtimestamp(timestamp)
        if date < START_DATE:
            continue
        elif date < END_DATE:
            hour = date.hour
            traffic[hour] += 1
            if vehicle['dir'] == 'left':
                traffic_left[hour] += 1
            else:
                traffic_right[hour] += 1
            try:
                vehicle_speed = float(vehicle['speed'])
                if vehicle_speed > 40:
                    speed[hour] += vehicle_speed
                    traffic_speed[hour] += 1
                min_speed = min(max_speed)
                if min_speed < vehicle_speed < 200:
                    for i in range(len(max_speed)):
                        if max_speed[i] == min_speed:
                            max_speed[i] = vehicle_speed
                            break
            except ValueError:
                continue
        elif date >= END_DATE:
            break

abs_traffic = sum(traffic)
abs_traffic_left = sum(traffic_left)
abs_traffic_right = sum(traffic_right)
avg_traffic = int(abs_traffic / HOURS)

avg_speed = round(sum(speed) / sum(traffic_speed), 2)
avg_speed_hours = list(map(lambda s, t: round(s / t, 2) if t > 3 else 0, speed, traffic_speed))
avg_speed_max = round(sum(max_speed) / len(max_speed), 2)

text = "Vehicles total: " + "{:,}".format(abs_traffic) \
       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
       + "\nVehicles per hour: " + "{:,}".format(avg_traffic) \
       + "\nSpeed avg: " + "{:,}".format(avg_speed) + " km/h" \
       + "\nSpeed max: " + "{:,}".format(avg_speed_max) + " km/h"
plt.text(-1, max(traffic) + 30, text, fontweight="bold")

plt.plot(x_axis, traffic, label="absolute")
plt.plot(x_axis, traffic_left, label="dir left (k)", linestyle=":", color="green")
plt.plot(x_axis, traffic_right, label="dir right (w)", linestyle="-.", color="red")
plt.plot(x_axis, [avg_traffic] * HOURS, label="average", linestyle="--", color="orange")
plt.plot(x_axis, avg_speed_hours, label="speed", linestyle=":", color="purple")

plt.legend()
plt.show()
