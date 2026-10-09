import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Tafel Corrosion Rate Calculator", layout="wide")

st.title("🧪 Tafel Plot Corrosion Rate Calculator")
st.write("Upload linear polarization resistance (LPR) or Tafel data to compute $i_{corr}$ and corrosion rates.")

# --- Sidebar Inputs ---
st.sidebar.header("Material Parameters")
density = st.sidebar.number_input("Density (g/cm³)", value=7.87, step=0.01)
atomic_wt = st.sidebar.number_input("Atomic Weight (g/mol)", value=55.85, step=0.01)
valence = st.sidebar.number_input("Valence (n)", value=2, step=1)
area = st.sidebar.number_input("Exposed Area (cm²)", value=1.0, step=0.1)

equivalent_weight = atomic_wt / valence
st.sidebar.write(f"**Equivalent Weight:** {equivalent_weight:.2f} g/eq")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload CSV Data (Potential in V, Current Density or Current)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head())

    cols = df.columns.tolist()
    col1, col2 = st.columns(2)
    potential_col = col1.selectbox("Select Potential Column (V)", cols, index=0)
    current_col = col2.selectbox("Select Current/Current Density Column", cols, index=1)

    df['Log_Current'] = np.log10(np.abs(df[current_col] / area))

    min_idx = df[current_col].abs().idxmin()
    e_corr_est = df.loc[min_idx, potential_col]

    st.info(f"Estimated Corrosion Potential ($E_{{corr}}$): **{e_corr_est:.3f} V**")

    st.subheader("Tafel Parameters Calibration")
    c1, c2, c3 = st.columns(3)
    icorr_val = c1.number_input("Corrosion Current Density $i_{corr}$ (A/cm²)",
                                value=float(df.loc[min_idx, current_col] / area), format="%.2e")
    ba = c2.number_input("Anodic Slope $\\beta_a$ (V/decade)", value=0.12, step=0.01)
    bc = c3.number_input("Cathodic Slope $\\beta_c$ (V/decade)", value=0.12, step=0.01)

    corrosion_rate_mpy = (3272 * icorr_val * equivalent_weight) / density

    st.markdown("---")
    st.subheader("📊 Calculation Results")
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Corrosion Current Density ($i_{corr}$)", f"{icorr_val:.3e} A/cm²")
    res_col2.metric("Corrosion Rate", f"{corrosion_rate_mpy:.4f} mm/year")

    st.subheader("Tafel Plot")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df['Log_Current'], df[potential_col], 'b.', label="Experimental Data")
    ax.axhline(e_corr_est, color='r', linestyle='--', label=f'E_corr ({e_corr_est:.3f} V)')

    ax.set_xlabel("$\log_{10}$ Current Density ($\log(A/cm^2)$)")
    ax.set_ylabel("Potential (V)")
    ax.set_title("Polarization Curve (Tafel Extrapolation)")
    ax.grid(True, which="both", ls="--")
    ax.legend()

    st.pyplot(fig)
else:
    st.info("Please upload a CSV file with your polarization data to begin.")