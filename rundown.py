""" 
*.rview is just a pickle file:
Pickle in Python is primarily used in serializing and deserializing a Python object structure. 
In other words, it’s the process of converting a Python object into a byte stream to store it 
in a file/database, maintain program state across sessions, or transport data over the network. 
The pickled byte stream can be used to re-create the original object hierarchy by unpickling 
the stream. This whole process is similar to object serialization in Java or .Net.
"""

# import pickle for deserialization
import pickle

# imports for type hinting
from typing import Any
from datetime import datetime
from strategies.strategy import StrategyEvent, StrategyResults

rview_file: str = "2022-08-12.rview"
print(f"> loading: {rview_file} ...")

with open(rview_file, "rb") as f: # open file in `read binary` mode
    print(f"> read {rview_file} bytes")
    data: bytes = f.read() # get byte data out of file

print(f"> decoded {rview_file} bytes")
loaded_data: Any = pickle.loads(data) # deserialize the bytes

"""
the shorthand form for the previous is:

with open(rview_file, "rb") as f:
    loaded_data = pickle.load(f)
    
"""

print(f"> unpacked {rview_file} data into `data, events, results`")
data, events, results = loaded_data

# type hinting unpacked variables
# essentially means that data is a list of lists of datetime, float, float.
data: list[list[datetime, float, float]]

"""
ie.

data looks like this
[
    [datetime, float, float],
    [datetime, float, float],
    ...
    [datetime, float, float]
]

or a practical example:

[
    [Timestamp('2022-08-11 15:59:58-0400', tz='tzoffset(None, -14400)'), 33331.36, 324.08]
    ...
    [Timestamp('2022-08-11 16:00:00-0400', tz='tzoffset(None, -14400)'), 33341.71, 324.37]
]

Timestamp and datetime are practically the same class or object type in terms of functionality.
"""

# I am going to convert the data to a table, just for display purposes
# just know that you don't need to
import pandas as pd

df: pd.DataFrame = pd.DataFrame(data, columns=["Time", "DJI", "QQQ"])

print(f"\n> contents of data (formatted):\n{df}\n")

# the contests of data just get plotted (Time against other columns, ie. DJI, and QQQ in this case).

# events is just a list of strategy events.
# refer to StrategyEvent for detail (ctrl + click on `StrategyEvent` below)
events: list[StrategyEvent]

"""
meaning events looks something like this:

[
    StrategyEvent(time=`some datetime object`, name=`name of the event`, 
    value=`value (price) at the time the event ocurred, often is "None" or "null" in general terms.`),
    ...
    StrategyEvent(...),
    StrategyEvent(...)
]
"""

events_formatted: pd.DataFrame = pd.DataFrame([[event.time, event.name, event.value] for event in events], columns=["Time", "Name", "Value"])
print(f"\n> contents of events (formatted):\n{events_formatted}\n")

"""
I also formatted the contents of `events` however, note that they actually look like this (for the 2022-08-11 example):

If you want to see it in the console set `show_events_raw` below to `True`.

[
    StrategyEvent(time=Timestamp('2022-08-12 09:35:55-0400', tz='tzoffset(None, -14400)'), name='stock cliff', value=None),
    StrategyEvent(time=Timestamp('2022-08-12 09:36:31-0400', tz='tzoffset(None, -14400)'), name='stock cliff corrected', value=None),
    ...,
    StrategyEvent(time=Timestamp('2022-08-12 09:40:48-0400', tz='tzoffset(None, -14400)'), name='verification part 1', value=None),
    StrategyEvent(time=Timestamp('2022-08-12 09:42:02-0400', tz='tzoffset(None, -14400)'), name='verification reset', value=None)]
]
"""

show_events_raw: bool = False
if show_events_raw:
    events_formatted_raw: str = '\n'.join(str(e) for e in events)
    print(f"\n> contents of events (raw) (formatted):\n{events_formatted_raw}\n")

# events is just a list of strategy results.
# refer to StrategyResults for detail (ctrl + click on `StrategyResults` below)
results: list[StrategyResults]

results_formatted: str = '\n'.join(str(r) for r in results)
# the 2022-08-11 example shows what it looks like when there is no trade.
print(f"\n> contents of results (formatted):\n{results_formatted}\n")
