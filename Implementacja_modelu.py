import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrowPatch


def hhmm_to_hour_minutes(time_hhmm):
    hours = int(time_hhmm / 100)
    minutes = time_hhmm - hours * 100

    return hours, minutes


def to_hhmm(hours, minutes):
    return hours * 100 + minutes


def time_difference(time_start, time_stop):
    hours_start, minutes_start = hhmm_to_hour_minutes(time_start)
    hours_stop, minutes_stop = hhmm_to_hour_minutes(time_stop)

    return (hours_stop * 60 + minutes_stop) - (hours_start * 60 + minutes_start)


def return_true_false_based_on_probability(probability):
    nr = np.random.uniform(0, 1, 1)
    if nr > probability:
        return False
    else:
        return True


nl = '\n'


class Plane:
    def __init__(self, time_arrival: int, time_departure: int, status: str, plane_id: int,
                 emergency_probability: float):
        self.id = plane_id
        self.arrival = time_arrival
        self.departure = time_departure
        self.actual_arrival = time_arrival
        self.actual_departure = time_departure
        self.if_emergency = return_true_false_based_on_probability(emergency_probability)
        # nawet jeśli samolot wylądował później, to nie może wylecieć szybciej niż zaplanowany czas jego obsługi
        self.time_to_prepare_for_departure = time_difference(self.arrival, self.departure)
        print(
            f"Class PLane initialization parameters: id: {self.id}{nl}arrival: {self.arrival}{nl}departure: "
            f"{self.departure}{nl}service time: {self.time_to_prepare_for_departure}{nl} ")



class Schedule:
    def __init__(self):
        self.list_of_planes = []

    def generate_schedule(self, nr_of_planes, prob_of_emergency):
        arrivals_hour = np.random.uniform(0, 24, nr_of_planes).astype(int)
        arrivals_minutes = np.random.uniform(0, 59, nr_of_planes).astype(int)
        arrivals_hour.sort()
        arrivals = []

        for i in range(nr_of_planes):
            arrivals.append(to_hhmm(arrivals_hour[i], arrivals_minutes[i]))

        departures = []

        for i in range(nr_of_planes):
            departure_hour = np.random.uniform(arrivals_hour[i] + 1, arrivals_hour[i] + 4, 1).astype(
                int)
            if departure_hour - arrivals_hour[i] == 1:
                departure_minutes = np.random.uniform(arrivals_minutes[i], 59, 1).astype(int)
            else:
                departure_minutes = np.random.uniform(0, 59, 1).astype(int)

            departures.append(to_hhmm(departure_hour[0], departure_minutes[0]))

        for i in range(nr_of_planes):
            plane_arr = int(arrivals[i])
            plane_dep = int(departures[i])
            # print(plane_arr, plane_dep)
            new_plane = Plane(plane_arr, plane_dep, '', i, prob_of_emergency)
            self.list_of_planes.append(new_plane)

        #print(f"Generated schedule: {nl}{self.list_of_planes}{nl}")

    def print_data(self):
        for plane in self.list_of_planes:
            print(
                f"Planes in simulation: id: {plane.id}{nl}arrival: {plane.arrival}{nl}departure: {plane.departure}{nl}actual arrival: {plane.actual_arrival}{nl}actual departure: {plane.actual_departure}{nl}emergency?: {plane.if_emergency}{nl}service time: {plane.time_to_prepare_for_departure}{nl} ")


class Airport:

    def __init__(self, nr_of_runways, max_nr_of_planes_on_ground):
        self.number_of_runways = nr_of_runways
        self.max_number_of_planes_on_ground = max_nr_of_planes_on_ground
        self.runways_occupation = {}
        self.list_planes_waiting_to_land = []
        self.list_planes_waiting_to_departure = []
        self.planes_currently_on_the_airport = []
        self.list_runways_occupation = []

    def initialize_runway_occupation(self):
        for i in range(self.number_of_runways):
            self.runways_occupation[i + 1] = [0, '', '', 0]
        #print(f"Initialized runway occupation: {nl}{self.runways_occupation}{nl}")

    def check_runways_occupation(self):

        temp = []
        order = []

        for i in range(self.number_of_runways):
            runway = self.runways_occupation[i + 1]
            temp.append(runway[3])

        clone_temp = temp.copy()
        clone_temp.sort()

        while len(clone_temp) > 0:
            g = [i for i, n in enumerate(temp) if n == clone_temp[0]]
            if g[0] not in order:
                order.extend(g)
            del clone_temp[0]

        for indeks in order:
            runway = self.runways_occupation[indeks + 1]
            if runway[0] == 0:
                return indeks + 1

        return -1

    def new_plane_on_runway(self, runway_nr, plane, reason, current_time):
        time_to_leave_runway = np.random.uniform(3, 6, 1).astype(int)[0]
        counter = self.runways_occupation[runway_nr][3]
        self.runways_occupation[runway_nr] = [time_to_leave_runway, plane, reason, counter + 1]
        self.list_runways_occupation.append([runway_nr, current_time, time_to_leave_runway, plane, reason])

    def upload_time_departure(self, airplane):
        h_arrival, m_arrival = hhmm_to_hour_minutes(airplane.actual_arrival)
        full_minutes_arrival = h_arrival * 60 + m_arrival
        full_minutes_departure = airplane.time_to_prepare_for_departure + full_minutes_arrival
        h_departure = int(full_minutes_departure / 60)
        m_departure = full_minutes_departure - h_departure * 60
        airplane.actual_departure = to_hhmm(h_departure, m_departure)


