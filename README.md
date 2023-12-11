[![Python - 3.10.13](https://img.shields.io/badge/Python-3.10.13-f4d159)](https://www.python.org/downloads/release/python-31013/)
[![Import Data](https://github.com/cyterat/mia-ua-weapons/actions/workflows/import.yml/badge.svg)](https://github.com/cyterat/mia-ua-weapons/actions/workflows/import.yml)
[![Model data](https://github.com/cyterat/mia-ua-weapons/actions/workflows/model.yml/badge.svg?branch=master)](https://github.com/cyterat/mia-ua-weapons/actions/workflows/model.yml)

# ⚔️Lost and Stolen Weapons in Ukraine  (1991-2023)

<https://ua-weapons.streamlit.app/>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I began working on this project at the end of 2021, when I stumbled upon **MIA** (Ministry of Internal Affairs) **of Ukraine** data, believing that it may potentially uncover how weapons theft and loss fit into the "terraforming" processes of the country as a political entity.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Some peculiar changes occur throughout the history of Ukraine, which may or may not correlate with particular events, some of which I included as the barchart annotations near the top of the webpage. Therefore, I would recommend viewing these annotations as time markers rather than events tied to the numbers.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;It is worth noting that this project is by no means a statistical analysis but rather a visual representation of the dataset, which some of you might find interesting, just as I did.

## 💾Data

* The **original dataset** can be accessed at [data.gov.ua](https://data.gov.ua/en/dataset/5e7a9e93-e4ae-408a-8b99-6a21bfa9c12a/resource/1fcab772-0b3c-4938-8f72-e60db343cbe5)

## 🚧 Version 1.1.0 (Latest)

The majority of changes were made to the data **import** and **modeling** workflows in the GitHub Actions.

- **wget** has been added which enables to download the JSON file via HTTPS using custom headers;
-  JSON file is now stored as an artifact and used only within a workflow;
- **Model Data** workflow will now run only when the **Import Data** finishes, or when triggered manually; 
-  Data Flow/Models Relationship [diagram](https://github.com/cyterat/mia-ua-weapons/blob/6d52dcc1d478c97ad8c48a54e6548febb850c8e6/assets/ua-mia-weapons-relationships.png) has been updated.
  
## 🛠 Libraries

Pandas, NumPy, Matplotlib, Plotly, Streamlit
