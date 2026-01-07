"""Utility functions for MiC Dynamic Scheduler"""

import numpy as np
import datetime
from config.base import Config


def scale_feature_array(feature_array, scaler=StandardScaler()):
    if len(feature_array) == 0:
        return np.array([])
    return scaler.fit_transform(feature_array)


def get_risk_factor(date_obj):
    return Config.HK_WEATHER_RISK.get(date_obj.month, (0, 0))


def is_working_hour(dt_obj):
    if dt_obj.weekday() == 6:
        return False
    current_hour = dt_obj.hour
    return any(start <= current_hour < end for start, end in Config.WORK_HOURS)


def add_work_hours(start_dt, hours_needed):
    if hours_needed <= 0:
        return start_dt

    current_dt = start_dt.replace(minute=0, second=0, microsecond=0)
    while not is_working_hour(current_dt):
        current_dt += datetime.timedelta(hours=1)

    hours_added = 0
    while hours_added < hours_needed:
        current_dt += datetime.timedelta(hours=1)
        if is_working_hour(current_dt):
            hours_added += 1
    return current_dt


def calculate_risk_integral(start_dt, duration_hours, urgency):
    total_risk = 0.0
    current_dt = start_dt
    hours_counted = 0
    urgency_factor = urgency / 10.0

    while hours_counted < duration_hours:
        if is_working_hour(current_dt):
            risk_prob, _ = get_risk_factor(current_dt)
            total_risk += risk_prob * urgency_factor
            hours_counted += 1
        current_dt += datetime.timedelta(hours=1)

    return total_risk * 100


def check_cycles(tasks_list, new_pred, target_id):
    task_graph = {task['ID']: task['Predecessors'].copy() for task in tasks_list}
    if target_id not in task_graph:
        return False

    task_graph[target_id].append(new_pred)

    visited = set()
    stack = set()

    def dfs_visit(node):
        if node in stack:
            return True
        if node in visited:
            return False
        visited.add(node)
        stack.add(node)

        for neighbor in task_graph.get(node, []):
            if dfs_visit(neighbor):
                return True
        stack.remove(node)
        return False

    return dfs_visit(target_id)


def find_elbow_point(sse_values):
    if len(sse_values) < 3:
        return 0

    coords = np.array(list(enumerate(sse_values)))
    p1 = coords[0]
    p2 = coords[-1]
    direction_vec = p2 - p1
    direction_vec = direction_vec / np.linalg.norm(direction_vec)

    max_distance = -1
    elbow_index = 0
    for idx, point in enumerate(coords):
        cross_product = np.linalg.norm(np.cross(direction_vec, point - p1))
        if cross_product > max_distance:
            max_distance = cross_product
            elbow_index = idx
    return elbow_index

from sklearn.preprocessing import StandardScaler