import streamlit as st

st.title("¡Hola, Streamlit!")
st.write("Esta es mi primera aplicación web con Streamlit.")


if st.button("Presiona para cambiar el estado"):
    st.write("¡Me hiciste clic! 😃")
else:
    st.write("Aún no has presionado el botón. 😴")