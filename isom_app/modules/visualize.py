import numpy as np
from scipy.spatial import KDTree


from bokeh.plotting import figure
from bokeh.layouts import column, row


from bokeh.events import ButtonClick
from bokeh.models import ColumnDataSource, CDSView, CustomJS, Styles

from bokeh.models import Div, Button, Select, TextInput
from bokeh.models import LinearColorMapper
from bokeh.models import TabPanel, Tabs

from bokeh.models import AllIndices, IndexFilter


########################################
### Internal module imports
########################################


from modules.plot_components.js_callbacks import *
from modules.plot_components.cells.details import *
from modules.plot_components.cells.inputs import *
from modules.plot_components.cells.hexagons import *
from modules.plot_components.cells.colorbar import *
from modules.plot_components.cells.graph import *

from constants import *
from modules.setup import *
from modules.organize import *
from modules.vectorize import *


def make_visualization(som, vec_vals, vec_df, transformer):


    xx, yy          = som.get_euclidean_coordinates()
    m,n             = yy.shape
    p               = vec_vals.shape[1] # number of inputs

    umatrix         = som.distance_map(scaling=SOM_SCALING)
    weights         = som.get_weights()
    hitsmatrix      = som.activation_response(vec_vals)

    winmap          = som.win_map(vec_vals, return_indices=True)
    winmap_long     = { np.ravel_multi_index(i,(m,n)): winmap[i] for i in winmap}

    codebook_long   = weights.reshape((m*n,p))
    codebook_tree   = KDTree(codebook_long)

    node_errors     = get_node_errors(codebook_long, vec_vals, winmap_long, m*n)
    
    ASSIGNEES = sorted([str(i) for i in list(vec_df.target.unique())])


    ## Given this som node grid:
    ## 0,0  0,1  0,2  0,3  0,4  0,5
    ## 1,0  1,1  1,2  1,3  1,4  1,5
    ## 2,0  2,1  2,2  2,3  2,4  2,5

    ## bmu node index in long m*n list
    bmu_index = np.arange(m*n)
    ## 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17


    ## bmu node index in mxn 2d list
    bmu_locate = np.reshape(bmu_index,(m,n))
    ## 00 01 02 03 04 05 
    ## 06 07 08 09 10 11 
    ## 12 13 14 15 16 17
    ## Knowing (i,j) address of node (2,5)
    ## easily get the long index equivalent [17]

    ########################################
    ### Visualize SOM
    ########################################


    size = np.min([PLOT_WIDTH / m, PLOT_HEIGHT / n])

    umatrix_vals = umatrix.reshape(m*n)

    c2 = hitsmatrix.reshape(m*n)
    y2 = yy.reshape(m*n) * size 
    x2 = xx.reshape(m*n) * size / np.sqrt(3)*2

    hits_flat = hitsmatrix.reshape(m*n)
    umat_flat = umatrix.reshape(m*n)

    hits_pct = hitsmatrix.reshape(m*n) / hitsmatrix.max()


    hits_labels = [ i.astype(int).astype(str) if i > 0 else '' for i in c2 ]
    hits_labels_color = [ 1 if i.astype(int) > (.75*np.mean([max(c2), min(c2)])) else 0 for i in c2 ] 



    ########################################
    ### Define Colors
    ########################################

    palette = 'Viridis256'

    umatrix_cmap = LinearColorMapper(palette=palette,
                                low = min(umat_flat), 
                                high = max(umat_flat))



    # def return_cds(data, feats):
    #     cds_obj = {}
    #     for feat_i, feat in enumerate(feats):
    #         cds_obj[feat] = data[feat_i]
        
    #     return ColumnDataSource(cds_obj)



    ###################### START Bars ######################
    bars, bar_plot, bar_view, bar_index, bar_source = make_bars(vec_df)

    ###################### END Bars ######################


    ###################### START User ######################
    user_src, user_view, user_select = make_user_input(vec_df, m,n, x2, y2, ASSIGNEES)
    ###################### END User ######################


    ###################### Table View ######################
    node_detail, node_table, table_cds, table_view = make_tables(vec_df)
    
    ###################### END Table View ######################


    ##################################################################
    ### Start Main Plot + Source
    ##################################################################

    node_indices = list(range(m*n))
    coords = ["{}".format(np.unravel_index(i,weights.shape[:2])) for i in range(m*n) ]

    radius_multiplier = .3
    # hits_long = hitsmatrix.reshape((m*n))



    main_source = ColumnDataSource(dict(
            x=x2,
            y=y2,
            c=c2,
            umatrix_vals=umatrix_vals,
            text=hits_labels,
            label_colors = hits_labels_color,
            umat_flat = umat_flat,
            hits_flat = hits_flat,
            hits_pct = hits_pct*size*.75,
            coords=coords,
            node_labels=coords,
            radius=hits_flat*radius_multiplier,
            index=node_indices,
            node_errs = node_errors

        )
    )

    plot = figure( width=PLOT_WIDTH,
                height= PLOT_HEIGHT,
                tools='tap,reset,save',
                toolbar_location='above',
                match_aspect=True,
                aspect_scale=1,
                title="SOM Grid Map",
                outline_line_width=0,
                name="hexwrapper"

                )
    plot.toolbar.logo = None

    ##################################################################
    ### END Main Plot + Source
    ##################################################################



    ##################################################################
    ### Plot UMatrix distance BG hex
    ##################################################################
    plot, bg_hex, um_colorbar = make_bg_hex(plot, main_source, umatrix_cmap, size)
    ##################################################################
    ### END Plot UMatrix distance BG hex
    ##################################################################


    ##################################################################
    ### Plot Quantization Error BG hex
    ##################################################################

    magma = 'Magma256'

    err_cmap = LinearColorMapper(palette=magma,
                                low = min(node_errors), 
                                high = max(node_errors))

    plot, qe_hex, qe_colorbar = make_qe_hex(plot, main_source, err_cmap, size)

    ##################################################################
    ### END Plot Quantization Error BG hex
    ##################################################################



    ##################################################################
    ### Plot hits hex
    ##################################################################
    plot, hits_hex, hits_switch = make_hits_hex(plot, main_source)
    ##################################################################
    ### END Plot hits hex
    ##################################################################


    ##################################################################
    ### Plot User selection hex
    ##################################################################
    plot = make_user_hex(plot, user_src, user_view, size)
    ##################################################################
    ### END Plot User selection hex
    ##################################################################


    ##################################################################
    ### Plot Query Results
    ##################################################################

    plot, highlight_src, highlight_hex = make_query_hex(plot, m, n, x2, y2, size)

    ## Setup Query Input 

    query_input = TextInput(placeholder='Search Query', width=200)

    ##################################################################
    ### END Plot Query Results
    ##################################################################


    ##################################################################
    ##################################################################
    ##################################################################


    ##################################################################
    ##################################################################
    ##################################################################

    ###################### END Main Plot ######################

    ###################### Plot Aesthetics ######################


    plot_renderers=[bg_hex]
    plot = annotate_plot(plot, umatrix_cmap, plot_renderers)


    ###################### END Plot Aesthetics ######################




    ###################### Configure Plot Layout ######################



    node_layout   = column(bar_plot,
                        node_detail, 
                        node_table, 
                        sizing_mode='stretch_both',
                        height=PLOT_HEIGHT, 
                        css_classes=['node_layout']
                        )


    ##################################################################
    ##################################################################
    ## GRAPH


    graph_plot = figure(title="Graph layout", 
                    tools="hover,tap,box_zoom,reset,save",
                    tooltips="node: @coords, hits: @hits_flat",
                    toolbar_location='above',
                    match_aspect=True,
                    aspect_scale=1,
                    x_axis_location=None, 
                    y_axis_location=None,
                    outline_line_width=0,
                    height=PLOT_HEIGHT-50
                    )
    
    G, Gpos = make_graph(weights, hitsmatrix)
    graph_plot, edge_cds = make_graph_plot(G, Gpos, graph_plot, main_source, umatrix_cmap)

    
    ##################################################################
    ##################################################################


    ##################################################################
    ### Start Hex callbacks
    ##################################################################

    hex_select_cb = CALLBACKS['hex_select_cb'] 
    main_source.selected.js_on_change('indices', 
                                    CustomJS(args=dict(
                                                table_src = table_cds,
                                                table_view = table_view,
                                                table_index = IndexFilter(indices=[]),
                                                table_all = AllIndices(),
                                                bar_view = bar_view,
                                                bar_index = bar_index,
                                                bar_source = bar_source,
                                                bar_plot = bar_plot,
                                                edge_cds=edge_cds,
                                                main_cds=main_source
                                                ),
                                            code=hex_select_cb
                                            ))
    
    ### Hex selection dropdown callbacks

    hexbg_select_dropdown = Select(value="UMatrix", 
                            options = ['UMatrix', 'Quantization Error'], 
                            styles=dict({'width':'200px'}))


    hexbg_select_dropdown.js_on_change('value',
            CustomJS(args=dict(qe=qe_hex,
                               um=bg_hex,
                               um_cb=um_colorbar, 
                               qe_cb=qe_colorbar
                            ),
                    code="""
                    qe.visible = !qe.visible
                    um.visible = !um.visible
                    
                    qe_cb.visible = qe.visible
                    um_cb.visible = um.visible
                    
                    """
            )
        )

    ##################################################################
    ### END Hex callbacks
    ##################################################################


    ##################################################################
    ### BEGIN TABS
    ##################################################################


    graph_tab = TabPanel(child=graph_plot, title='graph')
    node_tab = TabPanel(child=node_layout, title="main", 

                        )

    details_tab_layout   = Tabs(tabs=[
                                    node_tab,
                                    graph_tab, 
                                    ], 
                                name="detailswrapper"
                                )
    
    ##################################################################
    ### END TABS
    ##################################################################

    ##################################################################
    ### BEGIN Colorbar plot
    ##################################################################


    colorbar_plot = figure(width=60, 
                            toolbar_location=None, 
                            outline_line_width=0,
                            name="colorbar_plot"
                            )
    
    colorbar_plot.add_layout(um_colorbar, 'right')
    colorbar_plot.add_layout(qe_colorbar, 'right')
    ##################################################################
    ### END Colorbar plot
    ##################################################################



    ##################################################################
    ### BEGIN FOOTER ITEMS
    ##################################################################


    def calculate_query(event):

        topnn = codebook_tree.query(transformer.encode(query_input.value), TOPNN_K)[1].tolist()
        highlight_rank = np.zeros(m*n) #+ .5
        
        rank_alpha = (np.arange(TOPNN_K,0,-1)+1)/(1+TOPNN_K)
        for i in range(TOPNN_K):
            highlight_rank[topnn[i]] = np.max([rank_alpha[i],0.4])

        
        highlight_src.data['rank'] = highlight_rank
        highlight_hex.view = CDSView(filter=IndexFilter(indices=topnn))
        return

    def clear_query(event):
        query_input.value = ""
        highlight_hex.view = CDSView(filter=IndexFilter(indices=[]))

    button_styles = Styles(flex="1 0 auto")
    run_query_button =Button(label="Run Query", button_type="success", styles=button_styles)
    clear_query_button =Button(label="Clear Query", styles=button_styles)


    run_query_button.on_event(ButtonClick, calculate_query)
    clear_query_button.on_event(ButtonClick, clear_query)



    footer_col_style=Styles(
        padding="1em",
        margin="0 1em 0 0",
        min_width="200px"
    )

    
    
    hex_toggle_switch = row(hits_switch, Div(text="Toggle Hits Hex"))



    footer_overlay = column(
        Div(text="""
        <h3>Select SOM Hex Overlay</h3>
        """),
        hexbg_select_dropdown,
        hex_toggle_switch,
        styles=footer_col_style,
        name="footer_overlay"
    )

    footer_input = column(
        Div(text="""<h3>Enter Query</h3>"""),
        query_input,
        row(run_query_button, 
            clear_query_button, 
                sizing_mode='stretch_width', 
                styles=Styles(justify_content="space-between")
            ),
        styles=footer_col_style,
        name="footer_input"

        )

    footer_user = column(
        Div(text="""<h3>Select User</h3>"""),
        user_select,
        styles=footer_col_style,
        name="footer_user"

        )


    ###################### END Configure Plot Layout ######################
    
    return details_tab_layout, plot, colorbar_plot, footer_overlay, footer_input, footer_user