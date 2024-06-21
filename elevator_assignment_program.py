import random
import signal
import sys
import time
import threading
from collections import defaultdict, deque

class Elevator:
    def __init__(self, id, initial_floor):
        self.id = id
        self.initial_floor = initial_floor
        self.current_floor = initial_floor
        self.direction = None  # 'up' or 'down'
        self.requests = deque()
        self.lock = threading.Lock()
        self.active = True

    def move_to(self, floor):
        print(f"{self.id} moving from {self.current_floor} to {floor}")
        self.current_floor = floor
        print(f"{self.id} reached {floor}")

    def set_direction(self, direction):
        self.direction = direction

    def add_request(self, floor):
        with self.lock:
            self.requests.append(floor)
            print(f"{self.id} added request to {floor}. Current requests: {list(self.requests)}")

    def process_requests(self):
        while self.active:
            with self.lock:
                if self.requests:
                    next_floor = self.requests.popleft()
                    print(f"{self.id} servicing floors: {list(self.requests)}. Currently going to floor {next_floor} from floor {self.current_floor}")
                    self.move_to(next_floor)
                    print(f"{self.id} reached {next_floor}.")
                else:
                    if self.current_floor != self.initial_floor:
                        print(f"{self.id} not servicing any floors, moving to resting floor {self.initial_floor}.")
                        self.move_to(self.initial_floor)
                        print(f"{self.id} reached resting floor {self.initial_floor}.")
                    self.direction = None
            time.sleep(1)  # Check for new requests every second

    def display_requests(self):
        with self.lock:
            if self.requests:
                print(f"{self.id} servicing floors: {list(self.requests)}")
            else:
                print(f"{self.id} has no pending requests.")

    def stop(self):
        self.active = False

class ElevatorSystem:
    def __init__(self, num_floors, num_elevators):
        self.num_floors = num_floors
        self.floors = ["Parking"] + [str(i) for i in range(1, num_floors + 1)]
        self.elevators = [Elevator(f'Elevator {i+1}', self.floors[i * (num_floors // num_elevators)]) for i in range(num_elevators)]
        for elevator in self.elevators:
            elevator.floors = self.floors  # Share the floors list with each elevator instance
        self.elevator_requests = defaultdict(list)
        self.running = True
        self.lock = threading.Lock()

    def determine_direction(self, current_floor, destination_floor):
        current_index = self.floors.index(current_floor)
        destination_index = self.floors.index(destination_floor)
        if destination_index > current_index:
            return "up"
        else:
            return "down"

    def add_request(self, current_floor, destination_floor):
        direction = self.determine_direction(current_floor, destination_floor)
        with self.lock:
            self.elevator_requests[current_floor].append((destination_floor, direction))
        print(f"Added request from {current_floor} to {destination_floor}. Direction: {direction}")

    def find_best_elevator(self, current_floor, direction):
        best_elevator = None
        minimum_time = float('inf')

        for elevator in self.elevators:
            if elevator.direction == direction or elevator.direction is None:
                time_to_reach = abs(self.floors.index(elevator.current_floor) - self.floors.index(current_floor))
                if time_to_reach < minimum_time:
                    minimum_time = time_to_reach
                    best_elevator = elevator

        print(f"Best elevator for floor {current_floor} in direction {direction} is {best_elevator.id if best_elevator else 'None'}")
        return best_elevator

    def assign_elevator(self, current_floor, destination_floor):
        direction = self.determine_direction(current_floor, destination_floor)
        best_elevator = self.find_best_elevator(current_floor, direction)
        
        if best_elevator:
            best_elevator.move_to(current_floor)
            best_elevator.set_direction(direction)
            best_elevator.add_request(destination_floor)
            print(f"Assigned {best_elevator.id} to floor {current_floor} for direction {direction}")
            best_elevator.display_requests()
        else:
            print(f"No available elevator for request from {current_floor} to {destination_floor}.")

    def process_requests(self):
        while self.running:
            with self.lock:
                for floor, requests in list(self.elevator_requests.items()):
                    for destination_floor, direction in requests:
                        self.assign_elevator(floor, destination_floor)
                        self.elevator_requests[floor].remove((destination_floor, direction))
            time.sleep(1)  # Adjust the frequency as needed

    def start_elevators(self):
        for elevator in self.elevators:
            threading.Thread(target=elevator.process_requests).start()
        threading.Thread(target=self.process_requests).start()

    def simulate_users(self, num_users):
        for _ in range(num_users):
            current_floor = random.choice(self.floors)
            destination_floor = random.choice(self.floors)
            while destination_floor == current_floor:
                destination_floor = random.choice(self.floors)
            print(f"User request: From {current_floor} to {destination_floor}")
            self.add_request(current_floor, destination_floor)

    def stop(self):
        self.running = False
        for elevator in self.elevators:
            elevator.stop()
        print("Stopping elevator system gracefully...")

def signal_handler(sig, frame):
    system.stop()
    sys.exit(0)

if __name__ == "__main__":
    num_floors = 50
    num_elevators = 4
    num_users = 10

    system = ElevatorSystem(num_floors, num_elevators)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start monitoring elevators
    system.start_elevators()

    # Simulate initial users
    system.simulate_users(num_users)

    # Main thread for user input
    while True:
        try:
            user_input = input("Enter request as 'current_floor requested_floor' or type 'exit' to quit: ").strip()
            if user_input.lower() == 'exit':
                system.stop()
                break
            current_floor, destination_floor = user_input.split()
            if current_floor in system.floors and destination_floor in system.floors:
                system.add_request(current_floor, destination_floor)
            else:
                print("Invalid floor entered. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Please enter the request in the correct format.")
