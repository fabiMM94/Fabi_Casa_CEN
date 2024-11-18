# %%

import os
import pandas as pd

# Get the current directory
current_directory = os.getcwd()

# Modify the directory path to replace the last part with "Operation Point"
operation_point_dir = os.path.join(
    os.path.dirname(current_directory), "Operation Point"
)

# Check if the modified directory exists; if not, create it
if not os.path.exists(operation_point_dir):
    os.makedirs(operation_point_dir)
    print("Directory created:", operation_point_dir)
else:
    print("Directory already exists:", operation_point_dir)

# List all files in the current directory
files = os.listdir(current_directory)

# Filter files that start with 'data_PV' and end with '.csv'
data_pv_files = [
    file for file in files if file.startswith("data_PV") and file.endswith(".csv")
]

# Name of .ecf file
name_ecf_file = [file[len("data_PV") : -len(".csv")] for file in data_pv_files][0]

# Filter files that start with 'uc_pv' and end with '.csv'
uc_pv_files = [
    file for file in files if file.startswith("uc_pv") and file.endswith(".csv")
]

if data_pv_files:
    data_pv_file = data_pv_files[0]
    # Specify encoding when reading the CSV file
    df_data_pv = pd.read_csv(
        os.path.join(current_directory, data_pv_file), encoding="latin1"
    )
else:
    print("No CSV file starting with 'data_PV' was found in the current directory.")

if uc_pv_files:
    uc_pv_file = uc_pv_files[0]
    # Specify encoding when reading the CSV file
    df_uc_pv = pd.read_csv(
        os.path.join(current_directory, uc_pv_file), encoding="latin1"
    )
else:
    print("No CSV file starting with 'uc_pv' was found in the current directory.")

# Perform the merge using 'Name2' as the primary condition
merged_pv_df = pd.merge(
    df_data_pv, df_uc_pv, how="left", left_on="Name_PV", right_on="Name2"
)

# For rows where no match is found in 'Name2', try merging with 'Name1'
merged_pv_df = merged_pv_df.combine_first(
    pd.merge(df_data_pv, df_uc_pv, how="left", left_on="Name_PV", right_on="Name1")
)

# Define the required columns and rename them according to the specified header
required_pv_columns = [
    "Name_PV",
    "Name1",
    "Name2",
    "LibType",
    "Status1",
    "Status2",
    "StatusFinal",
    "N_PV_arrays",
    "N_PV_inServ",
    "S_spv",
    "Unit",
    "P_ctrlMode",
    "Active_ref",
    "Unit.1",
    "Q_ctrlMode",
    "Reactive_ref",
    "Unit.2",
    "s_nom",
    "p_mw",
    "q_mw",
    "p_pu",
    "q_pu",
]

# Filter and order columns to get the final DataFrame
final_pv_df = merged_pv_df[required_pv_columns]
operation_point_pv_df = final_pv_df[["Name_PV", "Active_ref", "Reactive_ref"]].copy()
name_output_data_pv = "op_PV.csv"
output_data_pv_path = os.path.join(operation_point_dir, name_output_data_pv)
operation_point_pv_df.to_csv(output_data_pv_path, index=False)

# %% ################################ WIND FARMS #####################################
# Filter files that start with 'data_WP' and end with '.csv'
data_wp_files = [
    file for file in files if file.startswith("data_WP") and file.endswith(".csv")
]

# Filter files that start with 'uc_wp' and end with '.csv'
uc_wp_files = [
    file for file in files if file.startswith("uc_wp") and file.endswith(".csv")
]

if data_wp_files:
    data_wp_file = data_wp_files[0]
    # Specify encoding when reading the CSV file
    df_data_wp = pd.read_csv(
        os.path.join(current_directory, data_wp_file), encoding="latin1"
    )
else:
    print("No CSV file starting with 'data_WP' was found in the current directory.")

if uc_wp_files:
    uc_wp_file = uc_wp_files[0]
    # Specify encoding when reading the CSV file
    df_uc_wp = pd.read_csv(
        os.path.join(current_directory, uc_wp_file), encoding="latin1"
    )
else:
    print("No CSV file starting with 'uc_wp' was found in the current directory.")

# Perform the merge using 'Name2' as the primary condition
merged_wp_df = pd.merge(
    df_data_wp, df_uc_wp, how="left", left_on="Name_WP", right_on="Name2"
)

# For rows where no match is found in 'Name2', try merging with 'Name1'
merged_wp_df = merged_wp_df.combine_first(
    pd.merge(df_data_wp, df_uc_wp, how="left", left_on="Name_WP", right_on="Name1")
)

# Define the required columns and rename them according to the specified header for WP
required_wp_columns = [
    "Name_WP",
    "Name1",
    "Name2",
    "LibType",
    "Status1",
    "Status2",
    "StatusFinal",
    "N_wind_turbines",
    "N_WT_inServ",
    "Snom_WP",
    "Unit",
    "Active_ref",
    "Unit",
    "Turbine Power",
    "Unit",
    "Q_ctrlMode",
    "Reactive_ref",
    "Unit",
    "s_nom",
    "p_mw",
    "q_mw",
    "p_pu",
    "q_pu",
]

# Filter and order columns to get the final DataFrame for WP
final_wp_df = merged_wp_df[required_wp_columns]
operation_point_wp_df = final_wp_df[["Name_WP", "Active_ref", "Reactive_ref"]].copy()
name_output_data_wp = "op_WP.csv"
output_data_wp_path = os.path.join(operation_point_dir, name_output_data_wp)
operation_point_wp_df.to_csv(output_data_wp_path, index=False)

# %% ################################ LOADS LF #####################################

# Filter files that start with 'data_loadLF' and end with '.csv'
data_load_files = [
    file for file in files if file.startswith("data_loadLF") and file.endswith(".csv")
]

if data_load_files:
    data_load_file = data_load_files[0]
    # Specify encoding when reading the CSV file
    df_data_load = pd.read_csv(
        os.path.join(current_directory, data_load_file), encoding="latin1"
    )
else:
    print("No CSV file starting with 'data_loadLF' was found in the current directory.")

operation_point_loadlf_df = df_data_load[["Name_LoadLF", "P_loadLF", "Q_loadLF"]].copy()
name_output_data_loadlf = "op_loadLF.csv"
output_data_loadlf_path = os.path.join(operation_point_dir, name_output_data_loadlf)
operation_point_loadlf_df.to_csv(output_data_loadlf_path, index=False)
# %% ################### FINAL EXPORTATION ################################
# Define the output path for the final WP DataFrame export
name_output_data_gen_load = "data_gen_load" + name_ecf_file + ".xlsx"
output_data_gen_load_path = os.path.join(current_directory, name_output_data_gen_load)

with pd.ExcelWriter(output_data_gen_load_path) as writer:
    # Write each DataFrame to a specific sheet
    final_pv_df.to_excel(writer, sheet_name="PFV", index=False)
    final_wp_df.to_excel(writer, sheet_name="PE", index=False)
    df_data_load.to_excel(writer, sheet_name="Cargas", index=False)

print("DataFrames exported successfully to 'output.xlsx'")

# %%
