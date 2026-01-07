"""Core configuration for MiC Dynamic Scheduler"""

class Config:
    APP_VERSION = "V9.5"

    # Cost Parameters
    DEFAULT_COSTS = {
        'skilled': 1200, 'semi': 800, 'unskilled': 500,
        'crane': 3000, 'testing': 1500, 'specialized': 1000,
        'penalty': 2000, 'downtime': 5000
    }
    COSTS = DEFAULT_COSTS

    COST_MAP = {
        'skilled': 'Skilled Labor', 'semi': 'Semi-skilled Labor',
        'unskilled': 'Unskilled Labor', 'crane': 'Crane',
        'testing': 'Testing Equipment', 'specialized': 'Special Tools',
        'penalty': 'Delay Penalty', 'downtime': 'Downtime Cost'
    }

    EMERGENCY_MULTIPLIER = 1.2

    # Default Resources
    DEFAULT_RESOURCES = {
        'R_skilled': 10, 'R_semi': 15, 'R_unskilled': 30,
        'R_crane': 2, 'R_testing': 5, 'R_specialized': 5
    }

    RES_MAP = {
        'R_skilled': 'Skilled Labor', 'R_semi': 'Semi-skilled Labor',
        'R_unskilled': 'Unskilled Labor', 'R_crane': 'Crane',
        'R_testing': 'Testing Equipment', 'R_specialized': 'Specialized Tools'
    }

    # Default Algorithm Parameters
    DEFAULT_ALGO = {'pop_size': 30, 'n_gen': 15, 'mutation_rate': 0.1}

    # Weights & Risk Configuration
    WEIGHTS = {'space': 0.4, 'system': 0.2, 'resource': 0.1, 'risk': 0.3}

    HK_WEATHER_RISK = {
        1: (0.01, 0), 2: (0.01, 0), 3: (0.02, 0.5), 4: (0.05, 1),
        5: (0.15, 2), 6: (0.30, 3), 7: (0.50, 4), 8: (0.60, 5),
        9: (0.40, 3), 10: (0.20, 2), 11: (0.05, 1), 12: (0.01, 0)
    }

    WORK_HOURS = [(8, 12), (13, 17)]
    SYSTEM_TYPES = ["Struct", "Elec", "Plumb", "HVAC", "Facade"]
    OBJ_WEIGHTS = {'cost': 0.35, 'risk': 0.45, 'delay': 0.20}