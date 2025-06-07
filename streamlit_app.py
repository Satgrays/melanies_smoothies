# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f" :cup_with_straw: Costomize yout smoothie :cup_with_straw: ")
st.write(
  """Choose the fruit you want in your custom smoothie!
  """
)

import streamlit as st

name_on_order = st.text_input("Name on smoothie:", max_chars=100)
st.write("The name on yor smoothie will be: ", name_on_order)

cnx= st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect (
"Choose up to 5 ingredients"
, my_dataframe
, max_selections = 5
)
if ingredients_list:
  ingredients_string =''
  time_to_insert = st.button ("Order smoothie")
  
  for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ' '
    st.subheader(fruit_chosen + ' Nutrition Information')
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
    sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    #st.write(ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, NAME_ON_ORDER)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    st.write(my_insert_stmt)
    #st.stop()
    if time_to_insert:
      session.sql(my_insert_stmt).collect()
      st.success('Your Smoothie is ordered! ' + name_on_order, icon="✅")


