def mean_peak_amp(trace, lbound, ubound):
    new_trace = trace[lbound:ubound]
    return new_trace.mean()
