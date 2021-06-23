# tutorial https://www.youtube.com/watch?v=oJyf8Q0KLRY&list=PL2Wg3oyN-jmMD39JFqejZAzi06BWo_uJa&index=3
import numpy as np

class Simulation:
    def __init__(self):
        self.num_in_system = 0

        self.clock = 0.0
        self.t_arrival = self.generate_interarrival()
        self.t_depart = float('inf')

        self.num_arrivals = 0 
        self.num_departs = 0
        self.total_wait = 0.0



    def advance_time(self):
        t_event = min(self.t_arrival, self.t_depart)
        
        self.total_wait += self.num_in_system * (t_event - self.clock)

        self.clock = t_event

        if self.t_arrival <= self.t_depart:
            self.handle_arrival_event()
        else:
            self.handle_depart_event()

    def handle_arrival_event(self):
        self.num_in_system += 1
        self.num_arrivals += 1
        if self.num_in_system <= 1:
            self.t_depart = self.clock + self.generate_service()
        self.t_arrival = self.clock + self.generate_interarrival()
        
    def handle_depart_event(self):
        self.num_in_system -= 1
        self.num_departs += 1
        if self.num_in_system > 0:
            self.t_depart = self.clock + self.generate_service()
        else:
            self.t_depart = float('inf')



    def generate_interarrival(self):
        return np.random.exponential(1./3)

    def generate_service(self):
        return np.random.exponential(1./4)

np.random.seed(0)

s = Simulation()


for i in range (100):
    s.advance_time()

    print("Time - " + str(i))
    print(s.num_arrivals)
    print(s.num_departs)
    print(s.num_in_system)
    print(s.total_wait)