# User Instructions - Bioprocessing Educational Simulator

## 🚀 Getting Started

### Running the Application
1. **Install Dependencies:**
   ```bash
   pip install streamlit numpy pandas plotly scipy
   ```

2. **Launch the App:**
   ```bash
   streamlit run Bioprocessing_app.py
   ```

3. **Access the Interface:**
   - The app will open in your default web browser
   - Use the sidebar controls to adjust parameters
   - View results in the main panel

## 📊 Application Features

### Bioprocessing Modes
The app simulates four different bioreactor operation modes:

- **Batch**: All nutrients added at start; simplest operation, lowest productivity
- **Fed-Batch**: Incremental nutrient feeding; moderate to high productivity
- **Repeated Fed-Batch**: Multiple cycles with partial harvest; improved productivity
- **Bleed-Perfusion**: Continuous operation; highest stable productivity

### Product Simulation
**NEW FEATURE**: The app now includes product formation modeling:

- **Product Types**: Simulate production of proteins, fatty acids, ethanol, or custom products
- **Product Yield (Y_xp)**: Adjustable ratio of product produced per unit biomass
- **Product Tracking**: Real-time visualization of product concentration
- **Product Metrics**: Dedicated productivity calculations for your target product

## ⚙️ Parameter Controls

**NEW**: Dual input system - use sliders for quick adjustment or direct numerical input for precise values.

### Core Parameters (All Modes)
- **Initial Substrate (g/L)**: Starting nutrient concentration
- **Initial Biomass (g/L)**: Starting cell concentration
- **Max Growth Rate (μ_max)**: Maximum cellular division rate
- **Monod Constant (Ks)**: Substrate affinity parameter
- **Yield Coefficient (Y_xs)**: Biomass produced per substrate consumed

### Product Parameters (NEW)
- **Product Yield (Y_xp)**: Product produced per biomass formed (0.01-1.0 g/g)
- **Product Name**: Customizable product identifier (e.g., "Monoclonal Antibody", "Ethanol")

### Mode-Specific Parameters
**Fed-Batch & Repeated Fed-Batch:**
- Initial Volume, Feed Rate, Feed Substrate Concentration
- Harvest Volume, Cycle Time, Number of Cycles (Repeated Fed-Batch only)

**Bleed-Perfusion:**
- Feed Rate (L/h): Continuous medium input (0.0-1.0)
- Bleed Rate (L/h): Continuous culture removal (0.0-1.0) 
- Cell Retention: Fraction of cells retained (0.0-1.0)
- **Culture Crash Detection**: Real-time monitoring with automatic alerts

## 📋 Pre-Configured Scenarios

### Available Scenarios
1. **High-Density Perfusion** - Monoclonal Antibody production
2. **Substrate-Limited Fed-Batch** - Recombinant Protein production
3. **Classical Batch Culture** - Ethanol fermentation
4. **Multi-Cycle Production** - Fatty Acids biosynthesis

### Using Scenarios
1. Select a scenario from the "Scenario Loader" dropdown
2. Parameters auto-populate with realistic values
3. Modify parameters as needed for your analysis
4. Compare different scenarios using the overlay feature

## 📈 Interpreting Results

### Visualization Panel
- **Real-time Plots**: Biomass, substrate, and product concentrations over time
- **Multi-scenario Overlay**: Compare different scenarios with dashed lines
- **Culture Status Indicators**: Live perfusion crash detection with warnings
- **Inflection Points**: Mark maximum biomass points (red markers)
- **Interactive Controls**: Toggle annotations and inflection points

### Performance Metrics (UPDATED)
**Biomass Metrics:**
- Biomass Productivity (g/L/h)
- Total Biomass Produced
- Substrate to Biomass Efficiency

**Product Metrics (NEW):**
- **Product Productivity (g/L/h)**: Rate of product formation per unit volume per hour. Higher values indicate more efficient production processes. Critical for economic viability.
- **Total Product Produced**: Cumulative amount of product generated during the entire process. In batch/fed-batch: final concentration × volume. In perfusion: continuous output over time.
- **Substrate to Product Efficiency**: Ratio of product formed to substrate consumed. Measures how effectively nutrients are converted to your target product rather than just biomass.

**Process Metrics:**
- Maximum Growth Rate Achieved
- Substrate Conversion Efficiency

### Data Export
- Export simulation data as CSV files
- Include all time-series data for further analysis
- Customizable file naming

## 🎓 Educational Features

### Assignment Mode
- Locks parameter controls for guided learning
- Provides structured questions for each mode
- Encourages critical thinking about process optimization

### Sample Questions by Mode
**Batch Culture:**
- Why does biomass plateau in batch culture?
- How does product formation relate to growth phase?
- What limits final product concentration?

**Fed-Batch:**
- How does feeding strategy affect product yield?
- What are the advantages for product formation?
- How to optimize feed rate for maximum product productivity?

**Repeated Fed-Batch:**
- How do multiple cycles improve product recovery?
- What's the optimal harvest strategy for your product?
- How does product loss during harvest affect economics?

**Bleed-Perfusion:**
- Why can perfusion achieve highest product productivity?
- How does product retention affect process design?
- What are the challenges for product recovery?

## 🔧 Advanced Features

### Scenario Builder
1. Adjust parameters to your desired conditions
2. Enter a custom scenario name
3. Click "Save Scenario" to store for future use
4. Saved scenarios persist across sessions

### Overlay Comparisons
- Select multiple scenarios from the overlay dropdown
- Visualize different conditions simultaneously
- Compare productivity metrics side-by-side
- Identify optimal operating conditions

### Process Optimization Tips
1. **Product Yield Optimization:**
   - Higher Y_xp values increase product per biomass
   - Balance with realistic biological constraints
   - Consider product toxicity effects on growth

2. **Mode Selection:**
   - Batch: Simple products, low capital cost
   - Fed-Batch: Growth-associated products
   - Repeated Fed-Batch: Improved product recovery
   - Perfusion: Continuous high-value products

3. **Parameter Tuning:**
   - Start with pre-configured scenarios
   - Adjust one parameter at a time
   - Monitor both biomass and product metrics
   - Consider economic trade-offs

## 📚 Glossary Integration

Access the built-in glossary by:
- Hovering over parameter help icons (?)
- Expanding the "Glossary" section at the bottom
- Understanding technical terms and their biological significance

## 🔍 Troubleshooting

### Common Issues
- **No product formation**: Check Y_xp value > 0
- **Unrealistic results**: Verify parameter ranges are biologically feasible
- **Slow performance**: Reduce simulation time span or number of cycles
- **Export issues**: Ensure write permissions in the target directory

### Performance Tips
- Use realistic parameter values based on your organism/product
- Start with pre-configured scenarios as templates
- Monitor both productivity and yield metrics
- Consider practical constraints (equipment, economics, regulations)

## 📞 Support & Attribution

**Created by**: Magnus Stefansson, MBA, Ph.D.  
**Institution**: Rabb School of Continuing Studies, Division of Graduate Professional Studies, Brandeis University  
**Address**: 475 Old S St, Waltham, MA 02453

For technical issues or educational questions:
- Review built-in glossary and parameter help tooltips
- Start with pre-configured scenarios for realistic parameter ranges
- Use assignment mode for structured learning exercises

---

**📚 For Educational Use Only** - This tool is designed exclusively for academic learning and training purposes.

© 2024 Magnus Stefansson. All rights reserved.

**Note**: This simulation tool is designed for educational purposes. Always validate results with experimental data and consult relevant literature for industrial applications.