#tutorial  https://www.youtube.com/watch?v=G2WftFiBRFg&list=PL2Wg3oyN-jmMD39JFqejZAzi06BWo_uJa&index=5

import simpy
import matplotlib.pyplot as plt
import numpy as np

def factory_run(env, repairers, spares):
    global cost 
    cost = 0.0
    for i in range(50):
        env.process(operate_machine(env,repairers,spares))
    while True:
        cost += 3.75 * 8 * repairers.capacity + 30 * spares.capacity
        yield env.timeout(8.0)

def operate_machine(env, repairers, spares):
    global cost
    while True:
        yield env.timeout(generate_time_to_failure())
        t_broken = env.now
        #print("{:.2f} machine broke".format(t_broken))
        env.process(repair_machine(env, repairers, spares))
        yield spares.get(1)
        t_replaced = env.now
        #print("{:.2f} machine replaced".format(t_replaced))
        cost += 20*(t_replaced-t_broken)

def repair_machine(env, repairers, spares):
    with repairers.request() as request:
        yield request
        yield env.timeout(generate_time_to_repair())
        yield spares.put(1)
    print("{:.2f} repair complete".format(env.now))

def generate_time_to_failure():
    return np.random.uniform(132,182)

def generate_time_to_repair():
    return np.random.uniform(4,10)

obs_time = []
obs_cost = []
obs_spares = []

def observe(env, spares):
    while True:
        obs_time.append(env.now)
        obs_cost.append(cost)
        obs_spares.append(spares.level)
        yield env.timeout(1.0)

np.random.seed(0)

env = simpy.Environment()

repairers = simpy.Resource(env,capacity=3)

spares = simpy.Container(env, init=20, capacity=20)

env.process(factory_run(env, repairers, spares))

env.process(observe(env, spares))

print("Start Simulation")

env.run(until=8*5*52)

plt.figure()
plt.step(obs_time, obs_spares, where = 'post')
plt.xlabel("time (hours)")
plt.ylabel("spares Level")


plt.figure()
plt.step(obs_time, obs_cost, where = 'post')
plt.xlabel("time (hours)")
plt.ylabel("cost")

plt.show()





