import os

ROOT_PATH = os.path.dirname(__file__)
OUT_PATH = os.path.join(ROOT_PATH, os.path.join('internal', 'data', 'out'))

RANDOM_STATE = 1
TOPNN_K = 10

KEEP_ISSUE_COLS = ['issue_id', 
                      'type', 
                      'created_date', 
                      'resolved_date', 
                      'summary', 
                      'description', 
                      'priority', 
                      'status', 
                      'resolution', 
                      'assignee_username', 
                     ]
KEEP_STATUS=["Resolved", "Closed"]
KEEP_RESOLUTION=["Done", "Duplicate", "Fixed", "Resolved"]
KEEP_TYPE=["Bug"]
PREVENT_NAN=["assignee_username"]

VECTOR_METADATA=["assignee_username", "resolution", "issue_id", "summary", "bmu"]


BR_QUERY = """
SELECT * from issue
"""

PLOT_HEIGHT = 600
PLOT_WIDTH = 600
SIDEBAR_WIDTH = 230

CONTRAST_COLOR1 = "#ff6361"
CONTRAST_COLOR2 = "#bc5090"
DEFAULT_SOMPARAMS = {
    'm': 15,
    'n': 15,
    'p': 0,
    'n_iters': 10000
}

SOM_SCALING = "mean"