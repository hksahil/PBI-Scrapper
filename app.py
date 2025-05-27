import streamlit as st
import pandas as pd
from pbixray.core import PBIXRay

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def app():
    st.title("PBIX info")

    uploaded_file = st.file_uploader("Choose a PBIX file", type="pbix")
    if uploaded_file:
        # Load PBIX metadata
        model = PBIXRay(uploaded_file)

        st.write(model.metadata)
        
        met1, met2 = st.columns(2)
        met1.metric(label='Model size', value=sizeof_fmt(model.size))
        met2.metric(label='# Tables', value=model.tables.size)

        # # Show Schema
        # st.write("Schema")
        # st.dataframe(model.schema)

        # # Show Calculated Columns
        # st.write("Calculated columns")
        # st.dataframe(model.dax_columns)

        # Merge Schema and Calculated Columns
        schema_df = model.schema.copy()
        calculated_df = model.dax_columns.copy()

        # Add missing columns to align structure
        for col in schema_df.columns:
            if col not in calculated_df.columns:
                calculated_df[col] = None
        for col in calculated_df.columns:
            if col not in schema_df.columns:
                schema_df[col] = None

        merged_table = pd.concat([schema_df, calculated_df], ignore_index=True)
        st.write("Columns")
        st.dataframe(merged_table)

        # Other metadata
        st.write("Tables")
        st.dataframe(model.statistics)

        if model.relationships.size:
            st.write("Relationships")
            st.write(model.relationships)

        if model.power_query.size:
            st.write("PowerQuery")
            st.dataframe(model.power_query)

        if model.dax_measures.size:
            st.write("Measures:")
            st.dataframe(model.dax_measures)

        # Table viewer
        table_name_input = st.selectbox("Select a table to peek at its contents:", model.tables)
        if st.button("Un-VertiPaq"):
            st.dataframe(model.get_table(table_name_input), use_container_width=True)

if __name__ == '__main__':
    app()
