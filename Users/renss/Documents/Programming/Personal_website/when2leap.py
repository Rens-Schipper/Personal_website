import numpy as np
import pandas as pd
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.layouts import column, row, gridplot
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Spectral6
from bokeh.models import ColumnDataSource, HoverTool, Select, Range1d, Paragraph, TextInput, Slider
from bokeh.models.widgets import Slider, Button, TextInput
from bokeh.models.widgets import DataTable, TableColumn, RangeSlider
from bokeh.embed import components

def max_func(rand_array, cut_off,rejection_chance):
    real_max_loc = rand_array.argmax()
    if cut_off != 0:
        m1, m2 = rand_array[:cut_off], rand_array[cut_off:]
        m2_max = m2.max()
        local_max = m1.max()
        #print(f"start run, {cut_off}, {local_max}")
        #print(m1,m2)
        m3 = m2
        
        m2_choice = 0
        m2_choice_num = 0
        stop_loop = False
        while stop_loop == False:
            #print(f"len m3 {len(m3)}")
            if m2.max() < local_max or len(m3) < 1:
                m2_choice = -1
                m2_choice_num = m2[m2_choice] 
                #temp loop break
                stop_loop = True
                break
                
            m2_choice = np.argmax(m3 > local_max)
            
            #if the max value of m1 is bigger than all figures in m2 then we take the last value of m2 because the algo will
            #run through the whole array, find no argument bigger than the local max and return a zero
            
            
            rng = np.random.default_rng()
            random_int = rng.integers(100, size=1)[0]
            #print(random_int, rejection_chance, m2_choice, m3[m2_choice]   )
            #rejection chance
            if random_int < rejection_chance:
                #print(m3)
                m3 = m3[(m2_choice + 1):]
                #print(m3)
            else:
                stop_loop = True
                #print(m3)
                #print("----------")
                
        if len(m3) != 0 :
            #print(m3)
            #print(m2_choice)
            #print(m3[m2_choice])
            #print("final choice")
            m2_choice_num = m3[m2_choice]
        else:
            pass
            #print(m3)
            #print(m2_choice)
            #print(m2[m2_choice])
            
    else:
        m2_choice = 0
        m2_choice_num = rand_array[m2_choice]
        local_max = rand_array[0]
        m2_max = rand_array[cut_off:].max()
        
    m2_max_check = m2_choice_num == rand_array.max()
        
    return [local_max, m2_choice, m2_choice_num, m2_max_check, m2_max, real_max_loc]

def generate_simulation(x_iters, y_len, rejection_chance):
    num_range = range(0,y_len )
    list_of_maxes = []
    m = np.random.normal(10, 1, size = [x_iters,y_len])
    for i in num_range:
        #m = np.random.normal(10, 1, size = [x_iters,y_len])
        z = np.array(list(map(lambda temp: max_func(temp, i, rejection_chance), m)))
        maxes = list(map(lambda x: x[3], z))

        list_of_maxes.append((np.array(maxes).sum() / x_iters) *100)

    return dict(perc_succes = list_of_maxes, num_range = list(range(1, (y_len + 1))))

def modify_doc(doc):
    tools = ["box_select","lasso_select","help","pan","wheel_zoom", "hover"]

    x_iterations = TextInput(title="Number of iterations per point", value="100", width = 200)
    y_length = TextInput(title="Number of values in range", value="10", width = 200)
        
    rejection_chance = TextInput(title="Chance of rejection on proposal: max 99", value="0",width = 200)
    button = Button(label="Refresh Visual.", width = 200)
    
    data = ColumnDataSource(generate_simulation(100 , 10, 0))
    max_data = ColumnDataSource(dict(max_index = [np.array(data.data["perc_succes"]).argmax() + 1],
                max_value = [np.array(data.data["perc_succes"]).max()]))
    
    analysis = ColumnDataSource({"calcs": ["Optimal Stopping Index", "Succes percentage"], 
                                 "vals": [np.round(max_data.data["max_index"], 2), np.round(max_data.data["max_value"], 2)]})
    
    p = figure(width=700, height=700, title="Chance of succes", tools = tools)

    # add a line renderer
    #p.line("num_range", "perc_succes", line_width=2, source = data)
    p.vbar(x = "num_range", top = "perc_succes", width=0.9, source = data)
    p.circle("max_index", "max_value", color = "red", size = 5, source = max_data)
        
    #set axis ranges
    p.y_range = Range1d(0,55)    
    
    #create columns for the data table
    columns = [
        TableColumn(field="calcs", title="Category")
        ,TableColumn(field="vals", title="Value")]
    
    data_table = DataTable(source=analysis, columns = columns, width=200, height=280)
                
    layout = row(column(x_iterations, y_length, rejection_chance, button, data_table), column(p)) # show the results
    
    def update():
        data.data = generate_simulation(int(x_iterations.value), int(y_length.value), int(rejection_chance.value))
        max_data.data = dict(max_index = [np.array(data.data["perc_succes"]).argmax() + 1],
                        max_value = [np.array(data.data["perc_succes"]).max()])
        analysis.data = {"calcs": ["Optimal Stopping Index", "Succes percentage"], 
                                 "vals": [np.round(max_data.data["max_index"], 2), np.round(max_data.data["max_value"], 2)]}
        
        
    #set the update function
    button.on_click(update)
    #x_iterations.on_change(update)
    #y_length.on_change(update)
    
    
    # add the layout to curdoc
    doc.add_root(layout)