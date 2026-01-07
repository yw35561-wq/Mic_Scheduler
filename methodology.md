# Technical Explanation of Modular Integrated Construction (MiC) Building Inspection and Maintenance Scheduling Code
This document provides a comprehensive technical breakdown of the code implemented for the CIVL6060 project—an optimal maintenance scheduling system for Hong Kong MiC buildings. The code integrates Failure Mode and Effects Analysis (FMEA), K-means clustering, and the Non-dominated Sorting Genetic Algorithm II (NSGA-II) to address dynamic Inspection and Maintenance (IM) task scheduling under resource constraints, regulatory requirements, and local environmental conditions. The implementation prioritizes modularity, reproducibility, and alignment with real-world engineering needs, with code structured to support iterative refinement and practical deployment.

## 1. Introduction
The core objective of the code is to transform scattered IM requirements of MiC buildings into a systematic, data-driven scheduling framework. Unlike static scheduling methods for conventional buildings, this code enables:
- **Dynamic risk quantification**: Prioritization of IM tasks based on context-aware risk assessment (adapted to Hong Kong’s typhoon-prone, high-humidity environment).
- **Efficient task grouping**: Batch processing of IM tasks to minimize resource reallocation and travel costs.
- **Multi-objective optimization**: Simultaneous minimization of total cost, system risk, and schedule delay under strict constraints (labor, equipment, time windows).

The code is implemented in Python (compatible with Python 3.8+) with modular components for risk analysis, clustering, optimization, and case validation. Key dependencies include `numpy` (numerical computations), `scikit-learn` (K-means clustering), `pandas` (data handling), and `matplotlib` (result visualization). All core algorithms are parameterized to support customization for different MiC projects.

## 2. Fundamental Background
### 2.1 MiC Building IM Core Challenges
MiC buildings differ from conventional reinforced concrete structures in their modular assembly, complex system dependencies, and sensitivity to environmental factors. The code addresses three critical challenges:
- **System interdependency**: Local failures propagate through module connections, requiring consideration of task dependencies.
- **Resource constraints**: Limited skilled labor, high equipment costs, and spatial restrictions in Hong Kong.
- **Dynamic deterioration**: Variable degradation rates due to usage, installation accuracy, and weather (e.g., typhoons, salt spray).

### 2.2 Algorithm Foundation
The code’s workflow is built on three interconnected algorithms, each addressing a key stage of scheduling:
1. **FMEA**: Converts qualitative failure modes into quantitative risk scores (Risk Priority Number, RPN) to guide task prioritization.
2. **K-means clustering**: Groups IM tasks based on spatial proximity, system affiliation, resource requirements, and risk level to optimize batch execution.
3. **NSGA-II**: Solves multi-objective optimization for task sequencing and resource allocation, generating Pareto-optimal schedules.

### 2.3 Data Requirements
The code relies on structured input data aligned with Hong Kong MiC project characteristics:
- **Failure mode data**: System affiliation, failure description, and dependency relationships (from literature and project records).
- **Risk assessment data**: Severity (S), Occurrence (O), and Detection (D) scores for FMEA (validated by engineering experts).
- **Resource data**: Labor (skilled/semi-skilled/unskilled), equipment (cranes, testing tools), and spatial coordinates of tasks.
- **Constraint data**: Legal working hours, weather-related downtime, and resource capacity limits.

## 3. Core Algorithm Modules
### 3.1 FMEA Risk Quantification Module
This module (implemented in `fmea_risk_calc.py`) quantifies the risk of each IM task to establish prioritization and dependencies. It serves as the foundational input for subsequent clustering and optimization.

#### 3.1.1 Core Workflow
| Step | Description | Implementation Details |
|------|-------------|------------------------|
| 1. System Definition | Partition MiC buildings into 5 core systems (structural connection, waterproofing/fireproofing, MEP, building envelope, interior/partition) | Configurable via `system_config.json`; aligns with Hong Kong Buildings Department standards |
| 2. Failure Mode Identification | Extract representative failure modes for each system | Curated from 20+ typical failures (e.g., bolt loosening, sealant cracking) in Hong Kong MiC projects |
| 3. Dependency Analysis | Map propagation paths between failures (e.g., bolt loosening → sealant cracking) | Stored as adjacency lists in `failure_dependencies.csv` |
| 4. RPN Calculation | Compute risk scores using expert-assessed S, O, D values | RPN = S × O × D; S/O/D scored on 1-10 scales (Section 3.1.2) |
| 5. Criticality Level Assignment | Convert RPN to urgency scores for task prioritization | $C_i = \lfloor RPN / 100 \rfloor$ (ranges 1-10) |

