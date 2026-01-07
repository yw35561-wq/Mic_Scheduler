"""Core scheduling model for MiC Dynamic Scheduler"""

import pandas as pd
import numpy as np
import datetime
import copy
from config.base import Config
from utils.helpers import (
    scale_feature_array,
    add_work_hours,
    get_risk_factor,
    is_working_hour
)


class ProjectModel:
    def __init__(self, tasks_df, resources_limit, start_date):
        self.tasks_df = tasks_df
        self.resources_limit = resources_limit
        base_start = datetime.datetime.combine(start_date, datetime.time(8, 0))
        self.start_date = add_work_hours(base_start, 0)
        self.logs = []

    def log(self, message):
        self.logs.append(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def calculate_weighted_features(self):
        df = self.tasks_df.copy()
        if df.empty:
            return np.array([])

        # Spatial features
        spatial_features = scale_feature_array(df[['X', 'Y', 'Z']].values) * Config.WEIGHTS['space']

        # Risk/urgency features
        risk_features = scale_feature_array(df[['Urgency_C']].values) * Config.WEIGHTS['risk']

        # Resource requirement features
        resource_cols = [col for col in df.columns if col.startswith('R_')]
        if resource_cols:
            resource_features = scale_feature_array(df[resource_cols].values) * Config.WEIGHTS['resource']
        else:
            resource_features = np.zeros((len(df), 1))

        # System type features
        system_codes = pd.factorize(df['System'])[0].reshape(-1, 1)
        system_features = scale_feature_array(system_codes) * Config.WEIGHTS['system']

        # Combine all features
        feature_components = [spatial_features, risk_features, system_features]
        if resource_cols:
            feature_components.append(resource_features)

        return np.hstack(feature_components)

    @staticmethod
    def preempt_and_split(running_tasks, roll_dt, next_free_id):
        split_tasks = []
        for task in running_tasks:
            if task['end_dt'] <= roll_dt:
                split_tasks.append(task)
                continue

            # Calculate completed hours
            start_dt = task['start_dt']
            completed_hours = 0
            current_dt = start_dt

            while current_dt < roll_dt and completed_hours < task['Duration_Hours']:
                if is_working_hour(current_dt):
                    completed_hours += 1
                current_dt += datetime.timedelta(hours=1)

            # Create completed task segment
            done_task = copy.deepcopy(task)
            done_task['ID'] = next_free_id
            done_task['Duration_Hours'] = completed_hours
            done_task['end_dt'] = roll_dt
            done_task['status'] = 'Split-Done'
            next_free_id += 1
            split_tasks.append(done_task)

            # Create remaining task segment
            remaining_hours = task['Duration_Hours'] - completed_hours
            rem_task = copy.deepcopy(task)
            rem_task['ID'] = next_free_id
            rem_task['Duration_Hours'] = remaining_hours
            rem_task['start_dt'] = roll_dt
            rem_task['predecessors'] = [done_task['ID']]
            rem_task['status'] = 'Split-Remaining'
            next_free_id += 1
            split_tasks.append(rem_task)

        return split_tasks, next_free_id