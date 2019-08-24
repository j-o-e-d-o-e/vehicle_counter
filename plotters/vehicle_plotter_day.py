import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv

PATH = '../csv/vehicles.csv'
HOURS = 24
START_DATE = datetime(2019, 8, 23)
END_DATE = START_DATE + timedelta(days=1)

traffic = [0] * HOURS
traffic_left = [0] * HOURS
traffic_right = [0] * HOURS
abs_traffic = 0
avg_traffic_hour = 0

avg_speed_hour = [0] * HOURS
avg_speed = 0
max_speed = 0


def main():
    # _, ax1 = plt.subplots()
    # ax2 = ax1.twinx()
    # ax1.grid()

    plt.title("TRAFFIC VOLUME\n" + START_DATE.strftime("%d. %b %Y (%a)"))
    plt.tight_layout()
    plt.grid()

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

    get_vehicles()
    set_text()
    plt.plot(x_axis, traffic, label="absolute")
    plt.plot(x_axis, traffic_left, label="dir left (k)", linestyle=":", color="green")
    plt.plot(x_axis, traffic_right, label="dir right (w)", linestyle="-.", color="red")
    plt.plot(x_axis, [avg_traffic_hour] * HOURS, label="average", linestyle="--", color="orange")
    plt.plot(x_axis, avg_speed_hour, label="speed", linestyle=":", color="purple")

    plt.legend()
    plt.show()


def get_vehicles():
    global traffic, traffic_left, traffic_right, avg_traffic_hour, avg_speed_hour, abs_traffic, avg_speed, max_speed
    speeds = [0] * HOURS
    speeds_traffic = [0] * HOURS
    max_speeds = [0] * 100
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
                        speeds[hour] += vehicle_speed
                        speeds_traffic[hour] += 1
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
    avg_traffic_hour = int(abs_traffic / HOURS)
    avg_speed_hour = list(map(lambda s, t: round(s / t, 2) if t > 3 else 0, speeds, speeds_traffic))
    avg_speed = round(sum(speeds) / sum(speeds_traffic), 2)
    max_speed = round(sum(max_speeds) / len(max_speeds), 2)


def set_text():
    if abs_traffic != 0:
        abs_traffic_left = sum(traffic_left)
        abs_traffic_right = sum(traffic_right)
        text_traffic = "Vehicles total: " + "{:,}".format(abs_traffic) \
                       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
                       + "\nVehicles per hour: " + "{:,}".format(avg_traffic_hour)
        plt.text(-1, max(traffic) + 30, text_traffic, fontweight="bold")

        text_speed = "Speed avg: " + "{:,}".format(avg_speed) + " km/h" \
                     + "\nSpeed max: " + "{:,}".format(max_speed) + " km/h"
        plt.text(2, max(traffic) + 30, text_speed, fontweight="bold")


if __name__ == "__main__":
    main()
