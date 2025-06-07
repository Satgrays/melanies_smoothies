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
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

    # Multi-select for choosing ingredients
    ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

    # Process ingredients selection

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        try:
            ingredients_string += fruit_chosen + ' '

            # Asumiendo que pd_df ya fue definido anteriormente como un DataFrame con FRUIT_NAME y SEARCH_ON
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

            # Mostrar encabezado
            st.subheader(f"{fruit_chosen} Nutrition Information")

            # Hacer la petición a la API
            fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            fruityvice_response.raise_for_status()  # Agrega esto para lanzar error si es 404, 500, etc.

            # Mostrar JSON en la app
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch details for {fruit_chosen}: {str(e)}")
        except Exception as e:
            st.error(f"Error general con {fruit_chosen}: {str(e)}")

        # Button to submit order
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            try:
                # Execute SQL insert statement
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
            except Exception as e:
                st.error(f"Failed to submit order: {str(e)}")

except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")


