#Imports
import subprocess
import streamlit as st
# from get_store_object import StoreObject
# from api import fetch_offers
# from parser import parser
# from data_cleaner import clean_data
# from data_saver import save_data
# from recipe_matcher import match_recipe

# #######################
# # Install your GitHub package
subprocess.run(["pip", "install", "git+https://github.com/FilipHolmbrg/veckans_erbjudanden.git"])
# from veckans_mat.check_password import check_connection
# # Now you can import and use your module
from veckans_mat.recipe_matcher import match_recipe

try:
    from veckans_mat.check_password import check_connection
    st.write("Module imported successfully!")
except ModuleNotFoundError as e:
    st.error(f"Error importing the module: {e}")


data = {'name': ['ägg', 'pasta']}

obj = match_recipe(data)
print(obj)
st.write(obj)
# ##############################

# st.write(check_connection('u41c_Y'))

# #Imports
# # import logging
# import streamlit as st
# # from get_store_object import StoreObject
# # from api import fetch_offers
# # from parser import parser
# # from data_cleaner import clean_data
# # from data_saver import save_data
# # from recipe_matcher import match_recipe

# ### Building App ###

# # Define your dictionaries
# user_one = {'name': 'Alice', 'age': 25}
# user_two = {'name': 'Bob', 'age': 30}
# store_one = {'location': 'New York', 'inventory': 100}
# store_two = {'location': 'Los Angeles', 'inventory': 150}

# # Define the secret password
# secret_password = "mysecretpassword"

# # Streamlit Application
# st.title('User and Store Dictionary Viewer')

# # Password input
# password_input = st.text_input("Enter the secret password:", type="password")

# # Check if the password matches
# if password_input == secret_password:
    
#     st.subheader("Choose User and Store")
    
#     # Use checkboxes to allow multiple selections
#     show_user_one = st.checkbox('Show User One')
#     show_user_two = st.checkbox('Show User Two')
#     show_store_one = st.checkbox('Show Store One')
#     show_store_two = st.checkbox('Show Store Two')

#     # Display the chosen user dictionary
#     if show_user_one:
#         st.write("User One Data:", user_one)
#     if show_user_two:
#         st.write("User Two Data:", user_two)
    
#     # Display the chosen store dictionary
#     if show_store_one:
#         st.write("Store One Data:", store_one)
#     if show_store_two:
#         st.write("Store Two Data:", store_two)

# else:
#     st.warning("Please enter the correct password to view the data.")