#### 3.1.2 Mathematical Formulation
- **Severity (S)**: Impact on safety, environment, or functionality (1 = no impact; 10 = fatal safety risk).
- **Occurrence (O)**: Frequency of failure (1 = rare; 10 = daily occurrence).
- **Detection (D)**: Likelihood of identifying the failure (1 = undetectable; 10 = always detected).
- **Risk Priority Number (RPN)**:  
  $$RPN = S \times O \times D$$  
- **Criticality Level ($C_i$)**:  
  $$C_i = \left\lfloor \frac{RPN}{100} \right\rfloor$$  

#### 3.1.3 Key Design Choices
- **Context-Aware Scoring**: S/O/D scales are calibrated to Hong Kong’s context (e.g., O scores for waterproofing failures are elevated due to high humidity).
- **Dependency Encoding**: Failure propagation paths are encoded as precedence constraints for scheduling (e.g., sealant repair must follow bolt tightening).

### 3.2 K-means Task Clustering Module
This module (implemented in `kmeans_task_clustering.py`) groups IM tasks to minimize resource mobilization and improve scheduling efficiency. Clustering is based on four dimensional features, with standardized processing to eliminate unit bias.

#### 3.2.1 Core Workflow
| Step | Description | Implementation Details |
|------|-------------|------------------------|
| 1. Feature Extraction | Extract 4 core features for each task: spatial position (X,Y,Z), system affiliation ($K_i$), resource requirements ($R_i^r$), risk criticality ($C_i$) | Features derived from `task_metadata.csv` and FMEA outputs |
| 2. Feature Standardization | Normalize features to [0,1] range to ensure equal weighting | Min-max scaling for spatial/resource features; binary encoding for system affiliation |
| 3. Optimal K Selection | Determine cluster number using the elbow rule (sum of squared errors, SSE) | Plots SSE vs. K (default range: 2-10) to identify inflection points |
| 4. K-means++ Clustering | Initialize cluster centers via K-means++ (avoids local optima) | Implemented using `scikit-learn.cluster.KMeans` with `init='k-means++'` |
| 5. Cluster Quality Assessment | Evaluate clustering using Silhouette Coefficient | Coefficient > 0.5 indicates reasonable clustering; <0.5 triggers re-optimization |

#### 3.2.2 Mathematical Formulation
- **Spatial Similarity**: Euclidean distance between task $i$ and $j$, standardized to [0,1]:  
  $$d_{\text{spatial}}(i,j) = \sqrt{(X_i - X_j)^2 + (Y_i - Y_j)^2 + (Z_i - Z_j)^2}$$  
  $$f_1(i,j) = 1 - \frac{d_{\text{spatial}}(i,j) - d_{\text{min}}}{d_{\text{max}} - d_{\text{min}}}$$  
- **System Similarity**: Binary indicator for same-system tasks:  
  $$f_2(i,j) = \begin{cases} 1 & \text{if } K_i = K_j \\ 0 & \text{otherwise} \end{cases}$$  
- **Resource Similarity**: Euclidean distance of 6 resource dimensions (skilled labor, crane, etc.), standardized:  
  $$d_{\text{resource}}(i,j) = \sqrt{\sum_{r=1}^6 (R_i^r - R_j^r)^2}$$  
  $$f_3(i,j) = 1 - \frac{d_{\text{resource}}(i,j) - d_{\text{rmin}}}{d_{\text{rmax}} - d_{\text{rmin}}}$$  
- **Risk Similarity**: Normalized difference in criticality levels:  
  $$f_4(i,j) = 1 - \frac{|C_i - C_j|}{10}$$  
- **Weighted Similarity**: Combined similarity with feature weights ($\omega_1=0.35, \omega_2=0.25, \omega_3=0.15, \omega_4=0.25$):  
  $$S(i,j) = \omega_1 f_1 + \omega_2 f_2 + \omega_3 f_3 + \omega_4 f_4$$  

#### 3.2.3 Key Design Choices
- **Feature Weighting**: Spatial proximity ($\omega_1=0.35$) is prioritized to reduce travel time in high-density Hong Kong sites.
- **K-means++ Initialization**: Avoids poor clustering caused by random center selection (critical for small task datasets, $n=20$ in case study).
- **Silhouette Validation**: Ensures clusters are compact and separated, with engineering judgment applied to boundary tasks.

### 3.3 NSGA-II Dynamic Scheduling Optimization Module
This module (implemented in `nsga2_scheduling.py`) solves the multi-objective scheduling problem, generating Pareto-optimal solutions that balance cost, risk, and delay. It supports dynamic rescheduling for urgent tasks (e.g., typhoon-induced failures).

