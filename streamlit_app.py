# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Título de la app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input del usuario
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

try:
    # Conexión a Snowflake
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Recuperar opciones de fruta
    fruit_snowpark_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
    pd_df = fruit_snowpark_df.to_pandas()

    # Lista de frutas para el multiselect
    fruit_names = pd_df["FRUIT_NAME"].tolist()
    ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_names, max_selections=5)

    if ingredients_list:
        ingredients_string = ""

        for fruit_chosen in ingredients_list:
            try:
                ingredients_string += fruit_chosen + " "

                # Obtener el campo SEARCH_ON desde el DataFrame
                search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

                # Mostrar nutrición de cada fruta
                st.subheader(f"{fruit_chosen} Nutrition Information")
                fruityvice_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                fruityvice_response.raise_for_status()

                st.dataframe(data=fruityvice_response.json(), use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Failed to fetch details for {fruit_chosen}: {str(e)}")
            except IndexError:
                st.warning(f"⚠️ No SEARCH_ON value found for {fruit_chosen}")
            except Exception as e:
                st.error(f"🔥 Error general con {fruit_chosen}: {str(e)}")

        # Limpieza de string final
        ingredients_string = ingredients_string.strip()

        # Insertar orden a DB
        if st.button("Submit Order"):
            try:
                my_insert_stmt = f"""
                    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                    VALUES ('{ingredients_string}', '{name_on_order}')
                """
                session.sql(my_insert_stmt).collect()
                st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
            except Exception as e:
                st.error(f"❌ Failed to submit order: {str(e)}")

except Exception as ex:
    st.error(f"💥 An error occurred: {str(ex)}")


