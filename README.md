# Using Self-Organizing Maps to Triage Software Bug Reports


## ISOM4BR: Interactive Self-Organizing Maps for Bug Report Triage

```
.
├── cloudbuild.yaml
├── isom_app
│   ├── constants.py
│   ├── internal
│   │   ├── data
│   │   │   ├── _processed
│   │   │   │   ├── spark-bugreports.csv
│   │   │   │   └── vec_df.csv
│   │   │   ├── embeddings
│   │   │   │   └── embeddings01.csv
│   │   │   ├── in
│   │   │   │   └── spark.sqlite3
│   │   │   └── out
│   │   └── models
│   │       ├── all-MiniLM-L6-v2
│   │       │   └── ...
│   │       ├── nltk_data
│   │       │   └── punkt
│   │       └── som
│   │           └── som.p
│   ├── main.py
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