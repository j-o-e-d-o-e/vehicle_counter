import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv
import sys

PATH = '../csv/vehicles.csv'
HOURS = 24
day = 24
month = 8
start_date = datetime(2019, month, day)
end_date = start_date + timedelta(days=1)

traffic = [0] * HOURS
traffic_left = [0] * HOURS
traffic_right = [0] * HOURS
abs_traffic = 0
avg_traffic_hour = 0
text_traffic = ""

avg_speed_hour = [0] * HOURS
avg_speed = 0
max_speed = 0
text_speed = ""


def main():
    _, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.grid()

    plt.title("TRAFFIC VOLUME\n" + start_date.strftime("%d. %b %Y (%a)"))
    # plt.tight_layout()

    ax1.set_xlabel('Hours')
    x_axis = [i for i in range(HOURS)]
    hours = []
    for i in range(HOURS):
        if i % 2 == 0:
            hour = (start_date + timedelta(hours=i)).strftime("%H:%M")
            hours.append(hour)
        else:
            hours.append("")
    plt.xticks(x_axis, hours)
    plt.gcf().autofmt_xdate()

    get_vehicles()

    set_text()
    plt.gcf().text(0.12, 0.9, text_traffic, fontweight="bold")
    plt.gcf().text(0.24, 0.9, text_speed, fontweight="bold")

    ax1.set_ylabel('Vehicles')
    ax1.set_yticks([i for i in range(600) if i % 50 == 0])

    line1, = ax1.plot(x_axis, traffic)
    line2, = ax1.plot(x_axis, [avg_traffic_hour] * HOURS, linestyle="--", color="orange")
    line3, = ax1.plot(x_axis, traffic_left, linestyle=":", color="green")
    line4, = ax1.plot(x_axis, traffic_right, linestyle="-.", color="red")

    ax2.set_ylabel('Speed (km/h)')
    line5, = ax2.plot(x_axis, avg_speed_hour, linestyle=":", color="magenta")
    ax2.set_yticks([i for i in range(100) if i % 10 == 0])

    plt.legend((line1, line2, line3, line4, line5), ('absolute', 'average', 'dir left (k)', 'dir right (w)', 'speed'))
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
            if date < start_date:
                continue
            elif date < end_date:
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
            elif date >= end_date:
                break
    abs_traffic = sum(traffic)
    avg_traffic_hour = int(abs_traffic / HOURS)
    sum_speeds_traffic = sum(speeds_traffic)
    if sum_speeds_traffic != 0:
        avg_speed_hour = list(map(lambda s, t: round(s / t, 2) if t > 3 else 0, speeds, speeds_traffic))
        avg_speed = round(sum(speeds) / sum_speeds_traffic, 2)
        max_speed = round(sum(max_speeds) / len(max_speeds), 2)


def set_text():
    global text_traffic, text_speed
    if abs_traffic != 0:
        abs_traffic_left = sum(traffic_left)
        abs_traffic_right = sum(traffic_right)
        text_traffic = "Vehicles total: " + "{:,}".format(abs_traffic) \
                       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
                       + "\nVehicles per hour: " + "{:,}".format(avg_traffic_hour)
        text_speed = "Speed avg: " + "{:,}".format(avg_speed) + " km/h" \
                     + "\nSpeed max: " + "{:,}".format(max_speed) + " km/h"


def set_dates():
    global day, month, start_date, end_date
    if len(sys.argv) == 2:
        day = int(sys.argv[1])
    elif len(sys.argv) == 3:
        day = int(sys.argv[1])
        month = int(sys.argv[2])
    start_date = datetime(2019, month, day)
    end_date = start_date + timedelta(days=1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_dates()
    main()
