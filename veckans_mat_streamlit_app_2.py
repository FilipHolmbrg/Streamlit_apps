#Imports
import subprocess
import streamlit as st
import requests
import re
from time import sleep
import pandas as pd

# Define functions:
def fetch_id(store_name: str, password: str, store_no: int) -> str:
    
        headers = {
                    'Content-Type': 'application/json',  # Non required argument
                    'X-Api-Key': password  # Using X-Api-Key header as required
                    }
        if store_no == 1:
            url = "https://ereklamblad.se/api/squid/v2/dealerfront?r_lat=57.694554&r_lng=12.206504&r_radius=2500&limit=12&order_by=name&types=paged%2Cincito"

        """Fetch id for store which updates every week"""
        # Make a request to the API
        response = requests.get(url, headers=headers)
        # Ensure the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Loop through the data and extract the desired fields
            for item in data:
                catalogs = item.get("catalogs", [])
                for catalog in catalogs:
                    # print(catalog)
                    if catalog['label'] == store_name:
                        catalog_id = catalog.get("id")
                        return catalog_id
                    
        else:
            raise Exception("Store id not found due to unsuccessful response")
        
def match_recipe(data: dict, user_dict: dict) -> dict:
    veckans_recept_förslag = {recipe: [] for recipe in user_dict.keys()}

    for key, values in user_dict.items():
        # print(key, values)
        current_recipe_list = [] 
        for value in values:
            for item in data['name']:
                if value.upper() in item:
                    pattern = fr'\b{item}\b' #avoid that 'ägg' is mixed up with 'fläsklägg', 'påskägg', 'pålägg'
                    # print(key, value, item)
                    # print(item, pattern)
                    match = re.search(pattern, value)
                    # veckans_recept_förslag.update({key: item})
                    if not value in current_recipe_list:
                        current_recipe_list.append(value)
        
        veckans_recept_förslag.update({key: current_recipe_list})
    
    return veckans_recept_förslag

def check_connection(password: str) -> bool:
    #random url that worked at the current time
    url = "https://ereklamblad.se/api/squid/v2/dealerfront?r_lat=57.694554&r_lng=12.206504&r_radius=2500&limit=12&order_by=name&types=paged%2Cincito"
    headers = {
                'Content-Type': 'application/json',  # Non required argument
                'X-Api-Key': password  # Using X-Api-Key header as required
                }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        my_response = True
    else:
        my_response = False
    response.close()
    
    return my_response

def get_dictionary(user: int) -> dict:
    if user == 1:
        user_dict = {
                    'carbonara': ['pasta', 'bacon', 'ägg', 'grädde', 'parmesan'],
                    'högrev med potatis': ['högrev', 'potatis'],
                    'korvstroganoff': ['falukorv', 'ris', 'gröna ärtor', 'tomatpuré', 'passerade tomater', 'grädde'],
                    }
        
    else:
        user_dict = None
        
    return user_dict

def fetch_offers(password: str, store_id: str, store_no: int) -> tuple:
    """Function to get weely offers based of object attributes"""
    # General url
    if store_no == 1:
        url = "https://ereklamblad.se/api/squid/v4/rpc/get_offers"  
    # Create dict used for population of data and creation of datafram
    offer_dict = {
            'validity': [],
            'name': [],
            'price': [],
            'unit': [],
            'save': [],
            'brand': [],
            }
    # Description of items to parse later
    description_list = []
    page_size = 24
    # Prepare request body
    data = {
            "where": {
                "publication_ids": [store_id]  # The publication ID you want to filter by
                    },
            "page": {
                "page_size": page_size  # Max number of items per page
                    }
            }
    
    headers = {
                        'Content-Type': 'application/json',  # Non required argument
                        'X-Api-Key': password  # Using X-Api-Key header as required
                        }
    
    for i in range(3): # Each iteration gives different results, so we need to pickup data many times to be sure to get all.
        sleep(.1)
        after_cursor = None  # Start without any cursor (first page)
        has_next_page = True
        
        while has_next_page:
            sleep(.1) # Pause between pages.
            # Add after_cursor if it's available (for next pages)
            
            if after_cursor:
                data["page"]["after_cursor"] = after_cursor
            else:
                data["page"].pop("after_cursor", None)  # Remove after_cursor if starting from the first page

            response = requests.post(url, json=data, headers=headers)
            
            # Check the response status code
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract and print offers
                offers = response_data.get("offers", [])

                for offer in offers:
                    offer_dict['validity'].append(offer['validity']['to'])
                    offer_dict['name'].append(offer['name']) 
                    offer_dict['price'].append(offer['price'])
                    description_list.append(offer['description'])

                # Handle pagination
                page_info = response_data.get("page_info", {})
                after_cursor = page_info.get("last_cursor", None)  # Get the cursor for the next page
                has_next_page = page_info.get("has_next_page", False)  # Check if there is another page
                
            else:
                break
            
    return (description_list, offer_dict)

def parser(description_list: list, offer_dict: dict) -> dict:
    """Function to parse list and populates empty entries in dict"""
    # key:pattern dict is needed to extract data from description list. 
    parse_dict = {
                'unit': r"Per förp|Per kg|Per st",
                'save': r"SPARA \d{1,2}:\d{2}",
                'brand': r"\b([A-ZÅÄÖÉa-zåäöé\-]{2,})\b •" 
                }

    for string in description_list:
        # dict with parse strings
        for key, pattern in parse_dict.items():
            try:
                dict_string = re.search(pattern, string).group()
            except AttributeError:
                offer_dict[key].append(None)
            else:
                offer_dict[key].append(dict_string)
    return offer_dict

def clean_data(offer_dict: dict) -> dict:
    "Function to transform and clean data."
    df = pd.DataFrame(offer_dict)
    
    #Cleaning and transformation of data
    df['unit'] = df.unit.str.replace('Per ', '').astype(str)
    df['save'] = df.save.str.replace('SPARA ', '').astype(str).apply(lambda x: float(''.join(x.split(':')))/100 if ':' in x else x)
    df['brand'] = df.brand.str.replace(' •', '').astype(str)
    df['price'] = df.price.astype(float)

    df['validity'] = pd.to_datetime(df['validity'])
    df['validity_week'] = df['validity'].apply(lambda x: x.isocalendar()[1])
    df['validity_year'] = df['validity'].apply(lambda x: x.isocalendar()[0])
    df = df.drop('validity', axis=1)
    #Options feature to add: rows with None values in 'save' column should be removed. These are not discount products!
    
    #Remove duplicates
    df = df.drop_duplicates()

    #Devoid dataleakage by transformation from dataframe into dict (not necessary when this small dataset)
    temp_dict = df.to_dict('split')
    
    data_dict = {c: [] for c in temp_dict['columns']}

    for row in temp_dict['data']:
        for td, col in zip(row, data_dict.values()):
                col.append(td)
    
    return data_dict

def get_offers(password: str, store_no: int, user_dict: dict) -> dict:
    store_id = fetch_id('Willys Landvetter', password, store_no)
    raw_description_list, raw_offer_dict = fetch_offers(password, store_id, store_no)
    parsed_dict = parser(raw_description_list, raw_offer_dict)
    cleaned_dict = clean_data(parsed_dict)
    
    veckans_recept_förslag = match_recipe(cleaned_dict, user_dict)
    
    return veckans_recept_förslag

### Building Streamlit Application ###
st.write(check_connection('u41c_Y'))

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
