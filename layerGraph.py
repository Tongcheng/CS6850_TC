import numpy as np
import matplotlib.pyplot as plt

def globalStart(objective_rule,T,discount_factor,discretization_tuple):
    
    #Global Variables
    C=5
    K=global_K
    A=3
    B=1
    p_inter = 0.01
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
        #Block 2 layer 0 is special
        for i in range(K):
            disc_B1 = flag_discrete_B1[i]
            U_NEW_B2[0] += A*p_inter*C*(STATE_NEW_B1[i] if disc_B1 else P_NEW_B1[i])
            U_OLD_B2[0] += B*p_inter*C*((1-STATE_NEW_B1[i]) if disc_B1 else (1-P_NEW_B1[i]))

        #Normalization
        for i in range(K):
            if not flag_discrete_B1[i]:
                P_NEW_B1[i] = (P_NEW_B1[i]+U_NEW_B1[i])/float(1+U_NEW_B1[i]+U_OLD_B1[i])
                STATE_NEW_B1[i] = 0
            else:
                STATE_NEW_B1[i] = (1 if U_NEW_B1[i]>=U_OLD_B1[i] else 0)
                P_NEW_B1[i] = 0.
            if not flag_discrete_B2[i]:
                P_NEW_B2[i] = (P_NEW_B2[i]+U_NEW_B2[i])/float(1+U_NEW_B2[i]+U_OLD_B2[i]) 
                STATE_NEW_B2[i] = 0
            else: 
                STATE_NEW_B2[i] = (1 if U_NEW_B2[i]>=U_OLD_B2[i] else 0)
                P_NEW_B2[i] = 0.
 
        #return money earned in this round
        output_cont = len(filter(lambda x:x>=0.5,P_NEW_B1+P_NEW_B2)) 
        output_disc = sum(STATE_NEW_B1+STATE_NEW_B2)
        output_money= output_cont + output_disc
        return C*(2*K-output_money)

    #objective calculation
    total_money = 0.
    total_money_L = [total_money]
    if (objective_rule==1):
        #Finite T horizon
        for t in range(T):
            local_money = iterate(P_NEW_B1,P_NEW_B2,STATE_NEW_B1,STATE_NEW_B2)
            total_money += local_money
            total_money_L.append(total_money)
        print STATE_NEW_B1
        print STATE_NEW_B2
        print P_NEW_B1
        print P_NEW_B2 

        return total_money, total_money_L

    elif (objective_rule==2):
        #Finite T discounted horizon + geometric sum toward infinity (Supposed to be added manually outside the function)
        cumulative_discount = 1.
        # Finite T round to supposed convergene
        for t in range(T):
            local_money = iterate(P_NEW_B1,P_NEW_B2,STATE_NEW_B1,STATE_NEW_B2)
            total_money += local_money * cumulative_discount
            cumulative_discount *= discount_factor 
            total_money_L.append(total_money)
        print STATE_NEW_B1
        print STATE_NEW_B2 
        print P_NEW_B1
        print P_NEW_B2 

        return total_money, total_money_L 

#Strategy 1 only discretize the 
def strategy1(obj_rule,T,discount_factor):
    return globalStart(obj_rule,T,discount_factor,(2,0))

def strategy2(obj_rule,T,discount_factor,layer_idx):
    return globalStart(obj_rule,T,discount_factor,(1,layer_idx))

global_K = 3
global_T = 20
global_criterion = 2
global_discount = 0.3
print "trying strategy 1"
handleList = []
end1,path1 = strategy1(global_criterion,global_T,global_discount)
handle_local1, = plt.plot(range(len(path1)),path1,label="strategy 1")
handleList.append(handle_local1)

for disc_idx in range(1,global_K):
  print "trying strategy 2"
  end2,path2 = strategy2(global_criterion,global_T,global_discount,disc_idx)
  handle_local2, = plt.plot(range(len(path2)),path2,label="strategy 2, discIdx="+`disc_idx`)
  handleList.append(handle_local2)
plt.legend(handles=handleList)
plt.show()
