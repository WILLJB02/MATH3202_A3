from itertools import combinations

# Data
# Zones in CCD25
Z = range(9)

#Facilities in Pacific Paradise
Facilities = [
    'School',
    'Police Station',
    'Bus Depot',
    'Town Hall',
    'Post Office',
    'Government Office',
    'Hospital',
    'Library',
    'Bank',
    'Medical Centre',
    'Fire Station',
    'Supermarket',
    'Convenience Store',
    'Wedding Chapel',
    'Ambulance',
    'Hotel'
]

#Facilities Located in Each Zone
Zone_Facilities = [
    [5,12],
    [4,9,13],
    [7,8,10,15],
    [0,2,5,8],
    [0,1,12,14],
    [0,3,6,14,15],
    [1,7,11],
    [2,15],
    [10,11]
]

# Neighbooring Zones of Each Zone
Zone_NBR = [
    [3],
    [2,6],
    [1,3,7],
    [0,2,4,8],
    [3],
    [6],
    [1,5,7],
    [2,6,8],
    [3,7]
]

# List of Priority Facilities
Priority = [6, 3, 14, 11]

# Transition Funciton
# The State is a 9-tuple where each element is
# -1 = outbreak, 0 = normal, 1 = protected
# NextStates returns a list of tuples with a probability
# in position 0 and a State as a tuple in position 1
def NextStates(State, OutbreakProb):
    ans = []
    # Z0 are the normal Zone_Facilities
    Z0 = [j for j in Z if State[j]==0]
    n = len(Z0)
    for i in range(n+1):
        for tlist in combinations(Z0, i):
            p = 1.0
            slist = list(State)
            for j in range(n):
                if Z0[j] in tlist:
                    p *= OutbreakProb[Z0[j]]
                    slist[Z0[j]] = -1
                else:
                    p *= 1-OutbreakProb[Z0[j]]
            ans.append((p, tuple(slist)))
    return ans


# Communication 12
# Function which calulates the number of disinct facilities that are protected
# and hence accesible based upon the state of zones in Pacific Paradise.
def DistinctFacilities(State):
    distinct = []
    for z in Z:
        if State[z] == 1:
            for facility in Zone_Facilities[z]:
                if facility not in distinct:
                    distinct.append(facility)
    return len(distinct)

# Protection Order as per Communication 12
Order = [5,4,3,2,6,1,8,7,0]

# Implementation of Value Function
_comm12 = {}
def comm12(State):
    # checking if all zones are infected of protected
    Normal = []
    for z in Z:
        if State[z] == 0:
            Normal.append(z)
    # evaluating base case
    if len(Normal) == 0:
        return DistinctFacilities(State)
    else:
        # determining first zone in the order that has not been infected or protected. 
        for z in Order:
            if z in Normal:
                break;
        # determining "all possible S_(t+1)"   
        New_State = State[:z]+(1,)+State[z+1:]
        Next_States = NextStates(New_State, [0.2 for z in Z])
        Expected_Value = 0
        # evaluting value function
        for NS in Next_States:
            Expected_Value = Expected_Value + NS[0]*comm12(NS[1])
    return Expected_Value


# Communication 13
_comm13 = {}
def comm13(State):
    # checking if all zones are infected of protected
    Normal = []
    for z in Z:
        if State[z] == 0:
            Normal.append(z)
    # evaluating base case
    if len(Normal) == 0:
        return (DistinctFacilities(State), None)
    else:
        Expected_Values = []
        if State not in _comm13:
            # iterating over all possible actions
            for n in Normal:
                # determining "all possible S_(t+1)" 
                New_State = State[:n]+(1,)+State[n+1:]
                Next_States = NextStates(New_State, [0.2 for z in Z])
                Expected_Value = 0
                # evaluating value function
                for NS in Next_States:
                    Expected_Value = Expected_Value + NS[0]*comm13(NS[1])[0]
                Expected_Values.append((Expected_Value, n))
            # taking maximum 
            _comm13[State] = max(Expected_Values)
        return _comm13[State]

# Function which can be used to dispaly the optimal strategy.
# Prev_zones - list of zones which have been protected
# Filter-Out - list of actions which you want to filter out from ouput
# Infected - list the zones which must be infected in output
def comm13_plan(prev_zones, filter_out, infected):
    t = len(prev_zones)
    states = []
    for k in _comm13:
        protected = 0
        for z in k:
            if z == 1:
                protected = protected + 1
        output = True
        for PZ in prev_zones:
            if k[PZ] != 1:
                output = False
        for i in infected:
            if k[i] != -1:
                output = False
        if protected == t and output == True:
            states.append((k.count(-1), _comm13[k][0], _comm13[k][1], k))
    states.sort()
    for s in states:
        if s[2] not in filter_out:
            I = []
            for z in Z:
                if s[3][z] == -1:
                    I.append(z) 
            print('{0:<10} {1:<10} {2:<20} {3}'.format(round(s[1], 2), s[2], str(I), s[3]))

 

