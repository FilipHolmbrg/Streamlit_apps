#Imports
import subprocess
import streamlit as st
import requests
# from get_store_object import StoreObject
# from api import fetch_offers
# from parser import parser
# from data_cleaner import clean_data
# from data_saver import save_data
# from recipe_matcher import match_recipe

# #######################
# # Install your GitHub package
subprocess.run(["pip", "install", "git+https://github.com/FilipHolmbrg/veckans_erbjudanden.git"])
# # Now you can import and use your module
from veckans_mat.get_store_id import fetch_id
from veckans_mat.recipe_matcher import match_recipe
from veckans_mat.check_password import check_connection
from veckans_mat.user_dictionary import get_dictionary
from veckans_mat.api import fetch_offers
from veckans_mat.parser import parser
from veckans_mat.data_cleaner import clean_data
# ##############################

st.write(check_connection('u41c_Y'))

# Define functions:
def get_offers(password: str, store_no: int, user_dict: dict) -> dict:
    store_id = fetch_id('Willys Landvetter', password, store_no)
    raw_description_list, raw_offer_dict = fetch_offers(password, store_id, store_no)
    parsed_dict = parser(raw_description_list, raw_offer_dict)
    cleaned_dict = clean_data(parsed_dict)
    
    veckans_recept_förslag = match_recipe(cleaned_dict, user_dict)
    
    return veckans_recept_förslag

### Building App ###
# Streamlit Application
st.title('User and Store Dictionary Viewer')

# Password input
# password_input = st.text_input("Enter the secret password:", type="password")
password_bool = check_connection('u41c_Y')

# Check if the password matches
if password_bool == True:
    
    # Define your dictionaries
    user_one = get_dictionary(1)
    user_two = get_dictionary(2)
    store_one_offers = get_offers('u41c_Y', 1, user_one)
    store_two = {'Coming': 'to', 'app': 'soon!'}
    
    st.subheader("Choose User and Store")
    
    # Use checkboxes to allow multiple selections
    show_user_one = st.checkbox('Show User One')
    show_user_two = st.checkbox('Show User Two')
    show_store_one = st.checkbox('Show Store One')
    show_store_two = st.checkbox('Show Store Two')

    # Display the chosen user dictionary
    if show_user_one:
        st.write("User One Data:", user_one)
    if show_user_two:
        st.write("User Two Data:", user_two)
    
    # Display the chosen store dictionary
    if show_store_one:
        st.write("Store One Data:", store_one_offers)
    if show_store_two:
        st.write("Store Two Data:", store_two)

else:
    st.warning("Please enter the correct password to view the data.")