#### 3.3.1 Core Workflow
| Step | Description | Implementation Details |
|------|-------------|------------------------|
| 1. Encoding | Represent schedules as chromosomes (task cluster IDs in execution order) | Each individual = [Cluster 3, Cluster 1, ...] (execution priority) |
| 2. Population Initialization | Generate random initial population (size = 50) | Ensures coverage of feasible schedule spaces; avoids duplicate individuals |
| 3. Multi-objective Evaluation | Compute three objective functions: total cost ($C_{\text{total}}$), total risk ($R_{\text{risk}}$), total delay ($D_{\text{delay}}$) | Decodes chromosomes to schedules using heuristic resource allocation |
| 4. Fast Non-dominated Sort | Stratify population into Pareto fronts ($F_1$ = optimal, $F_2$ = suboptimal, etc.) | Reduces computational complexity vs. traditional non-dominated sorting |
| 5. Crowding Distance Calculation | Maintain population diversity by measuring proximity of solutions in the same front | Prevents convergence to a narrow subset of optimal solutions |
| 6. Elitism & Genetic Operations | Merge parent/offspring populations (size = 100), select top 50 for next generation | Crossover (probability = 0.9), mutation (probability = 1/n) |
| 7. Dynamic Rescheduling | Trigger re-optimization for urgent tasks (e.g., typhoon-induced failures) | Freezes ongoing tasks, reallocates resources, and updates constraints |

#### 3.3.2 Mathematical Formulation
- **Objective Function (Minimization)**:  
  $$\min Z = \omega_1 C_{\text{total}} + \omega_2 R_{\text{risk}} + \omega_3 D_{\text{delay}}$$  
  Where weights are $\omega_1=0.35$ (cost), $\omega_2=0.45$ (risk), $\omega_3=0.2$ (delay) (calibrated for Hong Kong’s high-cost, safety-prioritized context).

- **Total Cost**: Direct (labor/equipment) + indirect (setup/penalty) costs:  
  $$C_{\text{total}} = C_{\text{direct}} + C_{\text{indirect}}$$  
  $$C_{\text{direct}} = \sum_{i,t} x_{it} (c_i^{\text{manpower}} + c_i^{\text{equipment}})$$  
  $$C_{\text{indirect}} = \sum_i y_{ik} c_i^{\text{setup}} + \sum_t \max\{0, R_{\text{required}}(t) - R_{\text{available}}(t)\} c^{\text{penalty}}$$  

- **Total Risk**: Weighted sum of task criticality levels (delayed tasks incur higher risk):  
  $$R_{\text{risk}} = \sum_{i,t} x_{it} \cdot \frac{C_i}{10} \cdot \gamma_{\text{risk}}$$  

- **Total Delay**: Penalty for tasks exceeding planned completion time:  
  $$D_{\text{delay}} = \sum_i \max\{0, T_i^{\text{actual}} - T_i^{\text{planned}}\} \cdot \omega_i^{\text{criticality}}$$  

#### 3.3.3 Key Design Choices
- **Risk Prioritization**: Higher weight for $R_{\text{risk}}$ ($\omega_2=0.45$) aligns with Hong Kong’s strict safety regulations.
- **Elitism**: Preserves optimal solutions across generations, ensuring convergence to high-quality schedules.
- **Dynamic Trigger**: Rescheduling is triggered by urgent tasks (e.g., typhoon damage) with 40-hour duration thresholds, simulating real-world emergency responses.

## 4. Data Preprocessing Module
Implemented in `data_preprocess.py`, this module cleans and standardizes input data to ensure algorithm robustness. Key steps include:

### 4.1 Data Cleaning
- **Invalid Value Filtering**: Removes missing or unrealistic data (e.g., RPN = 0, spatial coordinates outside project boundaries).
- **Duplicate Removal**: Eliminates redundant failure modes (e.g., duplicate "pipe leakage" entries).

### 4.2 Feature Standardization
- **Min-Max Scaling**: Applies to spatial and resource features to [0,1] range, avoiding bias from different units (e.g., meters vs. labor counts).
- **Binary Encoding**: Converts categorical features (e.g., system affiliation) to binary vectors for K-means compatibility.

### 4.3 Constraint Encoding
- **Time Window Conversion**: Translates Hong Kong’s Noise Control Ordinance and labor laws into numerical constraints (e.g., working hours = 07:00-19:00, Monday-Saturday).
- **Resource Capacity Mapping**: Converts resource limits (e.g., 8 skilled workers, 2 cranes) into algorithm-compatible bounds.

