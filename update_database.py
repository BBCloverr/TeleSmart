import json
from dependencies.scrapers import scrape_orion
import ast
import pprint
from dependencies.td import TelescopeDatabase
from dependencies.utilities import filter_interests, pack_quotes
from dependencies.AI import get_user_details
import os


string_values = ['aperture', 'focal_length', 'focal_ratio', 'mount', 'name', 'optical_design', 'resolution']
list_dict = []
i = 0
conditions_path = "conditions.json"


def update_is_finished(boolien_value):
    with open(conditions_path, 'r+') as file:
        json_dict = json.loads(file.read())
        json_dict['is_finished'] = boolien_value
        file.seek(0)
        json.dump(json_dict, file)
        file.truncate()

# user section
print('to add new data press 1, to update the existing data press 2 or if you wish to exit the program press 0')
print('once you have chosen your mode press enter to proceed')

while True:
    mode = input('please enter your mode here: ')

    if mode == '0':
        quit()
    elif mode == '1' or mode == '2':
        pass
    else:
        print('incorrect input please try again')
        continue

    with open(conditions_path, 'r') as conditions_file:
        is_finished = json.loads(conditions_file.read())['is_finished']

    print("gathering data please wait...")

    if is_finished:
        print("scraping telescope data...")
        list_dict = scrape_orion(show_details=True)
        update_is_finished(False)
    else:
        # select the youngest file and readies it
        print("loading pre-gathered scraper output file...")
        outputs_directory = "outputs"
        all_filenames = os.listdir(outputs_directory)
        full_paths = [os.path.join(outputs_directory, filename) for filename in all_filenames]
        scraper_output_filepath = max(full_paths, key=os.path.getctime)
        with open(scraper_output_filepath, 'r') as scraper_output_file:
            list_dict = ast.literal_eval(scraper_output_file.read())

    print("done!")

    database_connection = TelescopeDatabase()
    if mode == '1':   # add data code
        for dictionary in list_dict:
            i += 1
            dictionary_items = dictionary.items()
            for key, value in dictionary_items:
                if key in string_values:
                    dictionary[key] = pack_quotes(value)

            if not database_connection.exists(dictionary['name']):
                dictionary = filter_interests(dictionary)

                get_user_data_input = {k: v for k, v in dictionary_items if k not in ['price', 'name', 'interest']}
                user_dictionary = {k: v for k, v in dictionary_items if k in ['experience', 'price', 'interest']}
                details_dictionary = {k: v for k, v in dictionary_items if
                                      k in ['optical_design', 'aperture', 'focal_length', 'focal_ratio', 'mount',
                                            'resolution',
                                            'name']}

                get_user_details_output = get_user_details(get_user_data_input)
                user_dictionary.update(get_user_details_output)
                pprint.pp(user_dictionary)

                database_connection.insert_data(user_dictionary, 'user')
                database_connection.insert_data(details_dictionary, 'details')

                print(f'succesfully added record {i} \n')
            else:
                print(f'skipped record {i}')
        update_is_finished(True)
        print("successfully added all the data to the database")

    # might wanna put a way to figure out which of the pric2es were truly changed from the original one
    elif mode == '2':
        for dictionary in list_dict:
            database_connection.update_price(pack_quotes(dictionary['name']), dictionary['price'], show_details=True)
        update_is_finished(True)
        print("successfully updated all the prices of the database")
