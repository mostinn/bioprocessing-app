
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.integrate import odeint
import os
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Bioprocessing Educational Simulator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to reduce top padding
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
            }
    </style>
    """, unsafe_allow_html=True)

# --- App Title and Description ---
st.title("🔬 Bioprocessing and Biomanufacturing Simulator")
st.markdown(
    """
    **Magnus Stefansson, MBA, Ph.D.**  
    *Rabb School of Continuing Studies, Division of Graduate Professional Studies, Brandeis University, 475 Old S St, Waltham, MA 02453*
    
    Interactive bioprocessing simulation platform for exploring bioreactor operation modes including batch, fed-batch, 
    repeated fed-batch, and perfusion systems. Features real-time parameter adjustment, productivity analysis, 
    comparative visualization, and data simulation for analysis to enhance understanding of bioprocess engineering principles.
    """
)

# --- Mode Descriptions ---
mode_descriptions = {
    "Batch": "All nutrients added at the start; no input/output during cultivation. Lowest productivity but simplest operation.",
    "Fed-Batch": "Nutrients added incrementally during cultivation to extend growth. Moderate to high productivity.",
    "Repeated Fed-Batch": "Partial harvest followed by re-feeding; multiple cycles with same inoculum. Better productivity than batch.",
    "Bleed-Perfusion": "Continuous feeding and removal; most cells retained, some removed via bleed. Highest stable productivity."
}

# --- Scenario File Management ---
def load_scenarios():
    default_scenarios = {
        "High-Density Perfusion": {
            "mode": "Bleed-Perfusion",
            "params": {
                "initial_substrate": 50.0,
                "initial_biomass": 2.0,
                "initial_volume": 1.0,
                "mu_max": 0.4,
                "ks": 0.7,
                "Y_xs": 0.6,
                "Y_xp": 0.3,
                "product_name": "Monoclonal Antibody",
                "feed_rate": 0.2,
                "feed_substrate": 300.0,
                "bleed_rate": 0.02,
                "cell_retention": 0.95,
            }
        },
        "Substrate-Limited Fed-Batch": {
            "mode": "Fed-Batch",
            "params": {
                "initial_substrate": 5.0,
                "initial_biomass": 1.0,
                "initial_volume": 1.0,
                "mu_max": 0.3,
                "ks": 0.2,
                "Y_xs": 0.5,
                "Y_xp": 0.2,
                "product_name": "Recombinant Protein",
                "feed_substrate": 100.0,
                "exchange_time": 20,
                "exchange_volume_percent": 25,
            }
        },
        "Classical Batch Culture": {
            "mode": "Batch",
            "params": {
                "initial_substrate": 20.0,
                "initial_biomass": 0.5,
                "initial_volume": 1.0,
                "mu_max": 0.25,
                "ks": 1.0,
                "Y_xs": 0.45,
                "Y_xp": 0.15,
                "product_name": "Ethanol",
            }
        },
        "Multi-Cycle Production": {
            "mode": "Repeated Fed-Batch",
            "params": {
                "initial_substrate": 15.0,
                "initial_biomass": 1.5,
                "initial_volume": 2.0,
                "mu_max": 0.35,
                "ks": 0.8,
                "Y_xs": 0.55,
                "Y_xp": 0.25,
                "product_name": "Fatty Acids",
                "feed_substrate": 150.0,
                "harvest_volume_percent": 50,
                "first_harvest_time": 48,
                "subsequent_harvest_time": 24,
                "num_cycles": 5,
            }
        }
    }
    
    try:
        with open('scenarios.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_scenarios

def save_scenarios(scenarios):
    with open('scenarios.json', 'w') as f:
        json.dump(scenarios, f, indent=2)

# --- Initialize Session State ---
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = load_scenarios()

# --- Glossary ---
glossary = {
    "Initial Substrate (g/L)": "The starting concentration of the main nutrient for the cells.",
    "Initial Biomass (g/L)": "The starting concentration of cells in the bioreactor.",
    "Max Specific Growth Rate (mu_max, 1/h)": "The maximum rate at which cells can divide per hour.",
    "Monod Constant (Ks, g/L)": "The substrate concentration at which the growth rate is half of the maximum.",
    "Yield Coefficient (Y_xs, g/g)": "The ratio of biomass produced to substrate consumed.",
    "Product Yield (Y_xp, g/g)": "The ratio of product produced to biomass formed.",
    "Product Name": "The specific product being produced (e.g., proteins, fatty acids, ethanol).",
    "Initial Volume (L)": "The starting volume of the culture in the bioreactor.",
    "Feed Rate (L/h)": "The rate at which fresh medium is added to the bioreactor.",
    "Feed Substrate Concentration (g/L)": "The concentration of the substrate in the feed medium.",
    "Harvest Volume (%)": "The percentage of the working volume to exchange.",
    "Time of First Harvest (h)": "Time for the first harvest/feeding pulse.",
    "Incremental Time for Subsequent Harvests (h)": "Time between subsequent harvest/feeding pulses.",
    "Exchange Time (h)": "The time at which 20% of the working volume is exchanged with fresh medium in Fed-Batch mode.",
    "Exchange Volume (%)": "The percentage of the working volume that is exchanged with fresh medium in the Fed-Batch mode's harvest/feeding cycle.",
    "Number of Cycles": "The total number of cycles to simulate in a repeated fed-batch process.",
    "Bleed Rate (L/h)": "The rate at which culture is removed from the bioreactor in a perfusion system.",
    "Cell Retention": "The fraction of cells that are retained in the bioreactor during perfusion.",
}

# Runtime confirmation for debugging: make it obvious which app code is loaded
print("Loaded Bioprocessing_app — perfusion v2")
try:
    st.sidebar.markdown("See the [**Student Guide**](https://mostinn.github.io/bioprocessing-app/student_guide/STUDENT_GUIDE.html) for details and examples")
except Exception:
    # If Streamlit isn't initialized (e.g., imported for testing), ignore
    pass

# --- Sidebar for Mode Selection and Parameters ---
st.sidebar.title("⚙️ Controls")
st.sidebar.header("Mode Selector")

# --- Scenario Loader ---
st.sidebar.header("Scenario Loader")
scenario_names = list(st.session_state.scenarios.keys())
loaded_scenario = st.sidebar.selectbox("Load a scenario", ["None"] + scenario_names)

if loaded_scenario != "None":
    scenario_data = st.session_state.scenarios[loaded_scenario]
    mode = st.sidebar.selectbox(
        "Choose a bioreactor operation mode:",
        ["Batch", "Fed-Batch", "Repeated Fed-Batch", "Bleed-Perfusion"],
        index=["Batch", "Fed-Batch", "Repeated Fed-Batch", "Bleed-Perfusion"].index(scenario_data['mode'])
    )
    params = scenario_data['params']
else:
    mode = st.sidebar.selectbox(
        "Choose a bioreactor operation mode:",
        ["Batch", "Fed-Batch", "Repeated Fed-Batch", "Bleed-Perfusion"],
    )
    params = {}

# Display mode description
st.sidebar.info(f"**{mode} Mode**: {mode_descriptions[mode]}")

st.sidebar.header("Parameter Input")
# --- Dynamic Parameter Inputs Based on Mode ---
assignment_mode = st.sidebar.checkbox("Assignment Mode")
# UI option: allow user to open all sections by default and persist in session state
# Use session_state.get to preserve previous value across reruns
expand_all = st.sidebar.checkbox(
    "Show all sections expanded",
    value=st.session_state.get('expand_all', False),
    key='expand_all'
)

if mode == "Batch":
    with st.sidebar.expander("📊 Initial Conditions", expanded=expand_all):
        st.caption("Define the starting biomass, substrate, and volume for the batch process.")
        st.caption("Define the starting state of the bioreactor, including biomass and substrate concentrations.")
        st.markdown("##### Bioreactor Starting State")
        
        initial_substrate = st.slider("Initial Substrate (g/L)", 0.1, 100.0,
            params.get('initial_substrate', 20.0),
            help=glossary["Initial Substrate (g/L)"],
            disabled=assignment_mode)
        initial_substrate = st.number_input("Direct input:", value=initial_substrate,
            min_value=0.1, max_value=100.0, step=0.1,
            key="batch_substrate", disabled=assignment_mode,
            label_visibility="collapsed")
        
        initial_biomass = st.slider("Initial Biomass (g/L)", 0.1, 10.0,
            params.get('initial_biomass', 1.0),
            help=glossary["Initial Biomass (g/L)"],
            disabled=assignment_mode)
        initial_biomass = st.number_input("Direct input:", value=initial_biomass,
            min_value=0.1, max_value=10.0, step=0.1,
            key="batch_biomass", disabled=assignment_mode,
            label_visibility="collapsed")
    
    # Growth Kinetics Section
    with st.sidebar.expander("🦠 Growth Kinetics", expanded=expand_all):
        st.caption("Specify important kinetic parameters such as maximum growth rate and Monod constant for this mode.")
        st.markdown("##### Monod Model Parameters")
        
        mu_max = st.slider("Max Growth Rate (mu_max, 1/h)", 0.01, 1.0,
            params.get('mu_max', 0.3),
            help=glossary["Max Specific Growth Rate (mu_max, 1/h)"],
            disabled=assignment_mode)
        mu_max = st.number_input("Direct input:", value=mu_max,
            min_value=0.01, max_value=1.0, step=0.01,
            key="batch_mu_max", disabled=assignment_mode,
            label_visibility="collapsed")
        
        ks = st.slider("Monod Constant (Ks, g/L)", 0.01, 5.0,
            params.get('ks', 0.5),
            help=glossary["Monod Constant (Ks, g/L)"],
            disabled=assignment_mode)
        ks = st.number_input("Direct input:", value=ks,
            min_value=0.01, max_value=5.0, step=0.01,
                    key="batch_ks", disabled=assignment_mode,
                    label_visibility="collapsed")
                
    # Yield Coefficients Section
    with st.sidebar.expander("📈 Yield Coefficients", expanded=expand_all):
        st.caption("Enter biomass and product yield coefficients, which describe how efficiently substrate is converted.")
        st.markdown("##### Conversion Efficiencies")
        
        Y_xs = st.slider("Biomass Yield (Y_xs, g/g)", 0.1, 1.0,
            params.get('Y_xs', 0.5),
            help=glossary["Yield Coefficient (Y_xs, g/g)"],
            disabled=assignment_mode)
        Y_xs = st.number_input("Direct input:", value=Y_xs,
            min_value=0.1, max_value=1.0, step=0.01,
            key="batch_Y_xs", disabled=assignment_mode,
            label_visibility="collapsed")
        
        Y_xp = st.slider("Product Yield (Y_xp, g/g)", 0.01, 1.0,
            params.get('Y_xp', 0.2),
            help=glossary["Product Yield (Y_xp, g/g)"],
            disabled=assignment_mode)
        Y_xp = st.number_input("Direct input:", value=Y_xp,
            min_value=0.01, max_value=1.0, step=0.01,
            key="batch_Y_xp", disabled=assignment_mode,
            label_visibility="collapsed")
        
        product_name = st.text_input("Product Name",
            params.get('product_name', 'Protein'),
            help=glossary["Product Name"],
            disabled=assignment_mode,
            key="batch_product_name")
    current_params = {"initial_substrate": initial_substrate, "initial_biomass": initial_biomass, "initial_volume": 1.0, "mu_max": mu_max, "ks": ks, "Y_xs": Y_xs, "Y_xp": Y_xp, "product_name": product_name}

elif mode == "Fed-Batch":
    st.sidebar.subheader("🔄 Fed-Batch Configuration")
    
    # Initial Conditions Section
    with st.sidebar.expander("📊 Initial Conditions", expanded=expand_all):
        st.caption("Define the starting biomass, substrate, and volume for the fed-batch process.")
        st.markdown("##### Bioreactor Starting State")
        
        initial_substrate = st.slider("Initial Substrate (g/L)", 0.1, 100.0,
            params.get('initial_substrate', 10.0),
            help=glossary["Initial Substrate (g/L)"],
            disabled=assignment_mode)
        initial_substrate = st.number_input("Direct input:", value=initial_substrate,
            min_value=0.1, max_value=100.0, step=0.1,
            key="fed_substrate", disabled=assignment_mode,
            label_visibility="collapsed")
        
        initial_biomass = st.slider("Initial Biomass (g/L)", 0.1, 10.0,
            params.get('initial_biomass', 1.0),
            help=glossary["Initial Biomass (g/L)"],
            disabled=assignment_mode)
        initial_biomass = st.number_input("Direct input:", value=initial_biomass,
            min_value=0.1, max_value=10.0, step=0.1,
            key="fed_biomass", disabled=assignment_mode,
            label_visibility="collapsed")
        
        initial_volume = st.slider("Initial Volume (L)", 0.1, 10.0,
            params.get('initial_volume', 1.0),
            help=glossary["Initial Volume (L)"],
            disabled=assignment_mode)
        initial_volume = st.number_input("Direct input:", value=initial_volume,
            min_value=0.1, max_value=10.0, step=0.1,
            key="fed_volume", disabled=assignment_mode,
            label_visibility="collapsed")
    
    # Growth Kinetics Section
    with st.sidebar.expander("🦠 Growth Kinetics", expanded=expand_all):
        st.markdown("##### Monod Model Parameters")
        
        mu_max = st.slider("Max Growth Rate (mu_max, 1/h)", 0.01, 1.0,
            params.get('mu_max', 0.3),
            help=glossary["Max Specific Growth Rate (mu_max, 1/h)"],
            disabled=assignment_mode)
        mu_max = st.number_input("Direct input:", value=mu_max,
            min_value=0.01, max_value=1.0, step=0.01,
            key="fed_mu_max", disabled=assignment_mode,
            label_visibility="collapsed")
        
        ks = st.slider("Monod Constant (Ks, g/L)", 0.01, 5.0,
            params.get('ks', 0.5),
            help=glossary["Monod Constant (Ks, g/L)"],
            disabled=assignment_mode)
        ks = st.number_input("Direct input:", value=ks,
            min_value=0.01, max_value=5.0, step=0.01,
            key="fed_ks", disabled=assignment_mode,
            label_visibility="collapsed")
    
    # Yield Coefficients Section
    with st.sidebar.expander("📈 Yield Coefficients", expanded=expand_all):
        st.markdown("##### Conversion Efficiencies")
        
        Y_xs = st.slider("Biomass Yield (Y_xs, g/g)", 0.1, 1.0,
            params.get('Y_xs', 0.5),
            help=glossary["Yield Coefficient (Y_xs, g/g)"],
            disabled=assignment_mode)
        Y_xs = st.number_input("Direct input:", value=Y_xs,
            min_value=0.1, max_value=1.0, step=0.01,
            key="fed_Y_xs", disabled=assignment_mode,
            label_visibility="collapsed")
        
        Y_xp = st.slider("Product Yield (Y_xp, g/g)", 0.01, 1.0,
            params.get('Y_xp', 0.2),
            help=glossary["Product Yield (Y_xp, g/g)"],
            disabled=assignment_mode)
        Y_xp = st.number_input("Direct input:", value=Y_xp,
            min_value=0.01, max_value=1.0, step=0.01,
            key="fed_Y_xp", disabled=assignment_mode,
            label_visibility="collapsed")
        
        product_name = st.text_input("Product Name",
            params.get('product_name', 'Protein'),
            help=glossary["Product Name"],
            disabled=assignment_mode,
            key="fed_product_name")
    
    # Feeding Strategy Section
    with st.sidebar.expander("🔄 Feeding Strategy", expanded=expand_all):
        st.markdown("##### Feed & Exchange Parameters")
        
        feed_substrate = st.slider("Feed [S] (g/L)", 50.0, 500.0,
            params.get('feed_substrate', 200.0),
            help=glossary["Feed Substrate Concentration (g/L)"],
            disabled=assignment_mode)
        feed_substrate = st.number_input("Direct input:", value=feed_substrate,
            min_value=50.0, max_value=500.0, step=1.0,
            key="fed_feed_substrate", disabled=assignment_mode,
            label_visibility="collapsed")
        
        exchange_time = st.slider("Exchange Time (h)", 0, 50,
            params.get('exchange_time', 25),
            help=glossary["Exchange Time (h)"],
            disabled=assignment_mode)
        exchange_time = st.number_input("Direct input:", value=exchange_time,
            min_value=0, max_value=50, step=1,
            key="fed_exchange_time", disabled=assignment_mode,
            label_visibility="collapsed")
        
        exchange_volume_percent = st.slider("Exchange Volume (%)", 0, 100,
            params.get('exchange_volume_percent', 20),
            help=glossary["Exchange Volume (%)"],
            disabled=assignment_mode)
        exchange_volume_percent = st.number_input("Direct input:", value=exchange_volume_percent,
            min_value=0, max_value=100, step=1,
            key="fed_exchange_volume", disabled=assignment_mode,
            label_visibility="collapsed")
    
    current_params = {"initial_substrate": initial_substrate, "initial_biomass": initial_biomass, "initial_volume": initial_volume, "mu_max": mu_max, "ks": ks, "Y_xs": Y_xs, "Y_xp": Y_xp, "product_name": product_name, "feed_substrate": feed_substrate, "exchange_time": exchange_time, "exchange_volume_percent": exchange_volume_percent}

elif mode == "Repeated Fed-Batch":
    st.sidebar.subheader("🔁 Repeated Fed-Batch Configuration")
    
    # Initial Conditions Section
    with st.sidebar.expander("📊 Initial Conditions", expanded=expand_all):
        st.markdown("##### Bioreactor Starting State")
        
        initial_substrate = st.slider("Initial Substrate (g/L)", 0.1, 100.0,
            params.get('initial_substrate', 10.0),
            help=glossary["Initial Substrate (g/L)"],
            disabled=assignment_mode)
        initial_substrate = st.number_input("Direct input:", value=initial_substrate,
            min_value=0.1, max_value=100.0, step=0.1,
            key="rfb_substrate", disabled=assignment_mode,
            label_visibility="collapsed")
        
        initial_biomass = st.slider("Initial Biomass (g/L)", 0.1, 10.0,
            params.get('initial_biomass', 1.0),
            help=glossary["Initial Biomass (g/L)"],
            disabled=assignment_mode)
        initial_biomass = st.number_input("Direct input:", value=initial_biomass,
            min_value=0.1, max_value=10.0, step=0.1,
            key="rfb_biomass", disabled=assignment_mode,
            label_visibility="collapsed")
        
        initial_volume = st.slider("Initial Volume (L)", 0.1, 10.0,
            params.get('initial_volume', 1.0),
            help=glossary["Initial Volume (L)"],
            disabled=assignment_mode)
        initial_volume = st.number_input("Direct input:", value=initial_volume,
            min_value=0.1, max_value=10.0, step=0.1,
            key="rfb_volume", disabled=assignment_mode,
            label_visibility="collapsed")
    
    # Growth Kinetics Section
    with st.sidebar.expander("🦠 Growth Kinetics", expanded=expand_all):
        st.markdown("##### Monod Model Parameters")
        
        mu_max = st.slider("Max Growth Rate (mu_max, 1/h)", 0.01, 1.0,
            params.get('mu_max', 0.3),
            help=glossary["Max Specific Growth Rate (mu_max, 1/h)"],
            disabled=assignment_mode)
        mu_max = st.number_input("Direct input:", value=mu_max,
            min_value=0.01, max_value=1.0, step=0.01,
            key="rfb_mu_max", disabled=assignment_mode,
            label_visibility="collapsed")
        
        ks = st.slider("Monod Constant (Ks, g/L)", 0.01, 5.0,
            params.get('ks', 0.5),
            help=glossary["Monod Constant (Ks, g/L)"],
            disabled=assignment_mode)
        ks = st.number_input("Direct input:", value=ks,
            min_value=0.01, max_value=5.0, step=0.01,
            key="rfb_ks", disabled=assignment_mode,
            label_visibility="collapsed")
    
    # Yield Coefficients Section
    with st.sidebar.expander("📈 Yield Coefficients", expanded=expand_all):
        st.markdown("##### Conversion Efficiencies")
        
        Y_xs = st.slider("Biomass Yield (Y_xs, g/g)", 0.1, 1.0,
            params.get('Y_xs', 0.5),
            help=glossary["Yield Coefficient (Y_xs, g/g)"],
            disabled=assignment_mode)
        Y_xs = st.number_input("Direct input:", value=Y_xs,
            min_value=0.1, max_value=1.0, step=0.01,
            key="rfb_Y_xs", disabled=assignment_mode,
            label_visibility="collapsed")
        
        Y_xp = st.slider("Product Yield (Y_xp, g/g)", 0.01, 1.0,
            params.get('Y_xp', 0.2),
            help=glossary["Product Yield (Y_xp, g/g)"],
            disabled=assignment_mode)
        Y_xp = st.number_input("Direct input:", value=Y_xp,
            min_value=0.01, max_value=1.0, step=0.01,
            key="rfb_Y_xp", disabled=assignment_mode,
            label_visibility="collapsed")
        
        product_name = st.text_input("Product Name",
            params.get('product_name', 'Protein'),
            help=glossary["Product Name"],
            disabled=assignment_mode,
            key="rfb_product_name")
    
    # Harvest & Feed Strategy Section
    with st.sidebar.expander("🔄 Harvest & Feed Strategy", expanded=expand_all):
        st.markdown("##### Cycle Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            feed_substrate = st.slider("Feed [S] (g/L)", 50.0, 500.0,
                params.get('feed_substrate', 200.0),
                help=glossary["Feed Substrate Concentration (g/L)"],
                disabled=assignment_mode)
            feed_substrate = st.number_input("Direct input:", value=feed_substrate,
                min_value=50.0, max_value=500.0, step=1.0,
                key="rfb_feed_substrate", disabled=assignment_mode,
                label_visibility="collapsed")
        
        with col2:
            harvest_volume_percent = st.slider("Harvest Volume (%)", 0, 100,
                params.get('harvest_volume_percent', 20),
                help=glossary["Harvest Volume (%)"],
                disabled=assignment_mode)
            harvest_volume_percent = st.number_input("Direct input:", value=harvest_volume_percent,
                min_value=0, max_value=100, step=1,
                key="rfb_harvest_volume", disabled=assignment_mode,
                label_visibility="collapsed")
        
        # First harvest and subsequent schedule
        first_harvest_time = st.slider("First Harvest Time (h)", 1, 100,
            params.get('first_harvest_time', 24),
            help="Time for the first harvest/feeding pulse.",
            disabled=assignment_mode)
        first_harvest_time = st.number_input("Direct input:", value=first_harvest_time,
            min_value=1, max_value=100, step=1,
            key="rfb_first_harvest_time", disabled=assignment_mode,
            label_visibility="collapsed")
        
        subsequent_harvest_time = st.slider("Time Between Harvests (h)", 1, 100,
            params.get('subsequent_harvest_time', 24),
            help="Time between subsequent harvest/feeding pulses.",
            disabled=assignment_mode)
        subsequent_harvest_time = st.number_input("Direct input:", value=subsequent_harvest_time,
            min_value=1, max_value=100, step=1,
            key="rfb_subsequent_harvest_time", disabled=assignment_mode,
            label_visibility="collapsed")
        
        num_cycles = st.slider("Number of Cycles", 1, 10, params.get('num_cycles', 3), help=glossary["Number of Cycles"], disabled=assignment_mode)
        num_cycles = st.number_input("Direct input:", value=num_cycles, min_value=1, max_value=10, step=1, key="rfb_num_cycles", disabled=assignment_mode, label_visibility="collapsed")

    current_params = {"initial_substrate": initial_substrate, "initial_biomass": initial_biomass, "initial_volume": initial_volume, "mu_max": mu_max, "ks": ks, "Y_xs": Y_xs, "Y_xp": Y_xp, "product_name": product_name, "feed_substrate": feed_substrate, "harvest_volume_percent": harvest_volume_percent, "first_harvest_time": first_harvest_time, "subsequent_harvest_time": subsequent_harvest_time, "num_cycles": num_cycles}

elif mode == "Bleed-Perfusion":
    st.sidebar.subheader("🔬 Bleed-Perfusion Configuration")
    
    # Initial Conditions Section
    with st.sidebar.expander("📊 Initial Conditions", expanded=expand_all):
        st.markdown("##### Bioreactor Starting State")
        
        initial_substrate = st.slider("Initial Substrate (g/L)", 0.1, 100.0, 
            params.get('initial_substrate', 50.0), 
            help=glossary["Initial Substrate (g/L)"], 
            disabled=assignment_mode)
        initial_substrate = st.number_input("Direct input:", value=initial_substrate, 
            min_value=0.1, max_value=100.0, step=0.1, 
            key="bp_substrate", disabled=assignment_mode, 
            label_visibility="collapsed")
        
        initial_biomass = st.slider("Initial Biomass (g/L)", 0.1, 10.0, 
            params.get('initial_biomass', 2.0), 
            help=glossary["Initial Biomass (g/L)"], 
            disabled=assignment_mode)
        initial_biomass = st.number_input("Direct input:", value=initial_biomass, 
            min_value=0.1, max_value=10.0, step=0.1, 
            key="bp_biomass", disabled=assignment_mode, 
            label_visibility="collapsed")
        
        initial_volume = st.slider("Initial Volume (L)", 0.1, 10.0, 
            params.get('initial_volume', 1.0), 
            help=glossary["Initial Volume (L)"], 
            disabled=assignment_mode)
        initial_volume = st.number_input("Direct input:", value=initial_volume, 
            min_value=0.1, max_value=10.0, step=0.1, 
            key="bp_volume", disabled=assignment_mode, 
            label_visibility="collapsed")
    
    # Growth Kinetics Section
    with st.sidebar.expander("🦠 Growth Kinetics", expanded=expand_all):
        st.markdown("##### Monod Model Parameters")
        
        mu_max = st.slider("Max Growth Rate (mu_max, 1/h)", 0.01, 1.0, 
            params.get('mu_max', 0.4), 
            help=glossary["Max Specific Growth Rate (mu_max, 1/h)"], 
            disabled=assignment_mode)
        mu_max = st.number_input("Direct input:", value=mu_max, 
            min_value=0.01, max_value=1.0, step=0.01, 
            key="bp_mu_max", disabled=assignment_mode, 
            label_visibility="collapsed")
        
        ks = st.slider("Monod Constant (Ks, g/L)", 0.01, 5.0, 
            params.get('ks', 0.7), 
            help=glossary["Monod Constant (Ks, g/L)"], 
            disabled=assignment_mode)
        ks = st.number_input("Direct input:", value=ks, 
            min_value=0.01, max_value=5.0, step=0.01, 
            key="bp_ks", disabled=assignment_mode, 
            label_visibility="collapsed")
    
    # Yield Coefficients Section
    with st.sidebar.expander("📈 Yield Coefficients", expanded=expand_all):
        st.markdown("##### Conversion Efficiencies")
        
        Y_xs = st.slider("Biomass Yield (Y_xs, g/g)", 0.1, 1.0, 
            params.get('Y_xs', 0.6), 
            help=glossary["Yield Coefficient (Y_xs, g/g)"], 
            disabled=assignment_mode)
        Y_xs = st.number_input("Direct input:", value=Y_xs, 
            min_value=0.1, max_value=1.0, step=0.01, 
            key="bp_Y_xs", disabled=assignment_mode, 
            label_visibility="collapsed")
        
        Y_xp = st.slider("Product Yield (Y_xp, g/g)", 0.01, 1.0, 
            params.get('Y_xp', 0.3), 
            help=glossary["Product Yield (Y_xp, g/g)"], 
            disabled=assignment_mode)
        Y_xp = st.number_input("Direct input:", value=Y_xp, 
            min_value=0.01, max_value=1.0, step=0.01, 
            key="bp_Y_xp", disabled=assignment_mode, 
            label_visibility="collapsed")
        
        product_name = st.text_input("Product Name", 
            params.get('product_name', 'Monoclonal Antibody'), 
            help=glossary["Product Name"], 
            disabled=assignment_mode, 
            key="bp_product_name")
    
    # Perfusion Operation Section
    with st.sidebar.expander("⚡ Perfusion Operation", expanded=expand_all):
        st.markdown("##### Feed & Bleed Control")
        
        col1, col2 = st.columns(2)
        with col1:
            feed_rate = st.slider("Feed Rate (L/h)", 0.0, 1.0, 
                params.get('feed_rate', 0.2), 
                help=glossary["Feed Rate (L/h)"], 
                disabled=assignment_mode)
            feed_rate = st.number_input("Direct input:", value=feed_rate, 
                min_value=0.0, max_value=1.0, step=0.01, 
                key="bp_feed_rate", disabled=assignment_mode, 
                label_visibility="collapsed")
        
        with col2:
            bleed_rate = st.slider("Bleed Rate (L/h)", 0.0, 1.0, 
                params.get('bleed_rate', 0.02), 
                help=glossary["Bleed Rate (L/h)"], 
                disabled=assignment_mode)
            bleed_rate = st.number_input("Direct input:", value=bleed_rate, 
                min_value=0.0, max_value=1.0, step=0.01, 
                key="bp_bleed_rate", disabled=assignment_mode, 
                label_visibility="collapsed")
        
        feed_substrate = st.slider("Feed [S] (g/L)", 50.0, 500.0, 
            params.get('feed_substrate', 300.0), 
            help=glossary["Feed Substrate Concentration (g/L)"], 
            disabled=assignment_mode)
        feed_substrate = st.number_input("Direct input:", value=feed_substrate, 
            min_value=50.0, max_value=500.0, step=1.0, 
            key="bp_feed_substrate", disabled=assignment_mode, 
            label_visibility="collapsed")
        
        cell_retention = st.slider("Cell Retention", 0.0, 1.0, 
            params.get('cell_retention', 0.95), 
            help=glossary["Cell Retention"], 
            disabled=assignment_mode)
        cell_retention = st.number_input("Direct input:", value=cell_retention, 
            min_value=0.0, max_value=1.0, step=0.01, 
            key="bp_cell_retention", disabled=assignment_mode, 
            label_visibility="collapsed")
    
    # Basic parameters dictionary for simple Monod model
    current_params = {
        "initial_substrate": initial_substrate,
        "initial_biomass": initial_biomass,
        "initial_volume": initial_volume,
        "mu_max": mu_max,
        "ks": ks,
        "Y_xs": Y_xs,
        "Y_xp": Y_xp,
        "product_name": product_name,
        "feed_rate": feed_rate,
        "feed_substrate": feed_substrate,
        "bleed_rate": bleed_rate,
        "cell_retention": cell_retention
    }


# --- Productivity Calculations ---
def calculate_productivity_metrics(df, mode, params):
    metrics = {}
    
    if not df.empty:
        final_biomass = df['Biomass (g/L)'].iloc[-1]
        initial_biomass = df['Biomass (g/L)'].iloc[0]
        total_time = df['Time (h)'].iloc[-1]
        
        # Product metrics
        product_name = params.get('product_name', 'Product')
        product_col = f"{product_name} (g/L)"
        if product_col in df.columns:
            final_product = df[product_col].iloc[-1]
            initial_product = df[product_col].iloc[0]
        else:
            final_product = initial_product = 0
        
        if mode == "Batch":
            initial_volume = params.get('initial_volume', 1.0)
            metrics['Biomass Productivity (g/L/h)'] = (final_biomass - initial_biomass) / total_time
            metrics['Product Productivity (g/L/h)'] = (final_product - initial_product) / total_time
            metrics['Total Biomass Produced (g)'] = (final_biomass - initial_biomass) * initial_volume
            metrics['Total Product Produced (g)'] = (final_product - initial_product) * initial_volume
            
        elif mode == "Fed-Batch":
            final_volume = df['Volume (L)'].iloc[-1] if 'Volume (L)' in df.columns else params.get('initial_volume', 1.0)
            metrics['Biomass Productivity (g/L/h)'] = (final_biomass - initial_biomass) / total_time
            metrics['Product Productivity (g/L/h)'] = (final_product - initial_product) / total_time
            metrics['Total Biomass Produced (g)'] = (final_biomass * final_volume) - (initial_biomass * params.get('initial_volume', 1.0))
            metrics['Total Product Produced (g)'] = final_product * final_volume
            
        elif mode == "Repeated Fed-Batch":
            cycle_time = params.get('cycle_time', 24)
            num_cycles = params.get('num_cycles', 3)
            harvest_volume_percent = params.get('harvest_volume_percent', 20)
            initial_volume = params.get('initial_volume', 1.0)

            #This is a simplification, in reality volume changes.
            harvest_volume = initial_volume * (harvest_volume_percent / 100.0)

            biomass_per_cycle = final_biomass * harvest_volume
            product_per_cycle = final_product * harvest_volume
            metrics['Biomass Productivity (g/L/h)'] = biomass_per_cycle / cycle_time
            metrics['Product Productivity (g/L/h)'] = product_per_cycle / cycle_time
            metrics['Total Biomass Produced (g)'] = biomass_per_cycle * num_cycles
            metrics['Total Product Produced (g)'] = product_per_cycle * num_cycles
            
        elif mode == "Bleed-Perfusion":
            bleed_rate = params.get('bleed_rate', 0.01)
            volume = params.get('initial_volume', 1.0)
            metrics['Biomass Productivity (g/L/h)'] = final_biomass * bleed_rate / volume
            metrics['Product Productivity (g/L/h)'] = final_product * bleed_rate / volume
            metrics['Total Biomass Produced (g)'] = final_biomass * bleed_rate * total_time
            metrics['Total Product Produced (g)'] = final_product * bleed_rate * total_time
        
        initial_substrate = df['Substrate (g/L)'].iloc[0]
        final_substrate = df['Substrate (g/L)'].iloc[-1]
        substrate_consumed = initial_substrate - final_substrate
        
        if substrate_consumed > 0:
            metrics['Substrate to Biomass Efficiency'] = (final_biomass - initial_biomass) / substrate_consumed
            metrics['Substrate to Product Efficiency'] = (final_product - initial_product) / substrate_consumed
        else:
            metrics['Substrate to Biomass Efficiency'] = 0
            metrics['Substrate to Product Efficiency'] = 0
            
        if len(df) > 1:
            growth_rates = np.diff(np.log(df['Biomass (g/L)'])) / np.diff(df['Time (h)'])
            metrics['Max Growth Rate Achieved (1/h)'] = np.max(growth_rates[growth_rates > 0]) if len(growth_rates[growth_rates > 0]) > 0 else 0
        else:
            metrics['Max Growth Rate Achieved (1/h)'] = 0
    
    return metrics


# --- Kinetics Engine ---
def batch_kinetics(y, t, mu_max, Ks, Y_xs, Y_xp):
    X, S, P = y
    mu = mu_max * S / (Ks + S)
    dX_dt = mu * X
    dS_dt = -1/Y_xs * dX_dt
    dP_dt = Y_xp * dX_dt
    return [dX_dt, dS_dt, dP_dt]

def fed_batch_kinetics(y, t, mu_max, Ks, Y_xs, Y_xp, F, V, Sf):
    X, S, P = y
    mu = mu_max * S / (Ks + S)
    D = F / V
    dX_dt = mu * X - D * X
    dS_dt = D * (Sf - S) - (mu * X / Y_xs)
    dP_dt = Y_xp * mu * X - D * P
    return [dX_dt, dS_dt, dP_dt]

def perfusion_kinetics(y, t, mu_max, Ks, Y_xs, Y_xp, D, Sf, R, D_bleed):
    """
    Perfusion bioreactor kinetics with substrate-dependent culture crash.
    
    Key Features:
    1. Monod growth until substrate depletion
    2. Complete crash at critical substrate level (0.0015% of peak)
    3. No biological recovery after crash
    4. Physical processes (dilution) continue post-crash
    
    Args:
        y: [X, S, P] - Biomass, Substrate, Product (g/L)
        mu_max: maximum growth rate (1/h)
        Ks: Monod constant (g/L)
        Y_xs: biomass yield (g X/g S)
        Y_xp: product yield (g P/g X)
        D: feed dilution rate (1/h)
        Sf: feed substrate (g/L)
        R: cell retention (0-1)
        D_bleed: bleed dilution rate (1/h)
    """
    # Extract current state
    X, S, P = y
    S = max(0.0, S)  # Ensure non-negative substrate
    D_total = D + D_bleed
    
    # Track maximum substrate concentration
    if not hasattr(perfusion_kinetics, 'S_max'):
        perfusion_kinetics.S_max = max(Sf, S)
    perfusion_kinetics.S_max = max(perfusion_kinetics.S_max, S)
    
    # Critical substrate threshold for crash (0.0015% of peak)
    S_threshold = 0.000015 * perfusion_kinetics.S_max
    
    # Culture state determination
    if S <= S_threshold:
        # CRASH STATE: Complete cessation of biological activity
        dX_dt = -D_total * X    # Cell washout
        dS_dt = D * (Sf - S)    # Substrate dilution only
        dP_dt = -D_total * P    # Product washout
        
        # Store crash state for UI indicators
        perfusion_kinetics.crashed = True
        
    else:
        # NORMAL OPERATION: Active cell growth
        mu = mu_max * S / (Ks + S)
        
        # Cell mass balance
        cell_growth = mu * X                    # Growth
        cell_overflow = -(1.0 - R) * D * X      # Overflow loss (with retention)
        cell_bleed = -D_bleed * X              # Controlled removal
        dX_dt = cell_growth + cell_overflow + cell_bleed
        
        # Substrate mass balance
        substrate_in = D * Sf                   # Feed in
        substrate_out = -D_total * S            # Flow out
        substrate_consumed = -(mu * X / Y_xs)   # Consumption
        dS_dt = substrate_in + substrate_out + substrate_consumed
        
        # Product mass balance
        product_formation = Y_xp * mu * X       # Formation
        product_out = -D_total * P              # Flow out
        dP_dt = product_formation + product_out
        
        # Update crash tracking
        perfusion_kinetics.crashed = False
    
    return [dX_dt, dS_dt, dP_dt]


def unified_cstr_kinetics(y, t,
                          mu_max, Ks,
                          Y_G, m,
                          alpha, beta,
                          D, Sf, R, D_bleed,
                          k_d=0.0,
                          mu_model='monod',
                          K_I=None,
                          P_max=None,
                          inh_n=1,
                          use_pirt=False):
    """
    Unified CSTR kinetics implementing Monod/Haldane growth, Pirt substrate uptake,
    and Luedeking-Piret product formation. Returns [dX_dt, dS_dt, dP_dt].

    Parameters
    - y: [X, S, P]
    - mu_model: 'monod' | 'haldane' | 'product_inhibition' (product_inhibition multiplies Monod by (1-P/P_max)^n)
    - Y_G: true growth yield (gX/gS)
    - m: maintenance (gS/gX/h)
    - alpha, beta: Luedeking-Piret coefficients
    - k_d: biomass decay rate (1/h)
    """
    X, S, P = y
    S = max(0.0, S)

    # compute base mu depending on selected model
    if mu_model == 'haldane' and K_I is not None:
        mu = mu_max * S / (Ks + S + (S**2 / K_I if K_I and K_I > 0 else 0.0))
    else:
        # default Monod
        mu = mu_max * S / (Ks + S) if (Ks + S) > 0 else 0.0

    # product inhibition multiplier
    if mu_model == 'product_inhibition' and P_max is not None and P_max > 0:
        inh = max(0.0, (1.0 - (P / P_max))) ** inh_n
        mu = mu * inh

    # Allow uptake/Pirt formulation if requested (qS explicit)
    if use_pirt:
        qS = (mu / Y_G) + m  # specific substrate uptake (gS/gX/h)
        # Prevent negative uptake
        qS = max(0.0, qS)
        dS_dt = D * Sf - (D + D_bleed) * S - qS * X
        # Recompute mu from qS if needed (invert Pirt): mu = Y_G * (qS - m)
        mu = Y_G * max(0.0, qS - m)
    else:
        # substrate consumption via yield and growth
        dS_dt = D * Sf - (D + D_bleed) * S - (mu * X / Y_G)

    # specific product formation (Luedeking-Piret)
    qP = alpha * mu + beta

    # Biomass balance — includes washout and decay; cell retention handled externally via R
    dX_dt = mu * X - (1.0 - R) * D * X - D_bleed * X - k_d * X

    # Product balance
    dP_dt = qP * X - (D + D_bleed) * P

    return [dX_dt, dS_dt, dP_dt]

# --- Simulation Runner ---
def run_simulation(mode, params):
    t_span = np.linspace(0, 50, 500)
    df = pd.DataFrame()
    product_name = params.get('product_name', 'Product')

    if mode == "Batch":
        y0 = [params['initial_biomass'], params['initial_substrate'], 0.0]
        sol = odeint(batch_kinetics, y0, t_span, args=(params['mu_max'], params['ks'], params['Y_xs'], params['Y_xp']))
        X, S, P = sol[:, 0], sol[:, 1], sol[:, 2]
        df = pd.DataFrame({"Time (h)": t_span, "Biomass (g/L)": X, "Substrate (g/L)": S, f"{product_name} (g/L)": P})

    elif mode == "Fed-Batch":
        total_time = 50
        exchange_time = params.get('exchange_time', 25)

        y0 = [params['initial_biomass'], params['initial_substrate'], 0.0]
        V = params['initial_volume']

        # 1. Batch phase before exchange
        t_before = np.linspace(0, exchange_time, 250)
        sol_before = odeint(batch_kinetics, y0, t_before, args=(params['mu_max'], params['ks'], params['Y_xs'], params['Y_xp']))

        # Store results
        t_results = list(t_before)
        x_results = list(sol_before[:, 0])
        s_results = list(sol_before[:, 1])
        p_results = list(sol_before[:, 2])
        v_results = [V] * len(t_before) # Volume is constant during batch phase

        # 2. Apply the 20% volume exchange
        y_before_exchange = sol_before[-1]
        X_before, S_before, P_before = y_before_exchange[0], y_before_exchange[1], y_before_exchange[2]
        
        exchange_volume_percent = params.get('exchange_volume_percent', 20)
        exchange_fraction = exchange_volume_percent / 100.0
        keep_fraction = 1.0 - exchange_fraction

        # Concentrations after exchange
        S_after = keep_fraction * S_before + exchange_fraction * params['feed_substrate']
        X_after = keep_fraction * X_before
        P_after = keep_fraction * P_before
        
        # Volume does not change in this model of exchange
        V_after_exchange = V 

        # Add a point for the event
        t_results.append(exchange_time)
        x_results.append(X_after)
        s_results.append(S_after)
        p_results.append(P_after)
        v_results.append(V_after_exchange)

        # 3. Batch phase after exchange
        y0_after = [X_after, S_after, P_after]
        
        t_after = np.linspace(exchange_time, total_time, 250)
        sol_after = odeint(batch_kinetics, y0_after, t_after, args=(params['mu_max'], params['ks'], params['Y_xs'], params['Y_xp']))

        # Append results
        t_results.extend(t_after[1:])
        x_results.extend(sol_after[1:, 0])
        s_results.extend(sol_after[1:, 1])
        p_results.extend(sol_after[1:, 2])
        v_results.extend([V_after_exchange] * (len(t_after) - 1))

        df = pd.DataFrame({
            "Time (h)": t_results,
            "Biomass (g/L)": x_results,
            "Substrate (g/L)": s_results,
            f"{product_name} (g/L)": p_results,
            "Volume (L)": v_results
        })

    elif mode == "Repeated Fed-Batch":
        first_harvest_time = params.get('first_harvest_time', 24)
        subsequent_harvest_time = params.get('subsequent_harvest_time', 24)
        num_cycles = params.get('num_cycles', 3)
        harvest_volume_percent = params.get('harvest_volume_percent', 20)

        t_total, X_total, S_total, P_total, V_total = [], [], [], [], []
        
        y0 = [params['initial_biomass'], params['initial_substrate'], 0.0]
        V0 = params['initial_volume']
        
        current_time_offset = 0

        # Initial batch phase
        t_first_cycle = np.linspace(0, first_harvest_time, int(first_harvest_time * 10))
        sol = odeint(batch_kinetics, y0, t_first_cycle, args=(params['mu_max'], params['ks'], params['Y_xs'], params['Y_xp']))

        # Record results
        t_total.extend(t_first_cycle + current_time_offset)
        X_total.extend(sol[:, 0])
        S_total.extend(sol[:, 1])
        P_total.extend(sol[:, 2])
        V_total.extend([V0] * len(t_first_cycle))
        
        current_time_offset = t_total[-1]

        for i in range(num_cycles):
            # Harvest and Feed
            X_before, S_before, P_before = X_total[-1], S_total[-1], P_total[-1]
            V_before = V_total[-1]

            harvest_volume = V_before * (harvest_volume_percent / 100.0)
            feed_volume = harvest_volume  # Symmetric exchange

            V_after_harvest = V_before - harvest_volume
            
            # Dilution from harvesting
            X_after_harvest = X_before
            S_after_harvest = S_before
            P_after_harvest = P_before

            # Refeeding (dilution)
            V_after_feed = V_after_harvest + feed_volume
            
            S_after_feed = (S_after_harvest * V_after_harvest + params['feed_substrate'] * feed_volume) / V_after_feed
            X_after_feed = X_after_harvest * V_after_harvest / V_after_feed
            P_after_feed = P_after_harvest * V_after_harvest / V_after_feed

            y0 = [X_after_feed, S_after_feed, P_after_feed]
            V0 = V_after_feed

            # Add a point for the event
            t_total.append(current_time_offset)
            X_total.append(y0[0])
            S_total.append(y0[1])
            P_total.append(y0[2])
            V_total.append(V0)

            # Subsequent batch phase
            t_subsequent_cycle = np.linspace(0, subsequent_harvest_time, int(subsequent_harvest_time * 10))
            sol = odeint(batch_kinetics, y0, t_subsequent_cycle, args=(params['mu_max'], params['ks'], params['Y_xs'], params['Y_xp']))

            # Record results
            t_to_add = t_subsequent_cycle[1:] + current_time_offset
            t_total.extend(t_to_add)
            X_total.extend(sol[1:, 0])
            S_total.extend(sol[1:, 1])
            P_total.extend(sol[1:, 2])
            V_total.extend([V0] * len(t_subsequent_cycle[1:]))
            
            current_time_offset = t_total[-1]


        df = pd.DataFrame({"Time (h)": t_total, "Biomass (g/L)": X_total, "Substrate (g/L)": S_total, f"{product_name} (g/L)": P_total, "Volume (L)": V_total})


    elif mode == "Bleed-Perfusion":
        # Reset perfusion model state
        if hasattr(perfusion_kinetics, 'S_max'):
            delattr(perfusion_kinetics, 'S_max')
        perfusion_kinetics.crashed = False
            
        # Operating parameters
        V = params['initial_volume']  # L
        F = params['feed_rate']       # L/h
        B = params['bleed_rate']      # L/h
        D = F / V                     # Feed dilution rate (1/h)
        D_bleed = B / V              # Bleed dilution rate (1/h)
        Sf = params['feed_substrate'] # Feed substrate (g/L)
        R = params['cell_retention']  # Cell retention fraction
        
        # Initial state [X, S, P]
        y0 = [params['initial_biomass'], 
              params['initial_substrate'],
              0.0]  # Start with no product
        
        # Initialize crash detection
        perfusion_kinetics.S_max = max(Sf, params['initial_substrate'])
        
        # Solve ODEs
        sol = odeint(
            perfusion_kinetics,
            y0,
            t_span,
            args=(
                params['mu_max'],
                params['ks'],
                params['Y_xs'],
                params['Y_xp'],
                D,
                Sf,
                R,
                D_bleed
            ),
        )
        X, S, P = sol[:, 0], sol[:, 1], sol[:, 2]

        # Stop simulation when substrate is depleted
        stop_threshold = params.get('initial_substrate', 10.0) * 0.008
        stop_point = np.where(S < stop_threshold)

        if len(stop_point[0]) > 0:
            stop_index = stop_point[0][0]
            t_span = t_span[:stop_index]
            X = X[:stop_index]
            S = S[:stop_index]
            P = P[:stop_index]

        df = pd.DataFrame({"Time (h)": t_span, "Biomass (g/L)": X, "Substrate (g/L)": S, f"{product_name} (g/L)": P})
    
    return df

# --- Main Content Area ---
st.header(f"Simulation Results for {mode} Mode")

# --- Visualization Settings ---
with st.sidebar.expander("🎨 Visualization Settings", expanded=True):
    show_inflection_points = st.checkbox("Show Inflection Points")
    show_annotations = st.checkbox("Show Annotations")

# --- Overlay Scenarios ---
overlay_scenarios = st.sidebar.multiselect("Overlay Scenarios", scenario_names)

df_main = run_simulation(mode, current_params)

col1, col2 = st.columns(2)
with col1:
    with st.expander("📈 Visualization Panel", expanded=True):
        fig = go.Figure()
    
        # Plot main simulation
        for col in df_main.columns:
            if col != "Time (h)":
                fig.add_trace(go.Scatter(x=df_main["Time (h)"], y=df_main[col], mode='lines', name=f"Current - {col}"))

        # Plot overlay scenarios
        for scenario in overlay_scenarios:
            scenario_data = st.session_state.scenarios[scenario]
            df_overlay = run_simulation(scenario_data['mode'], scenario_data['params'])
            for col in df_overlay.columns:
                if col != "Time (h)":
                    fig.add_trace(go.Scatter(x=df_overlay["Time (h)"], y=df_overlay[col], mode='lines', name=f"{scenario} - {col}", line=dict(dash='dash')))

        if show_inflection_points and not df_main.empty:
            max_biomass_idx = df_main['Biomass (g/L)'].idxmax()
            max_biomass_time = df_main["Time (h)"][max_biomass_idx]
            max_biomass_val = df_main['Biomass (g/L)'][max_biomass_idx]
            fig.add_trace(go.Scatter(x=[max_biomass_time], y=[max_biomass_val], mode='markers', name='Max Biomass', marker=dict(size=10, color='red')))

        if show_annotations and not df_main.empty:
            fig.add_annotation(x=df_main["Time (h)"][int(len(df_main)/4)], y=df_main['Biomass (g/L)'][int(len(df_main)/4)],
                text="Lag Phase", showarrow=True, arrowhead=1)

        fig.update_layout(title="Biomass and Substrate vs. Time", xaxis_title="Time (h)", yaxis_title="Concentration (g/L)")
        st.plotly_chart(fig, use_container_width=True)

        # Culture Status Indicators (moved here for immediate visibility)
        if mode == "Bleed-Perfusion" and hasattr(perfusion_kinetics, 'S_max'):
            st.markdown("### 🔬 Culture Status")
            S_threshold = 0.000015 * perfusion_kinetics.S_max
            current_S = df_main['Substrate (g/L)'].iloc[-1]
        
            if current_S <= S_threshold:
                st.error("⚠️ CULTURE CRASH DETECTED!")
                st.error("""
                Severe substrate depletion has stopped all biological activity.
                The culture requires restart - no recovery is possible.
                """)
                st.info(f"""
                📊 Status Details:
                - Current substrate: {current_S:.4f} g/L
                - Crash threshold: {S_threshold:.4f} g/L
                - Peak substrate seen: {perfusion_kinetics.S_max:.1f} g/L
                - Condition: No cell growth, no product formation
                - Action: Culture washout in progress
                """)
            elif current_S < 5 * S_threshold:
                st.warning("⚠️ CRITICAL WARNING - Culture at Risk!")
                st.warning("""
                Substrate levels dangerously low - immediate action required.
                """)
                st.info(f"""
                📊 Status Details:
                - Current substrate: {current_S:.4f} g/L
                - Crash threshold: {S_threshold:.4f} g/L
                - Action Required: Increase feed rate or substrate concentration
                """)

with col2:
    with st.expander("📄 Data Table", expanded=True):
        st.dataframe(df_main)

with st.expander("📊 Process Performance", expanded=False):
    # Check for culture crash in perfusion mode
    if mode == "Bleed-Perfusion" and hasattr(perfusion_kinetics, 'S_max'):
        S_threshold = 0.000015 * perfusion_kinetics.S_max
        current_S = df_main['Substrate (g/L)'].iloc[-1]
    
        if current_S <= S_threshold:
            st.error("⚠️ CULTURE CRASH DETECTED - Severe substrate depletion has stopped all biological activity!")
            st.info(f"""
            - Current substrate: {current_S:.4f} g/L
            - Crash threshold: {S_threshold:.4f} g/L (0.0015% of peak {perfusion_kinetics.S_max:.1f} g/L)
            - Status: No cell growth, no product formation, washout in progress
            """)
        elif current_S < 5 * S_threshold:  # Warning zone
            st.warning("⚠️ WARNING - Substrate levels critically low, approaching crash threshold!")
            st.info(f"""
            - Current substrate: {current_S:.4f} g/L
            - Crash threshold: {S_threshold:.4f} g/L
            - Recommended: Check feed rate and substrate concentration
            """)

    # Show metrics
    st.subheader("Process Metrics")
    metrics = calculate_productivity_metrics(df_main, mode, current_params)

    col3, col4 = st.columns(2)
    with col3:
        for key, value in list(metrics.items())[:len(metrics)//2]:
            st.metric(key, f"{value:.4f}")
        
    with col4:
        for key, value in list(metrics.items())[len(metrics)//2:]:
            st.metric(key, f"{value:.4f}")

with st.expander("🔄 Mode Comparison", expanded=False):
    comparison_data = {
        "Mode": ["Batch", "Fed-Batch", "Repeated Fed-Batch", "Bleed-Perfusion"],
        "Fresh Medium Introduction": ["Single addition at start", "Gradual or pulsed feeding", "Periodic feeding after each cycle", "Continuous"],
        "Spent Medium Removal": ["None during process", "None during process", "Partial removal between cycles", "Continuous"],
        "Cell Harvesting": ["At end of run; entire culture", "At end of run; entire culture", "Partial harvest after each cycle", "Continuous bleed stream"],
        "Relative Productivity": ["🔹 Lowest", "🔸 Moderate to high", "🔸 Moderate to high", "🔹 Highest"]
    }
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

with st.expander("📝 Assignment Questions", expanded=False):
    if assignment_mode:
        questions = {
            "Batch": [
                "Why does the biomass concentration plateau in batch culture?",
                "What limits the final biomass concentration achieved?",
                "How would increasing the initial substrate concentration affect the results?"
            ],
            "Fed-Batch": [
                "How does the feeding strategy affect biomass productivity?",
                "What are the advantages of fed-batch over batch culture?",
                "How would you optimize the feed rate for maximum productivity?"
            ],
            "Repeated Fed-Batch": [
                "What are the benefits of multiple cycles compared to single batch?",
                "How does the harvest volume affect overall productivity?",
                "What factors determine the optimal cycle time?"
            ],
            "Bleed-Perfusion": [
                "Why can perfusion systems achieve the highest productivity?",
                "How does cell retention efficiency affect the process?",
                "What are the main challenges in operating perfusion systems?"
            ]
        }
    
        for i, question in enumerate(questions[mode]):
            st.write(f"**Question {i+1}:** {question}")
            st.text_area(f"Answer {i+1}:", key=f"answer_{i}")
    
        st.text_area("Overall interpretation of the results:", key="overall_interpretation")

# --- Glossary Expander ---
with st.expander("Glossary"):
    for term, definition in glossary.items():
        st.markdown(f"**{term}**: {definition}")

# --- Scenario Builder and Export Tool ---
with st.sidebar.expander("🛠️ Scenario Builder", expanded=False):
    scenario_name = st.text_input("Enter scenario name to save", "MyScenario")
    if st.button("Save Scenario"):
        st.session_state.scenarios[scenario_name] = {"mode": mode, "params": current_params}
        save_scenarios(st.session_state.scenarios)
        st.success(f"Scenario '{scenario_name}' saved to scenarios.json!")

with st.sidebar.expander("📥 Import / Export 📤", expanded=False):
    # --- Import Scenarios ---
    uploaded_file = st.file_uploader("Upload scenario file", type="json")
    if uploaded_file is not None:
        try:
            uploaded_scenarios = json.load(uploaded_file)
            st.session_state.scenarios.update(uploaded_scenarios)
            save_scenarios(st.session_state.scenarios)
            st.success(f"Imported {len(uploaded_scenarios)} scenarios!")
        except json.JSONDecodeError:
            st.error("Invalid JSON file format")

    # --- Export Tool ---
    file_name = st.text_input("Enter file name for export", "simulation_data.csv")
    if st.button("Export Data to CSV"):
        df_main.to_csv(file_name, index=False)
        st.success(f"Data exported to {file_name}!")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;'>
    📚 <strong>For Educational Use Only</strong> - This tool is designed exclusively for academic learning and training purposes.

    © 2025 Magnus Stefansson. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)
