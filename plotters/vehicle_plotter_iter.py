from datetime import datetime, timedelta
# noinspection PyUnresolvedReferences
import vehicle_plotter_day as v
import sys

day = 26
month = 8
start_date = datetime(2019, month, day)
PATH = '../plots/iter/'


def main():
    times = datetime.now().day - start_date.day
    for i in range(times):
        set_data(i)
        v.main()
        # mng = p.plt.get_current_fig_manager()
        # mng.full_screen_toggle()
        v.fig.savefig(PATH + str(v.start_date.day)
                      + '_' + str(v.start_date.month)
                      + '_' + str(v.start_date.year) + '.png')
        # p.plt.close()


def set_data(i):
    v.start_date = start_date + timedelta(days=i)
    v.end_date = start_date + timedelta(days=i + 1)

    v.traffic = [0] * v.HOURS
    v.traffic_left = [0] * v.HOURS
    v.traffic_right = [0] * v.HOURS
    v.abs_traffic = 0
    v.avg_traffic_hour = 0
    v.text_traffic = ""

    v.avg_speed_hour = [0] * v.HOURS
    v.avg_speed = 0
    v.max_speed = 0
    v.text_speed = ""


def set_dates():
    global day, month, start_date
    if len(sys.argv) == 2:
        day = int(sys.argv[1])
    elif len(sys.argv) == 3:
        day = int(sys.argv[1])
        month = int(sys.argv[2])
    start_date = datetime(2019, month, day)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_dates()
    main()
