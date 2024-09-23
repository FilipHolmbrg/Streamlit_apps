#Imports
import logging
from get_store_object import StoreObject
from api import fetch_offers
from parser import parser
from data_cleaner import clean_data
from data_saver import save_data
from recipe_matcher import match_recipe

def main():

    logger = logging.getLogger(__name__)
    # Configurate logger messages
    logging.basicConfig(
        filename='pipeline.log', 
        format='[%(asctime)s][%(name)s] %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S', 
        level=logging.DEBUG)

    stores = ['Willys Landvetter'] #List of stores to get offers from
    
    for store in stores:
        logger.info(f'Starting data pipeline on {store}')
        
        store_object = StoreObject(store) # initalize object to hold attributes
        # Pipeline: Extract, Transform, Load
        raw_description_list, raw_offer_dict = fetch_offers(store_object)
        parsed_dict = parser(raw_description_list, raw_offer_dict)
        cleaned_dict = clean_data(parsed_dict)
        save_data(cleaned_dict, store_object)
        
        veckans_recept_förslag = match_recipe(cleaned_dict)
        print("Med veckans erbjudande kan man laga..")
        for key, val in veckans_recept_förslag.items():
            print(f"{key}: {val}")
        
    logger.info(f'Data pipeline on finalized')
    
if __name__ == '__main__':
    main()