# Communication 14
# Function which calcualtes the probability of an outbreak occuring in each zone
# given the number of neighbooring zones that are infected.
def Outbreak_Probability(State):
    p = []
    for z in Z:
        outbreaks = 0
        for NBR in Zone_NBR[z]:
            if State[NBR] == -1:
                outbreaks = outbreaks + 1
        p.append(0.2+0.05*outbreaks)
    return p
       

_comm14 = {}
def comm14(State):
    # checking if all zones are infected of protected
    Normal = []
    for z in Z:
        if State[z] == 0:
            Normal.append(z)
    # evaluating base case
    if len(Normal) == 0:
        return (DistinctFacilities(State), None)
    else:
        Expected_Values = []
        if State not in _comm14:
            # iterating over all possible actions
            for n in Normal:
                # determining "all possible S_(t+1)" 
                New_State = State[:n]+(1,)+State[n+1:]
                Next_States = NextStates(New_State, Outbreak_Probability(New_State))
                Expected_Value = 0
                # evaluating value function
                for NS in Next_States:
                    Expected_Value = Expected_Value + NS[0]*comm14(NS[1])[0]
                Expected_Values.append((Expected_Value, n))
            # taking maximum 
            _comm14[State] = max(Expected_Values)
        return _comm14[State]
    
# Same as above except for comm14
def comm14_plan(prev_zones, filter_out, infected):
    t = len(prev_zones)
    states = []
    for k in _comm14:
        protected = 0
        for z in k:
            if z == 1:
                protected = protected + 1
        output = True
        for PZ in prev_zones:
            if k[PZ] != 1:
                output = False
        for i in infected:
            if k[i] != -1:
                output = False
        if protected == t and output == True:
            states.append((k.count(-1), _comm14[k][0], _comm14[k][1], k))
    states.sort()
    for s in states:
        if s[2] not in filter_out:
            I = []
            for z in Z:
                if s[3][z] == -1:
                    I.append(z) 
            print('{0:<10} {1:<10} {2:<20} {3}'.format(round(s[1], 2), s[2], str(I), s[3]))

#Communication 15
# Function which determines whether all priority facilities are accesable
# given the state 
def priority_accessible(State):
    access = 0
    for facility in Priority:
        for z in Z:
            if State[z] == 1 and facility in Zone_Facilities[z]:
                access = access + 1
                break
    if access == 4:
        return True
    return False

_comm15 = {}
def comm15(State):
    # checking if all zones are infected of protected
    Normal = []
    for z in Z:
        if State[z] == 0:
            Normal.append(z)
    access = priority_accessible(State)
    # evaluating base case
    if access == True:
        return (1, None)
    elif len(Normal) == 0 and access == False:
        return (0, None)
    else:
        Probs = []
        if State not in _comm15:
            # iterating over all possible actions
            for n in Normal:
                 # determining "all possible S_(t+1)" 
                New_State = State[:n]+(1,)+State[n+1:]
                Next_States = NextStates(New_State, Outbreak_Probability(New_State))
                p = 0
                 # evaluating value function
                for NS in Next_States:
                    p = p + NS[0]*comm15(NS[1])[0]
                Probs.append((p, n))
            # taking maximum 
            _comm15[State] = max(Probs)
        return _comm15[State]
    
# Same as above except for comm15
def comm15_plan(prev_zones, filter_out, infected):
    t = len(prev_zones)
    states = []
    for k in _comm15:
        protected = 0
        for z in k:
            if z == 1:
                protected = protected + 1
        output = True
        for PZ in prev_zones:
            if k[PZ] != 1:
                output = False
        for i in infected:
            if k[i] != -1:
                output = False
        if protected == t and output == True:
            states.append((k.count(-1), _comm15[k][0], _comm15[k][1], k))
    states.sort()
    for s in states:
        if s[2] not in filter_out:
            I = []
            for z in Z:
                if s[3][z] == -1:
                    I.append(z) 
            print('{0:<10} {1:<10} {2:<20} {3}'.format(round(s[1], 2), s[2], str(I), s[3]))

# Optimum Values for Each Communication
print(comm12((0,0,0,0,0,0,0,0,0)))
print(comm13((0,0,0,0,0,0,0,0,0)))             
print(comm14((0,0,0,0,0,0,0,0,0)))
print(comm15((0,0,0,0,0,0,0,0,0)))
