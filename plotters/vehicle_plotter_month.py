import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv
import sys

PATH = '../csv/vehicles.csv'
DAYS = 31
day = 2
month = 9
start_date = datetime(2019, month, day)
end_date = start_date + timedelta(days=DAYS - 1)


def main():
    traffic = [0] * DAYS
    traffic_left = [0] * DAYS
    traffic_right = [0] * DAYS

    speed = [0] * DAYS
    max_speeds = [0] * 100
    abs_speed = 0

    plt.title("TRAFFIC VOLUME\n" + start_date.strftime("%d. %b %Y") + " - " + end_date.strftime("%d. %b %Y"))
    plt.tight_layout()
    plt.grid()

    plt.xlabel('Days')
    days = []
    for i in range(DAYS):
        if i % 3 == 0:
            day = (start_date + timedelta(days=i)).strftime("%a (%d.%m.)")
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
            timestamp = float(vehicle['first_seen'])
            date = datetime.fromtimestamp(timestamp)
            if date < start_date:
                continue
            elif date < end_date:
                index = (date - start_date).days
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
            elif date >= end_date:
                break

    abs_traffic = sum(traffic)
    avg_traffic_day = abs_traffic / DAYS
    if abs_traffic != 0:
        abs_traffic_left = sum(traffic_left)
        abs_traffic_right = sum(traffic_right)
        avg_traffic_week = int(avg_traffic_day * 7)
        text_traffic = "Vehicles total: " + "{:,}".format(abs_traffic) \
                       + "\nLeft/right: " + "{:,}".format(abs_traffic_left) + "/{:,}".format(abs_traffic_right) \
                       + "\nVehicles per week: " + "{:,}".format(avg_traffic_week) \
                       + "\nVehicles per day: " + "{:,}".format(int(avg_traffic_day))
        plt.gcf().text(0.12, 0.9, text_traffic, fontweight="bold")

        avg_speed = round(sum(speed) / abs_speed, 2)
        avg_speed_max = round(sum(max_speeds) / len(max_speeds), 2)
        text_speed = "Speed avg: " + "{:,}".format(avg_speed) + " km/h" \
                     + "\nSpeed max: " + "{:,}".format(avg_speed_max) + " km/h"
        plt.gcf().text(0.24, 0.9, text_speed, fontweight="bold")

    for i, v in enumerate(traffic):
        plt.text(i - 0.35, v + 20, v)

    plt.bar(x_axis, traffic_left, label="dir left (k)", hatch="\\", color="green")
    plt.bar(x_axis, traffic_right, label="dir right (w)", bottom=traffic_left, hatch="//", color="red")
    plt.plot(x_axis, [avg_traffic_day] * DAYS, label="average", linestyle="--", color="orange")
    plt.legend()
    plt.show()


def set_dates():
    global day, month, start_date, end_date
    if len(sys.argv) == 2:
        day = int(sys.argv[1])
    elif len(sys.argv) == 3:
        day = int(sys.argv[1])
        month = int(sys.argv[2])
    start_date = datetime(2019, month, day)
    end_date = start_date + timedelta(days=DAYS - 1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_dates()
    main()
