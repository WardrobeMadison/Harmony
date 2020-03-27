def two_afc(traces): 
"""
traces := List of dict
    values
    preTime
    stimTime
"""
    num_correct = 0
    for i, trace in traces:
        discr = traces.copy()
        del discr[i]

        discr = discr.mean()


        


    