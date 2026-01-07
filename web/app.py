"""Streamlit web application for MiC Dynamic Scheduler"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import time
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.base import Config
from io.excel_handler import FileManager
from utils.helpers import (
    scale_feature_array, get_risk_factor, is_working_hour,
    add_work_hours, calculate_risk_integral, check_cycles,
    find_elbow_point
)
from core.model import ProjectModel

# Page Configuration (Must be first)
st.set_page_config(page_title="MiC Dynamic Scheduler V9.5", layout="wide")


def main():
    st.title(f"MiC Dynamic Scheduler {Config.APP_VERSION}")
    st.write("A dynamic scheduling system for MiC projects with clustering and optimization.")


    st.subheader("1. Download Input Template")
    template_data = FileManager.generate_master_template()
    st.download_button(
        label="Download Excel Template",
        data=template_data,
        file_name=FileManager.get_filename("Template", "MiC_Scheduler_Input"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("2. Upload Input Data")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    if uploaded_file is not None:
        with st.spinner("Parsing Excel file..."):
            parsed_tasks, parsed_res, parsed_notes, parsed_algo, parsed_costs, parsed_emerg, error = FileManager.parse_master_excel(uploaded_file)
            if error:
                st.error(f"Error: {error}")
            else:
                st.success("File parsed successfully!")

                st.write("### Parsed Task Count:", len(parsed_tasks))
                st.write("### Resource Configuration:", parsed_res)


                if st.button("Initialize Scheduling Model"):
                    tasks_df = pd.DataFrame(parsed_tasks)
                    start_date = datetime.date.today()
                    project = ProjectModel(tasks_df, parsed_res, start_date)
                    st.success(f"Model initialized with start date: {start_date}")
                    st.write("### Feature Matrix Shape:", project.calculate_weighted_features().shape)

if __name__ == "__main__":
    main()