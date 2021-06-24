# Source https://dc.etsu.edu/cgi/viewcontent.cgi?article=4651&context=etd
# Lauren Holden
import simpy
import numpy as np
import math
from itertools import repeat
from random import seed
from random import randint



class P:
    externalToDRMean = 1/2
    DRorderLotSize = 10
    externalToBUMean = 5/60
    BUorderLotSize = 20
    Q_1 = 100
    Q_2 = 20
    ROP_BU = 20 + (200/30) * 7
    ROP_DR = 10 + (150/30) * 2
    LT_1 = 7
    LT_2 = 2
    simulationTimeMax = 12 * 30

class S:
    Inv = None
    DRwaits = []
    BUwaits = []
    nBUCustomers = 0
    nDRCustomers = 0
    BU_Dem_day = list(repeat(0,P.simulationTimeMax))
    DR_Dem_day = list(repeat(0,P.simulationTimeMax))

class Inventory:
    def __init__ (self,env):
        self.env = env
        self.BU_inv = simpy.Container(env ,init = P.ROP_BU)
        self.DR_inv = simpy.Container(env ,init = P.ROP_DR)
        self.mon_procBU = env.process(self.monitor_BU_inv(env))
        self.mon_procDR = env.process(self.monitor_DR_inv(env))


    def monitor_BU_inv(self ,env):
        while True:
            if self.BU_inv.level <= P.ROP_BU:
                print ("Time {0}: BU inventory reached ROP: BU places replenishment order".format (self.env.now))
                yield self.env.timeout(P.LT_1)
                print ("Time {0}: BU replenishment inventory arrives".format(self.env.now))
                yield self.BU_inv.put(P.Q_1)
                print ("Time {0}: BU replenishment order is added to inventory".format(self.env.now))
                yield self.env.timeout(1)


    def monitor_DR_inv(self ,env ):
        while True :
            if self.DR_inv.level <= P.ROP_DR:
                print("Time {0}: DR inventory reached ROP: DR places replenishment order to BU".format(self.env.now))
                yield self.BU_inv.get(P.Q_2)
                print ("Time {0}: BU fills DR replenishment request".format(self.env.now))
                yield self.env.timeout(P.LT_2)
                print ("Time {0}: DR replenishment inventory arrives from BU".format(self.env.now))
                yield self.DR_inv.put(P.Q_2)
                print ("Time {0}: DR replenishment order is added to inventory".format(self.env.now))
                yield self.env.timeout(1)


class DRCustomer(object):
    def init(self , env , name = '' ):
        self.env = env
        self.action = self.env.process(self.ordertoDR())
        if ( name == '' ):
            self.name = 'RandomDRCustomer' + str(randint(100))
        else:
            self.name = name


    def DRorderToBU(self):
        print("Time {1}: DR places order to BU to fill order for {0}".format(self.name , self.env.now))
        yield S.Inv.BU_inv.get(P.DRorderLotSize)
        yield self.env.timeout(P.LT_2)
        yield S.Inv.DR_inv.put(P.DRorderLotSize)

    def ordertoDR(self):
        startTime_DR = self.env.now
        j = math.floor(self.env.now)
        S.DR_Dem_day[j] += 1
        print("Time {1}: {0} places order to DR".format(self.name ,self.env.now))
        if S.Inv.DR_inv.level < P. DRorderLotSize :
            self.env.process(self.DRorderToBU())
        yield S.Inv.DR_inv.get(P.DRorderLotSize)
        print("Time {1}: {0} receives order from DR".format(self.name , self.env.now))
        waitTime_DR = self.env.now - startTime_DR
        print("{0} had to wait {1} days".format(self.name ,waitTime_DR))
        S.DRwaits.append(waitTime_DR)

class BUCustomer(object):
    def __init__ (self, env , name = '' ) :
        self.env = env
        self.action = self.env.process(self.ordertoBU())
        if (name == '' ):
            self.name = 'RandomBUCustomer'+ str(randint(100))
        else:
            self.name = name

    def ordertoBU (self):
        startTime_BU = self.env.now
        i = math.floor(self.env.now)
        S.BU_Dem_day[i] += 1
        print("Time {1}: {0} places order to BU".format(self.name , self.env.now))
        yield S.Inv.BU_inv.get(P.BUorderLotSize)
        print ("Time {1}: {0} receives order".format (self.name , self.env.now))
        waitTime_BU = self.env.now - startTime_BU
        print("{0} had to wait {1} days".format(self.name ,waitTime_BU))
        S.BUwaits.append(waitTime_BU)


class DROrderProcessor(object):
    def __init__(self , env , DRlambda):
        self.env = env
        self.action = env.process(self.DREntrance())
        self.lam = DRlambda

    def DREntrance (self):
        while True :
            interarrivalTime_DR = 1 #np.exp( 1/P.externalToDRMean)
            yield self.env.timeout(interarrivalTime_DR)
            c = DRCustomer(self. env , name = "DRCustomer {0}".format (S.nDRCustomers))
            S.nDRCustomers += 1

class BUOrderProcessor(object):
    def __init__(self , env , BUlambda) :
        self.env = env
        self.action = env.process(self.BUEntrance())
        self.lam = BUlambda

    def BUEntrance(self):
        while True :
            interarrivalTime_BU = 1 #np.exp(1/P.externalToBUMean)
            yield self.env.timeout( interarrivalTime_BU)
            c = BUCustomer(self.env , name = "BUCustomer {0}".format(S.nBUCustomers))
            S.nBUCustomers += 1

def model(randomSeed = 123):
    seed(randomSeed)
    S.DRwaits = []
    S.BUwaits = []
    envr = simpy.Environment()
    BU = BUOrderProcessor( envr , BUlambda = P. externalToBUMean)
    DR = DROrderProcessor( envr , DRlambda = P. externalToDRMean)
    S.Inv = Inventory(envr)
    envr.run(until = P.simulationTimeMax)
    return S.DRwaits , S.BUwaits , S.BU_Dem_day , S.DR_Dem_day , S.nBUCustomers , S.nDRCustomers


model()
