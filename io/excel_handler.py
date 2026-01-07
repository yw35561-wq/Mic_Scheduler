"""Excel file handling for MiC Dynamic Scheduler"""

import pandas as pd
import io
import datetime
from config.base import Config
from sklearn.preprocessing import MinMaxScaler, StandardScaler


class FileManager:
    SHEET_TASKS = "1_Task_Data"
    SHEET_RESOURCES = "2_Resource_Config"
    SHEET_ALGO = "3_Algo_Config"
    SHEET_COSTS = "4_System_Costs"
    SHEET_EMERGENCY = "5_Emergency_Tasks"

    COL_TASK_MAP = {
        'ID': 'ID', 'System': 'System', 'Urgency_C': 'Urgency',
        'Duration_Hours': 'Duration', 'Predecessors': 'Predecessors', 'Remarks': 'Remarks',
        'X': 'X', 'Y': 'Y', 'Z': 'Z',
        'R_skilled': 'Res_Skilled', 'R_semi': 'Res_Semi', 'R_unskilled': 'Res_Unskilled',
        'R_crane': 'Res_Crane', 'R_testing': 'Res_Testing', 'R_specialized': 'Res_Specialized'
    }

    COL_KEYWORDS = {
        'ID': (['id'], []),
        'System': (['system'], []),
        'Urgency_C': (['urgency'], []),
        'Duration_Hours': (['duration', 'hours', 'time'], []),
        'Predecessors': (['predecessor', 'preceding'], []),
        'Remarks': (['remark', 'notes'], []),
        'X': (['coord_x', 'x'], []),
        'Y': (['coord_y', 'y'], []),
        'Z': (['coord_z', 'z'], []),
        'R_skilled': (['skilled'], ['unskilled', 'semi']),
        'R_semi': (['semi'], []),
        'R_unskilled': (['unskilled'], []),
        'R_crane': (['crane', 'hoist'], []),
        'R_testing': (['testing', 'inspection'], []),
        'R_specialized': (['specialized', 'special'], [])
    }

    @staticmethod
    def get_filename(step_prefix, description, ext="xlsx"):
        ts = datetime.datetime.now().strftime("%Y%m%d")
        return f"{step_prefix}_{description}_{Config.APP_VERSION}_{ts}.{ext}"

    @staticmethod
    def generate_master_template():
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Task Data Sheet
            cols = list(FileManager.COL_TASK_MAP.values())
            instructions = ['Unique Int', 'Struct/Elec/Plumb/HVAC/Facade', '0-10', '>0', '1,2', 'Text', 'Float',
                            'Float', 'Float'] + ['Int'] * 6
            example_row = [1, 'Struct', 8, 40, '', 'Initial Task', 10.0, 20.0, 5.0, 2, 0, 1, 1, 0, 0]
            pd.DataFrame([instructions, example_row], columns=cols).to_excel(writer, sheet_name=FileManager.SHEET_TASKS,
                                                                             index=False)

            # Resource Configuration Sheet
            res_data = {
                'Resource_Type': list(Config.DEFAULT_RESOURCES.keys()),
                'Limit_Value': list(Config.DEFAULT_RESOURCES.values()),
                'Note': ['Severe Shortage', 'Normal', 'Normal', 'Bottleneck', 'Normal', 'Normal']
            }
            pd.DataFrame(res_data).to_excel(writer, sheet_name=FileManager.SHEET_RESOURCES, index=False)

            # Algorithm Configuration Sheet
            algo_data = {'Parameter': ['pop_size', 'n_gen', 'mutation_rate'], 'Value': [30, 15, 0.1]}
            pd.DataFrame(algo_data).to_excel(writer, sheet_name=FileManager.SHEET_ALGO, index=False)

            # Cost Configuration Sheet
            cost_data = {
                'Cost_Item': list(Config.DEFAULT_COSTS.keys()),
                'Unit_Price': list(Config.DEFAULT_COSTS.values())
            }
            pd.DataFrame(cost_data).to_excel(writer, sheet_name=FileManager.SHEET_COSTS, index=False)

            # Emergency Tasks Sheet
            emerg_cols = ['Insert_Day', 'System', 'Duration', 'Urgency', 'R_skilled', 'R_crane', 'Note']
            emerg_example = [14, 'Struct', 40, 10, 3, 1, 'Beam Crack Fix']
            pd.DataFrame([emerg_example], columns=emerg_cols).to_excel(writer, sheet_name=FileManager.SHEET_EMERGENCY,
                                                                       index=False)

        return buffer.getvalue()

    @staticmethod
    def parse_master_excel(uploaded_file):
        try:
            xls = pd.ExcelFile(uploaded_file)

            if FileManager.SHEET_TASKS not in xls.sheet_names:
                return None, None, None, None, None, None, f"Missing Required Sheet: {FileManager.SHEET_TASKS}"

            # Parse Task Data
            df_tasks = pd.read_excel(xls, sheet_name=FileManager.SHEET_TASKS, header=0)
            if not pd.api.types.is_numeric_dtype(df_tasks.iloc[0, 0]) and not pd.to_numeric(df_tasks.iloc[0, 0],
                                                                                            errors='coerce'):
                df_tasks = df_tasks.drop(index=0).reset_index(drop=True)
            parsed_tasks = FileManager._parse_task_df(df_tasks)

            # Parse Resource Configuration
            parsed_res = Config.DEFAULT_RESOURCES.copy()
            parsed_notes = {}
            if FileManager.SHEET_RESOURCES in xls.sheet_names:
                df_res = pd.read_excel(xls, sheet_name=FileManager.SHEET_RESOURCES)
                for _, row in df_res.iterrows():
                    res_key = str(row['Resource_Type']).strip()
                    try:
                        res_value = int(row['Limit_Value'])
                    except (ValueError, TypeError):
                        res_value = Config.DEFAULT_RESOURCES.get(res_key, 10)
                    if res_key in parsed_res:
                        parsed_res[res_key] = res_value
                    if 'Note' in df_res.columns and pd.notna(row['Note']):
                        parsed_notes[res_key] = str(row['Note'])

            # Parse Algorithm Parameters
            parsed_algo = Config.DEFAULT_ALGO.copy()
            if FileManager.SHEET_ALGO in xls.sheet_names:
                df_algo = pd.read_excel(xls, sheet_name=FileManager.SHEET_ALGO)
                for _, row in df_algo.iterrows():
                    param_key = str(row['Parameter']).strip()
                    param_value = row['Value']
                    if param_key == 'mutation_rate':
                        parsed_algo[param_key] = float(param_value)
                    elif param_key in parsed_algo:
                        parsed_algo[param_key] = int(param_value)

            # Parse Cost Configuration
            parsed_costs = Config.DEFAULT_COSTS.copy()
            if FileManager.SHEET_COSTS in xls.sheet_names:
                df_cost = pd.read_excel(xls, sheet_name=FileManager.SHEET_COSTS)
                for _, row in df_cost.iterrows():
                    cost_key = str(row['Cost_Item']).strip()
                    try:
                        cost_value = int(row['Unit_Price'])
                    except (ValueError, TypeError):
                        cost_value = Config.DEFAULT_COSTS.get(cost_key, 0)
                    if cost_key in parsed_costs:
                        parsed_costs[cost_key] = cost_value

            # Parse Emergency Tasks
            parsed_emerg = []
            if FileManager.SHEET_EMERGENCY in xls.sheet_names:
                df_em = pd.read_excel(xls, sheet_name=FileManager.SHEET_EMERGENCY)
                for _, row in df_em.iterrows():
                    try:
                        emerg_task = {
                            'Insert_Day': int(row['Insert_Day']),
                            'System': row['System'],
                            'Duration': int(row['Duration']),
                            'Urgency': int(row.get('Urgency', 10)),
                            'R_skilled': int(row.get('R_skilled', 0)),
                            'R_crane': int(row.get('R_crane', 0)),
                            'Note': str(row.get('Note', ''))
                        }
                        parsed_emerg.append(emerg_task)
                    except (ValueError, TypeError):
                        continue

            return parsed_tasks, parsed_res, parsed_notes, parsed_algo, parsed_costs, parsed_emerg, None

        except Exception as e:
            return None, None, None, None, None, None, f"Excel Parsing Error: {str(e)}"

    @staticmethod
    def _parse_task_df(df_data):
        tasks = []
        col_mapping = FileManager._map_task_columns(df_data.columns)

        for _, row in df_data.iterrows():
            task = {}

            # Parse Task ID
            id_col = col_mapping.get('ID')
            if not id_col:
                continue
            try:
                task['ID'] = int(float(row[id_col]))
            except (ValueError, TypeError):
                continue

            # Basic Task Metadata
            task['System'] = row.get(col_mapping.get('System'), 'Struct')
            task['Remarks'] = str(row.get(col_mapping.get('Remarks', ''))) if pd.notna(
                row.get(col_mapping.get('Remarks'))) else ''

            # Parse Predecessors
            pred_col = col_mapping.get('Predecessors')
            pred_str = str(row.get(pred_col, '')).strip() if pred_col else ''
            task['Predecessors'] = []
            if pred_str:
                cleaned_preds = pred_str.replace(';', ',').replace('[', '').replace(']', '').replace(' ', '')
                task['Predecessors'] = [int(float(p)) for p in cleaned_preds.split(',') if
                                        p.replace('.', '', 1).isdigit()]

            # Parse Numeric Fields
            numeric_fields = ['Urgency_C', 'Duration_Hours'] + [k for k in FileManager.COL_KEYWORDS if
                                                                k.startswith('R_')]
            for field in numeric_fields:
                col_name = col_mapping.get(field)
                task[field] = FileManager._parse_numeric_value(row.get(col_name, 0), int)
            task['Duration_Hours'] = max(1, task['Duration_Hours'])

            # Parse Spatial Coordinates
            spatial_fields = ['X', 'Y', 'Z']
            for field in spatial_fields:
                col_name = col_mapping.get(field)
                task[field] = FileManager._parse_numeric_value(row.get(col_name, 0.0), float)

            tasks.append(task)
        return tasks

    @staticmethod
    def _map_task_columns(available_columns):
        col_map = {}
        available_lower = [col.lower() for col in available_columns]

        for internal_key, (keywords, excludes) in FileManager.COL_KEYWORDS.items():
            display_name = FileManager.COL_TASK_MAP.get(internal_key, '')
            if display_name.lower() in available_lower:
                col_map[internal_key] = available_columns[available_lower.index(display_name.lower())]
                continue

            for idx, col in enumerate(available_columns):
                col_lower = col.lower()
                if any(kw in col_lower for kw in keywords) and not any(ex in col_lower for ex in excludes):
                    col_map[internal_key] = col
                    break
        return col_map

    @staticmethod
    def _parse_numeric_value(value, target_type):
        try:
            return target_type(float(value))
        except (ValueError, TypeError):
            return target_type(0)

    @staticmethod
    def generate_schedule_report(schedule_df):
        if schedule_df.empty:
            return None
        return schedule_df.to_csv(index=False).encode('utf-8-sig')


import xlsxwriter
import openpyxl