import numpy as np

def globalStart(objective_rule,T,discount_factor,discretization_tuple):
    
    #Global Variables
    C=5
    K=5
    A=2
    B=1
    P_NEW_B1 = [0.]*K
    P_NEW_B2 = [0.]*K
    STATE_NEW_B1 = [0] * K
    STATE_NEW_B2 = [0] * K
    flag_discrete_B1 = [False] * K
    flag_discrete_B2 = [False] * K
    
    #Discretization
    block_idx , layer_idx = discretization_tuple
    if block_idx == 1:
        flag_discrete_B1[layer_idx] = True
    elif block_idx == 2:
        flag_discrete_B2[layer_idx] = True
    #Initial Pertubation
    P_NEW_B1[0] = 1.

    #move forward one step
    def iterate(P_NEW_B1,P_NEW_B2,STATE_NEW_B1,STATE_NEW_B2):
        U_NEW_B1 = [0.] * K
        U_OLD_B1 = [0.] * K
        U_NEW_B2 = [0.] * K
        U_OLD_B2 = [0.] * K
        #Utility Computation
        for i in range(K):
            if i!=0:
                # Has Left Neighbor
                right_disc_B1 = flag_discrete_B1[i-1]
                U_NEW_B1[i] += (A*C*(STATE_NEW_B1[i-1])) if right_disc_B1 else (A*C*P_NEW_B1[i-1])
                U_OLD_B1[i] += (B*C*(1-STATE_NEW_B1[i-1])) if right_disc_B1 else (B*C*(1-P_NEW_B1[i-1]))
                right_disc_B2 = flag_discrete_B2[i-1]
                U_NEW_B2[i] += (A*C*STATE_NEW_B2[i-1]) if right_disc_B2 else (A*C*P_NEW_B2[i-1])
                U_OLD_B2[i] += (B*C*(1-STATE_NEW_B2[i-1])) if right_disc_B2 else (B*C*(1-P_NEW_B2[i-1]))

            if i!=K-1:
                # Has Right Neighbor
                right_disc_B1 = flag_discrete_B1[i+1]
                U_NEW_B1[i] += (A*C*(STATE_NEW_B1[i+1])) if right_disc_B1 else (A*C*P_NEW_B1[i+1])
                U_OLD_B1[i] += (B*C*(1-STATE_NEW_B1[i+1])) if right_disc_B1 else (B*C*(1-P_NEW_B1[i+1]))
                right_disc_B2 = flag_discrete_B2[i+1]
                U_NEW_B2[i] += (A*C*STATE_NEW_B2[i+1]) if right_disc_B2 else (A*C*P_NEW_B2[i+1])
                U_OLD_B2[i] += (B*C*(1-STATE_NEW_B2[i+1])) if right_disc_B2 else (B*C*(1-P_NEW_B2[i+1]))


        #Normalization
        for i in range(K):
            if not flag_discrete_B1[i]:
                P_NEW_B1[i] = (P_NEW_B1[i]+U_NEW_B1[i])/float(1+U_NEW_B1[i]+U_OLD_B1[i])
            else:
                STATE_NEW_B1[i] = (1 if U_NEW_B1[i]>=U_OLD_B1[i] else 0)
            if not flag_discrete_B2[i]:
                P_NEW_B2[i] = (P_NEW_B2[i]+U_NEW_B2[i])/float(1+U_NEW_B2[i]+U_OLD_B2[i]) 
            else: 
                STATE_NEW_B2[i] = (1 if U_NEW_B2[i]>=U_OLD_B2[i] else 0)
        #return money earned in this round
        return len(filter(lambda x:x>=0.5,P_NEW_B1+P_NEW_B2))+sum(STATE_NEW_B1+STATE_NEW_B2)
    #objective calculation
    total_money = 0.
    if (objective_rule==1):
        #Finite T horizon
        for t in range(T):
            local_money = iterate(P_NEW_B1,P_NEW_B2,STATE_NEW_B1,STATE_NEW_B2)
            total_money += local_money
        return total_money

    elif (objective_rule==2):
        #Finite T discounted horizon + geometric sum toward infinity (Supposed to be added manually outside the function)
        cumulative_discount = 1.
        # Finite T round to supposed convergene
        for t in range(T):
            local_money = iterate(P_NEW_B1,P_NEW_B2,STATE_NEW_B1,STATE_NEW_B2)
            total_money += local_money * cumulative_discount
            cumulative_discount *= discount_factor 
        return total_money 

#Strategy 1 only discretize the 
def strategy1(obj_rule,T,discount_factor):
    return globalStart(obj_rule,T,discount_factor,(2,0))

def strategy2(obj_rule,T,discount_factor,layer_idx):
    return globalStart(obj_rule,T,discount_factor,(1,layer_idx))

print "trying strategy 1"
print strategy1(1,50,0.95)

print "trying strategy 2"
print strategy2(1,50,0.95,2)
