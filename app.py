import streamlit as st
import pandas as pd
from pbixray.core import PBIXRay
from st_aggrid import AgGrid, GridOptionsBuilder

# MUST be first Streamlit command
st.set_page_config(page_title="PBIX Assistant", layout="wide")

# Hide Streamlit default UI elements
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def aggrid_table(df, fit_columns=True):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(groupable=True, enableRowGroup=True, aggFunc="sum", editable=False)
    gb.configure_side_bar()
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, fit_columns_on_grid_load=fit_columns)

def app():
    st.title("Explore PBIX files without Power BI App or a license!")

    uploaded_file = st.file_uploader("📁 Upload a PBIX file", type="pbix")
    
    if uploaded_file:
        model = PBIXRay(uploaded_file)

        with st.container():
            st.subheader("PBIX Metadata Overview")
            met1, met2 = st.columns(2)
            met1.metric(label='Model Size', value=sizeof_fmt(model.size))
            met2.metric(label='Number of Tables', value=model.tables.size)

        st.subheader("Table Analysis")
        aggrid_table(model.statistics)

        if model.relationships.size:
            st.subheader("Relationships Analysis")
            aggrid_table(model.relationships)

        if model.power_query.size:
            st.subheader("PowerQuery Analysis")
            aggrid_table(model.power_query)

        st.subheader("Columns Analysis")
        schema_df = model.schema.copy()
        calculated_df = model.dax_columns.copy()

        for col in schema_df.columns:
            if col not in calculated_df.columns:
                calculated_df[col] = None
        for col in calculated_df.columns:
            if col not in schema_df.columns:
                schema_df[col] = None

        merged_table = pd.concat([schema_df, calculated_df], ignore_index=True)
        aggrid_table(merged_table)

        if model.dax_measures.size:
            st.subheader("DAX Measures")
            aggrid_table(model.dax_measures)

        st.subheader("Table Viewer")

        valid_tables = []
        for table in model.tables:
            try:
                _ = model.get_table(table)
                valid_tables.append(table)
            except:
                continue

        if not valid_tables:
            st.warning("⚠️ No tables could be previewed from this PBIX file.")
        else:
            table_name_input = st.selectbox("Choose a table to preview its content", valid_tables)
            if st.button("📤 Get the data"):
                try:
                    table_df = model.get_table(table_name_input)
                    st.write(f"Preview of table: `{table_name_input}`")
                    aggrid_table(table_df)
                except ValueError as e:
                    st.error(f"⚠️ Could not retrieve the table due to error:\n\n{e}")
                except Exception as e:
                    st.error(f"❌ Unexpected error while loading table:\n\n{e}")
    else:
        st.info("Upload a PBIX file to get started.")

#     # Custom footer
# custom_footer = """
#     <div style="position: fixed; bottom: 10px; width: 100%; text-align: center; font-size: 14px;">
#         Made with ❤️ by 
#         <a href="https://sahilchoudhary.com/" target="_blank" style="color: #1f77b4; text-decoration: underline;">
#             Sahil
#         </a>
#     </div>
# """
# st.markdown(custom_footer, unsafe_allow_html=True)


if __name__ == '__main__':
    app()
