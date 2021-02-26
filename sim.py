import random
import simpy

RANDOM_SEED = 42
NUM_PEOPLE = 10  # number of people
ARRIVED_INTERVAL = (1, 5)  # person arrival time interval to another person
STAY_TIME = (2, 30)  # person stay time

wait_times = []
stay_times = []

def my_print(*x):
    print(*x)

# generate person
def source(env, number, interval, counter):
    arrived_inter_time = [random.randint(*interval) for i in range(number)]
    arrived_time = [sum(arrived_inter_time[:i+1]) for i in range(len(arrived_inter_time))]
    my_print("arrival time:", arrived_time)
    for i in range(number):
        c = person(env, ' '*i*4 + 'PERSON%02d' % i, counter, arrived_time[i])
        env.process(c)
    yield env.timeout(0)

def person(env, name, shelter, arrived_time):
    yield env.timeout(arrived_time)  # arrive
    my_print(name, 'arrival time:', env.now)
    with shelter.request() as req:  # enter
        yield req
        my_print(name, 'enter time:', env.now)
        stay_time = random.randint(*STAY_TIME)
        wait_time = env.now - arrived_time
        yield env.timeout(stay_time)
        my_print(name, 'out time:', env.now)
        wait_times.append(wait_time/NUM_PEOPLE)
        stay_times.append(stay_time/NUM_PEOPLE)

ans = []
for i in range(1):
    wait_times.clear()
    stay_times.clear()
    # Setup and start the simulation
    # random.seed(RANDOM_SEED)
    env = simpy.Environment()

    # Start processes and run
    shelter = simpy.Resource(env, capacity=3)
    env.process(source(env, NUM_PEOPLE, ARRIVED_INTERVAL, shelter))
    env.run()

    ans.append(sum(wait_times))

print("average wait days =", sum(ans) / len(ans))