# ------------ Przygotowanie do symulacji ------------------------

current_time_hours = 0
current_time_minutes = 0
current_time = 0
probability_of_emergency = float(input(
    "Podaj prawdopodobieństwo (od 0.0 do 1.0), że samolot otrzyma pierwszeństwo obsługi podczas przylotu: "))
simulation_duration = 2400  # format HHMM
number_of_planes = int(input("Podaj liczbę samolotów, które mają zostać uwzględnione w harmonogramie symulacji: "))
liczba_pasow_startowych = int(input("Podaj liczbę pasów startowych na lotnisku: "))
maks_samolotow_na_ziemi = int(input("Podaj maksymalną liczbę samolotów, która może w danej chwili przebywać na "
                                    "lotnisku: "))

simulation_schedule = Schedule()
simulation_schedule.generate_schedule(number_of_planes, probability_of_emergency)
simulation_Airport = Airport(liczba_pasow_startowych, maks_samolotow_na_ziemi)
simulation_Airport.initialize_runway_occupation()

# -------- Przebieg symulacji ----------


while current_time < simulation_duration:

    # Sprawdzenie czy są samoloty do przylotu i przypisanie do pasa (zarówno te, które czekają na lądowanie oraz te,
    # które w tym momencie się zgłaszają)
    # sprawzenie czy są samoloty z pierwszeństwem (awaria)

    print(f"time: {current_time}")
    print(f"Airport: {nl}planes waiting to land: {simulation_Airport.list_planes_waiting_to_land}{nl}planes waiting "
          f"to departure: {simulation_Airport.list_planes_waiting_to_departure}{nl}planes on the gr"
          f"ound: {simulation_Airport.planes_currently_on_the_airport}{nl}planes on runways: "
          f"{simulation_Airport.runways_occupation} ")

    for airplane in simulation_schedule.list_of_planes:
        if airplane.arrival == current_time:

            if airplane.if_emergency:
                available_runway = simulation_Airport.check_runways_occupation()
                if available_runway != -1 and len(
                        simulation_Airport.planes_currently_on_the_airport) < simulation_Airport.max_number_of_planes_on_ground:
                    simulation_Airport.new_plane_on_runway(available_runway, airplane, "arrival", current_time)
                else:
                    simulation_Airport.list_planes_waiting_to_land.insert(0, airplane)

    for airplane in simulation_Airport.list_planes_waiting_to_land:
        available_runway = simulation_Airport.check_runways_occupation()
        if available_runway != -1 and len(
                simulation_Airport.planes_currently_on_the_airport) < simulation_Airport.max_number_of_planes_on_ground:
            simulation_Airport.new_plane_on_runway(available_runway, airplane, "arrival", current_time)
            simulation_Airport.list_planes_waiting_to_land.remove(airplane)
            airplane.actual_arrival = current_time
            simulation_Airport.upload_time_departure(airplane)

    for airplane in simulation_Airport.list_planes_waiting_to_departure:
        available_runway = simulation_Airport.check_runways_occupation()
        if available_runway != -1:
            simulation_Airport.new_plane_on_runway(available_runway, airplane, "departure", current_time)
            simulation_Airport.list_planes_waiting_to_departure.remove(airplane)

    # przypisanie samolotów do pasów lotniczych jeśi możliwe
    for airplane in simulation_schedule.list_of_planes:
        if airplane.arrival == current_time and not airplane.if_emergency:
            available_runway = simulation_Airport.check_runways_occupation()
            if available_runway != -1 and len(
                    simulation_Airport.planes_currently_on_the_airport) < simulation_Airport.max_number_of_planes_on_ground:
                simulation_Airport.new_plane_on_runway(available_runway, airplane, "arrival", current_time)
            else:
                simulation_Airport.list_planes_waiting_to_land.append(airplane)

    # sprawdzenie czy są samoloty do odlotu i przypisanie do pasa
    # jeśli samolot trafia na pas, to zmniejsza się licznik samolotów na lotnisku

    for airplane in simulation_Airport.planes_currently_on_the_airport:
        #print(f"sprawdzenie gotowości do odlotu, samolot {airplane}")
        if airplane.actual_departure == current_time:
            available_runway = simulation_Airport.check_runways_occupation()
            if available_runway != -1:
                simulation_Airport.new_plane_on_runway(available_runway, airplane, "departure", current_time)
            else:
                simulation_Airport.list_planes_waiting_to_departure.append(airplane)
            simulation_Airport.planes_currently_on_the_airport.remove(airplane)

    # zakończono wszystkie czynności związane z obsługą samolotów, zatem następuje aktualizacja czasu
    current_time_minutes += 1
    if current_time_minutes == 60:
        current_time_hours += 1
        current_time_minutes = 0

    current_time = current_time_hours * 100 + current_time_minutes

    # zmiana liczników czasowych dla runways_occupation

    # Sprawdzenie czy samolot, który był na pasie nie opuścił go; jeśli przyleciał - zwiększyć licznik samolotów na
    # lotnisku i dodać samolot do listy samolotów na lotnisku

    for runway_nr in simulation_Airport.runways_occupation.keys():
        if simulation_Airport.runways_occupation[runway_nr][1] != '':
            simulation_Airport.runways_occupation[runway_nr][0] -= 1

            if simulation_Airport.runways_occupation[runway_nr][0] == 0:
                if simulation_Airport.runways_occupation[runway_nr][2] == "arrival":
                    simulation_Airport.planes_currently_on_the_airport.append(
                        simulation_Airport.runways_occupation[runway_nr][1])

                counter = simulation_Airport.runways_occupation[runway_nr][3]
                simulation_Airport.runways_occupation[runway_nr] = [0, '', '', counter]

