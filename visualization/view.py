from pathlib import Path

import numpy as np
from _utils.typing import PathLike

import pickle

from strategies.strategy import StrategyEvent, StrategyResults
from _utils.val import defval_instance, val_instance

import pandas as pd
import datetime as dt

from bokeh.plotting import output_file

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show
from bokeh.models import LinearAxis, Range1d, Label, HoverTool, Span

def view(path: PathLike, output: PathLike, interpolate: bool = None) -> None:
    val_instance(path, PathLike)
    val_instance(output, PathLike)
    interpolate = defval_instance(interpolate, bool, False)
    
    with open(path, "rb") as f:
        _data = pickle.load(f)
        
    data, events, results = _data
    results: StrategyResults
    output_file(output)
    
    df: pd.DataFrame = pd.DataFrame(data, columns=["TIME", "INDEX", "STOCK"])
    df = df.sort_values("TIME")
    df = df.reset_index(drop=True)
    
    # if df["TIME"].dtype == object:
    def localize(x: dt.datetime) -> None:
        return x.replace(tzinfo=None)
        
    df["TIME"] = df["TIME"].apply(localize)
    df["TIME"] = df["TIME"].astype(np.datetime64)
    
    def just_time(datetime: dt.datetime) -> dt.time:
        return datetime.time()
    
    df["_time"] = df["TIME"].apply(just_time)
    
    plot = figure(x_axis_type="datetime", title=f"Graph", tools = "freehand_draw,poly_draw,poly_edit,pan,box_zoom,wheel_zoom,undo,redo,reset,save")
    sell_time: dt.datetime = None
    
    for event in events:
        event: StrategyEvent
        
        event_time, event_name, event_value = event
        
        event_time = localize(event_time)
        
        labels: list[Label] = []
        vlines: list[Span] = []
        
        if event_name == "stock cliff":
            vlines.append(Span(location=event_time, dimension='height', line_color='#f43546', line_width=3, line_alpha=0.5))
            labels.append(Label(x=(event_time), y=(20), y_units='screen', text=' CLIFF', text_font_style="bold"))
        elif event_name == "stock cliff corrected":
            vlines.append(Span(location=event_time, dimension='height', line_color='#398e3b', line_width=3, line_alpha=0.5))
            labels.append(Label(x=(event_time), y=(20), y_units='screen', text=' CLIFF C', text_font_style="bold"))
        elif event_name == "verification done":
            vlines.append(Span(location=event_time, dimension='height', line_color='#398e3b', line_width=3, line_alpha=0.5))
            labels.append(Label(x=(event_time), y=(20), y_units='screen', text=' VDONE', text_font_style="bold"))
        elif event_name == "verification part 1":
            vlines.append(Span(location=event_time, dimension='height', line_color='#398e3b', line_width=3, line_alpha=0.5))
            labels.append(Label(x=(event_time), y=(20), y_units='screen', text=' VP1', text_font_style="bold"))
        elif event_name == "verification reset":
            vlines.append(Span(location=event_time, dimension='height', line_color='#f43546', line_width=3, line_alpha=0.8))
            labels.append(Label(x=(event_time), y=(20), y_units='screen', text=' VRESET', text_font_style="bold"))
        elif event_name == "signal 1":
            labels.append(Label(x=(event_time), y=(100), y_units='screen', text=' SIGNAL 1', text_font_style="bold"))
            # labels.append(Label(x=(event_time), y=(80), y_units='screen', text=f' ${results.buy_price}', text_font_style="bold"))
            labels.append(Label(x=(event_time), y=(60), y_units='screen', text=f' {event_time.time()}', text_font_style="bold"))
            vlines.append(Span(location=event_time, dimension='height', line_color='#2c60ff', line_width=3, line_alpha=0.8))
        elif event_name == "signal 2":
            labels.append(Label(x=(event_time), y=(100), y_units='screen', text=f' SIGNAL 2 {event_value}', text_font_style="bold"))
            # labels.append(Label(x=(event_time), y=(80), y_units='screen', text=f' ${results.sell_price}', text_font_style="bold"))
            labels.append(Label(x=(event_time), y=(60), y_units='screen', text=f' {event_time.time()}', text_font_style="bold"))
            # labels.append(Label(x=(event_time), y=(40), y_units='screen', text=f'  Δ%: {str(results.pnl_perc() * 100).ljust(5)[:5]}%', text_font_style="bold"))
            # labels.append(Label(x=(event_time), y=(20), y_units='screen', text=f' P&L: {str(results.pnl_bps()).ljust(5)[:6]}bps', text_font_style="bold"))
            vlines.append(Span(location=event_time, dimension='height', line_color='#f43546', line_width=3, line_alpha=0.5))
        
        for label in labels:
            plot.add_layout(label)
            
        for vline in vlines:
            plot.add_layout(vline)
            
    cut_off_time: dt.time = None
    if sell_time is not None:
        cut_off_time = (sell_time + dt.timedelta(minutes=2)).time()
    else:
        cut_off_time = dt.time(9, 50, 0)
    
    mask = (df["_time"] > dt.time(9, 25, 0)) & (df["_time"] < cut_off_time)
    df = df.loc[mask]
    
    # df["TIME"] = df["TIME"].apply(to_datetime)
    df["TIME"] = df["TIME"].dt.tz_localize(None)
    
    if interpolate:
        df = df.interpolate(method="ffill")
    
    time = df["TIME"].tolist()
    index = df["INDEX"].tolist()
    stock = df["STOCK"].tolist()
    
    stock_range = (np.nanmin(stock), np.nanmax(stock))
    index_range = (np.nanmin(index), np.nanmax(index))
    
    plot.y_range = Range1d(start=stock_range[0], end=stock_range[1])
    plot.extra_y_ranges = {"index_range": Range1d(start=index_range[0], end=index_range[1])}
    
    plot.add_layout(LinearAxis(y_range_name="index_range"), 'right')
    plot.grid.grid_line_alpha=0.3
    plot.xaxis.axis_label = 'Time'
    plot.yaxis.axis_label = 'Price'
    
    plot.line(time, stock, color='#3063f0', legend_label='Stock')
    plot.line(time, index, color='#ff6d00', legend_label='Index', y_range_name="index_range")
    
    plot.legend.location = "top_left"
            
    hover_tools = HoverTool(
        tooltips=[
            ( 'Time',  '@x{%F %H:%M:%S}'),
            ( 'Price',  '$@y{%0.2f}' ), # use @{ } for field names with spaces
        ],
        formatters={
            '@x' : 'datetime', # use 'datetime' formatter for '@date' field
            '@y' : 'printf',   # use 'printf' formatter for '@{adj close}' field
                                            # use default 'numeral' formatter for other fields
        },
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    )
    
    # plot.add_tools(hover_tools)
    
    show(gridplot([[plot]], sizing_mode="stretch_both"))