## 5. Parameter Optimization & Robustness
### 5.1 Critical Parameters
| Parameter | Default Value | Optimization Rationale | Impact on Results |
|-----------|---------------|------------------------|-------------------|
| K-means Cluster Number (K) | 4 | Elbow rule on case study data (SSE inflection at K=4) | K<4: Overly large clusters (poor resource optimization); K>4: Fragmented tasks (increased setup costs) |
| NSGA-II Population Size | 50 | Balances diversity and computational efficiency (n=20 tasks) | <50: Insufficient diversity; >50: Diminishing returns in solution quality |
| NSGA-II Crossover Probability | 0.9 | Promotes exploration of new schedule combinations | <0.8: Slow convergence; >0.95: Destroys high-quality solutions |
| NSGA-II Mutation Probability | 1/n (n=number of clusters) | Avoids premature convergence to local optima | <1/n: Stagnation; >1/n: Randomness dominates |
| Feature Weights (K-means) | $\omega_1=0.35, \omega_2=0.25, \omega_3=0.15, \omega_4=0.25$ | Expert validation + sensitivity analysis | Misweighting (e.g., $\omega_1<0.2$) increases travel time and resource waste |

### 5.2 Robustness Considerations
- **Dynamic Task Handling**: Code automatically re-optimizes schedules within 10 seconds of urgent task injection (validated with typhoon-induced failure cases).
- **Resource Fluctuations**: Tolerates ±20% variations in resource availability (e.g., 6-10 skilled workers) without significant schedule degradation.
- **Data Sparsity**: Implements default risk scores for missing failure mode data (based on Hong Kong MiC project averages) to avoid algorithm crashes.

## 6. Limitations & Future Improvements
### 6.1 Current Limitations
1. **Data Dependence**: Relies on structured failure mode and resource data, which is scarce for Hong Kong MiC projects (≤5 years of operational data).
2. **Parameter Subjectivity**: S/O/D scores and feature weights require expert input; miscalibration may bias results.
3. **Computational Complexity**: NSGA-II requires 50-100 iterations (≈30 minutes on consumer hardware) for large task sets (>50 tasks).
4. **Static Weights**: Objective function weights (ω1, ω2, ω3) are fixed; real-world priorities may vary by project.

### 6.2 Future Research Directions
1. **Data Augmentation**: Integrate Building Information Modeling (BIM) data to supplement sparse operational data.
2. **Adaptive Parameter Tuning**: Replace fixed weights with Bayesian optimization to dynamically adjust parameters based on project context.
3. **Parallel Computing**: Optimize NSGA-II with GPU acceleration (e.g., `PyTorch`) to reduce runtime for large-scale projects.
4. **Multi-agent Simulation**: Incorporate stakeholder preferences (e.g., facility managers, contractors) into real-time schedule adjustment.

## 7. Implementation Validation
The code was validated using the Wong Chuk Hang Student Residence (Hong Kong) case study, with 20 IM tasks and real-world constraints. Key validation results include:
- **Optimization Performance**: Reduces total cost by 18.7% and schedule delay by 22.3% compared to static scheduling (project report Section 4.4).
- **Risk Reduction**: High-criticality tasks ($C_i≥8$) are completed 37% faster than traditional methods.
- **Dynamic Response**: Successfully reschedules tasks within 10 seconds of urgent task injection, with only 4.8% increase in total duration (project report Section 4.4.2).
- **Resource Utilization**: Improves skilled labor utilization from 62% to 89% (reduces idle time).

Validation confirms the code meets Hong Kong’s MiC maintenance requirements, with performance metrics aligned with industry standards for quality control and cost efficiency.

## 8. Code Reference
### 8.1 Directory Structure
```
civl6060_mic_scheduling/
├── src/
│   ├── fmea_risk_calc.py        # FMEA risk quantification
│   ├── kmeans_task_clustering.py # Task grouping via K-means
│   ├── nsga2_scheduling.py      # Multi-objective dynamic scheduling
│   ├── data_preprocess.py       # Data cleaning/standardization
│   ├── case_validation.py       # Case study implementation
│   └── visualization/           # Gantt charts, resource utilization plots
├── data/
│   ├── task_metadata.csv        # Task features (spatial, resource, system)
│   ├── failure_dependencies.csv # Failure propagation paths
│   ├── resource_constraints.csv # Labor/equipment limits
│   └── fmea_scores.csv          # S/O/D scores for failure modes
├── config/
│   ├── algorithm_params.json    # K-means/NSGA-II parameters
│   └── system_config.json       # MiC system definitions
└── main.py                      # Entry point (run full pipeline)
```

### 8.2 Code Standards
- Follows PEP 8 style guidelines for readability and maintainability.
- Includes type hints and docstrings for all core functions (e.g., `def calculate_rpn(s: int, o: int, d: int) -> Tuple[int, int]`).
- Implements error handling for edge cases (e.g., empty task lists, invalid resource constraints).
- Generates reproducible results via fixed random seeds (`numpy.random.seed(42)`, `random.seed(42)`).

### 8.3 Dependencies
```
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.2.2
matplotlib==3.7.1
opencv-python==4.8.0.76
```