# ---------------------- Podsumowanie i wizualizacja przebiegu symulacji ----------------------------

# Wyświetlenie ponownie harmonogramu wraz z aktualizacją rzeczywistych godzin przylotu
print(f"End of simulation{nl}")
simulation_schedule.print_data()

# Zaznaczenie na osi czasu kiedy jaki samolot przyleciał i wyleciał

fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)
plt.grid()

for airplane in simulation_schedule.list_of_planes:
    ax1.scatter([airplane.arrival, airplane.departure], [airplane.id, airplane.id],
                label=f'Samolot {airplane.id}')
    ax2.scatter([airplane.actual_arrival, airplane.actual_departure], [airplane.id, airplane.id],
                label=f'Samolot {airplane.id}')
    if airplane.if_emergency:
        arrow = FancyArrowPatch((airplane.arrival - 500, airplane.id), (airplane.arrival - 50, airplane.id),
                                arrowstyle='-|>,head_width=.2', mutation_scale=20, color="black")
        ax1.add_patch(arrow)

ax1.set_title("Harmonogram godzin przylotu i wylotu samolotów")
ax2.set_title("Rzeczywiste godziny przylotu i wylotu samolotów")

ax1.set_ylabel('ID Samolotu', fontsize=12)
ax1.set_xlabel('Czas', fontsize=12)
ax2.set_ylabel('ID Samolotu', fontsize=12)
ax2.set_xlabel('Czas', fontsize=12)

#fig.suptitle('Wykres punktowy godzin przylotu i wylotu samolotów')
ax1.legend()
ax1.grid(True)
ax2.grid(True)
plt.show()

# Wykres opóźnień samolotów
x = ['Opóźnienie w przylotach', 'Opóźnienie w wylotach']
y_col = []
botom_next_bars = list(np.zeros(2))

for airplane in simulation_schedule.list_of_planes:
    o_przylotu = time_difference(airplane.arrival, airplane.actual_arrival)
    o_wylotu = time_difference(airplane.departure, airplane.actual_departure)
    if o_przylotu > 0 or o_wylotu > 0:
        plt.bar(x, [o_przylotu, o_wylotu], bottom=botom_next_bars, label=f'Samolot {airplane.id}')
        botom_next_bars = [o_przylotu + botom_next_bars[0], o_wylotu + botom_next_bars[1]]

l = plt.legend()
if len(l.get_texts()) == 0:
    plt.xticks(np.arange(0, 4, 1), ["", 'Opóźnienie przylotów', 'Opóźnienie wylotów', ""])
else:
    plt.legend()

plt.ylabel('Czas opóźnienia [min]')
plt.show()

# Wykres użycia pasów startowych
fig, ax = plt.subplots()
y_bar = 1
y_labels = []
y_labels_points = []

for runway_nr in simulation_Airport.runways_occupation.keys():
    data_to_plot = []
    colors_available = ('tab:orange', 'tab:green')
    bars_colors = []
    for registered_flight in simulation_Airport.list_runways_occupation:
        if registered_flight[0] == runway_nr:
            data_to_plot.append((registered_flight[1], registered_flight[2]))
            if registered_flight[4] == "arrival":
                bars_colors.append(colors_available[0])
            else:
                bars_colors.append(colors_available[1])
    ax.broken_barh(data_to_plot, (y_bar, 2), facecolors=tuple(bars_colors))
    y_bar = y_bar + 3
    y_labels.append(f'Pas nr {runway_nr}')
    y_labels_points.append(y_bar - 2)

ax.set_ylim(0, y_bar)
ax.set_xlim(0, 2500)
ax.set_xlabel('Czas', fontsize=12)
ax.set_yticks(y_labels_points, labels=y_labels)

legend_elements = [Patch(facecolor='orange', edgecolor='orange', label='Samoloty lądujące'),
                   Patch(facecolor='green', edgecolor='green', label='Samoloty odlatujące')]

ax.legend(handles=legend_elements, loc='upper right')
plt.show()
