# Using Self-Organizing Maps to Triage Software Bug Reports

You can find the demo here: https://sombr.pointy.dev/

## SOMBR: Interactive Self-Organizing Maps for Bug Report Triage

This repository contains the code used to develop my Master Thesis. The document can be accessed [here](http://hdl.handle.net/10362/160225).

It does not include the source data files (which can be retrieved from [Rath and Mäder, 2019](https://www.sciencedirect.com/science/article/pii/S2352340919303580)) nor the processed output files.

For questions you can get in touch [here](https://pointy.dev/).


### File Structure

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
