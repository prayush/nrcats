import gwsurrogate
import inspect

sur = gwsurrogate.LoadSurrogate("NRSur7dq4")
print(inspect.signature(sur.__call__))
