from bokeh.io import curdoc
import os 


import nltk
nltk.data.path.append("./internal/models/nltk_data/")

########################################
### Internal module imports
########################################


# from modules.plot_components.js_callbacks import *
# from modules.plot_components.cells.details import *
# from modules.plot_components.cells.inputs import *
# from modules.plot_components.cells.hexagons import *
# from modules.plot_components.cells.colorbar import *
# from modules.plot_components.tabs.graph import *

from constants import *
from modules.setup import *
from modules.organize import *
from modules.vectorize import *
from modules.visualize import *

import argparse
parser = argparse.ArgumentParser()
parser = setup_parser(parser)
args = parser.parse_args()

transformer = get_transformer()

if args.force_retrain:
    print("force_retrain turned on")
    dbpath = os.path.join(ROOT_PATH, os.path.relpath(os.path.join('.', 'internal', 'data', 'in', 'spark.sqlite3')))

    vec_vals, vec_df, som = setup_new(save=True, dbpath=dbpath)
else:
    vec_vals, vec_df, som = setup_pretrained()



details_tab_layout, plot, colorbar_plot, footer_overlay, footer_input, footer_user = make_visualization(som, vec_vals, vec_df, transformer)


curdoc().add_root(details_tab_layout)
curdoc().add_root(plot)
curdoc().add_root(colorbar_plot)

curdoc().add_root(footer_overlay)
curdoc().add_root(footer_input)
curdoc().add_root(footer_user)

curdoc().title = "Interactive SOM for BR Triage"














