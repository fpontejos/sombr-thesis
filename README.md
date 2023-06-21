# Using Self-Organizing Maps to Triage Software Bug Reports

You can find the demo here: https://sombr.pointy.dev/

## SOMBR: Interactive Self-Organizing Maps for Bug Report Triage

```
.
├── isom_app
│   ├── constants.py
│   ├── main.py
│   ├── internal
│   │   ├── data
│   │   │   ├── _processed
│   │   │   │   └── vec_df.csv
│   │   │   ├── in
│   │   │   │   └── spark.sqlite3
│   │   │   └── out
│   │   └── models
│   │       ├── all-MiniLM-L6-v2
│   │       ├── nltk_data
│   │       └── som
│   │           └── som.p
│   ├── modules
│   │   ├── __init__.py
│   │   ├── organize.py
│   │   ├── plot_components
│   │   │   ├── cells
│   │   │   │   ├── colorbar.py
│   │   │   │   ├── details.py
│   │   │   │   ├── graph.py
│   │   │   │   ├── hexagons.py
│   │   │   │   └── inputs.py
│   │   │   ├── js
│   │   │   │   ├── hex_select_callback.js
│   │   │   │   ├── row_select_callback.js
│   │   │   │   └── user_callback.js
│   │   │   ├── js_callbacks.py
│   │   │   └── utils
│   │   │       ├── interstitials.py
│   │   │       └── metrics.py
│   │   ├── setup.py
│   │   ├── vectorize.py
│   │   └── visualize.py
│   ├── static
│   │   └── styles.css
│   └── templates
│       └── index.html
├── notebooks
└── requirements.txt
```