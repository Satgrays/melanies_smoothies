# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# User input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

try:
    # Establish connection to Snowflake (assuming st.connection is correctly defined)
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Retrieve fruit options from Snowflake
    # Retrieve fruit options from Snowflake
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
    fruit_options = [row["FRUIT_NAME"] for row in fruit_df.collect()]  # Convertir a lista

    # Multi-select para elegir ingredientes
    ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_options, max_selections=5)

    # Si se eligieron ingredientes
    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)

        # Mostrar info nutricional desde Fruityvice
        st.subheader("🍓 Fruit Nutrition Info")
        for fruit_chosen in ingredients_list:
            fruit_api_name = fruit_chosen.lower().replace(" ", "")  # Normalizar nombre
            try:
                response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_api_name}")
                response.raise_for_status()
                data = response.json()
                st.json(data)  # También podrías formatear mejor si quieres
            except requests.exceptions.HTTPError:
                st.warning(f"❌ Fruityvice no tiene info para '{fruit_chosen}'")
            except requests.exceptions.RequestException as e:
                st.error(f"Error al buscar {fruit_chosen}: {str(e)}")

        # Botón para insertar orden
        if st.button('Submit Order'):
            try:
                # Crear DataFrame con los datos del pedido y guardar en tabla
                new_order_df = session.create_dataframe(
                    [[ingredients_string, name_on_order]],
                    schema=["INGREDIENTS", "NAME_ON_ORDER"]
                )
                new_order_df.write.mode("append").save_as_table("smoothies.public.orders")
                st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
            except Exception as e:
                st.error(f"Failed to submit order: {str(e)}")


except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")

