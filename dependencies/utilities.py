import requests
from bs4 import BeautifulSoup


def get_title(spec):
    return spec.div.div.contents[1].text.strip()


def get_value(spec, class_value):
    return spec.find('div', class_=class_value).text.strip()


def get_price_block(_soup):
    return _soup.find('div', id='entity-price-widget')


def get_soup(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


# spec rows = [title, value]
# add the data to a common dictionary instead of the map dictionary
def get_telescope_specs(specs_map_instance, spec_rows):
    if not isinstance(specs_map_instance, dict):
        raise TypeError('specs_map_instance must be a dictionary')
    if not isinstance(spec_rows, list):
        raise TypeError('spec_rows must be a list')

    for row in spec_rows:
        title = row[0]
        value = row[1]
        if title in specs_map_instance:
            specs_map_instance[title] = value

    return specs_map_instance


def assemble_output_dictionary(data_dictoinary, title_to_name_map):
    output_dictionary = {}
    for key in data_dictoinary:
        output_dictionary[title_to_name_map[key]] = data_dictoinary[key]
    return output_dictionary


def polish_prices(raw_price):
    garbage_values = ['$', ',', '*']
    clean_price = raw_price

    dot_index = clean_price.find('.')
    if dot_index != -1:
        clean_price = clean_price[0:dot_index]

    for g_value in garbage_values:
        clean_price = clean_price.replace(g_value, '')

    try:
        return int(clean_price)
    except ValueError:
        raise ValueError(f'invalid literal for int() with base 10: "{clean_price}". expected literals: {garbage_values}')


def show_results(i, show_details, show_records, specs_polished_output):
    if show_details:
        print(f'{i} telescopes gathered')

    if show_records:
        print(specs_polished_output)


def filter_interests(detail_map):
    interest_value = detail_map['interest']
    if interest_value == 'Nature & scenic':
        detail_map['interest'] = 'terrestial'
    elif interest_value == 'Lunar & terrestrial':
        detail_map['interest'] = 'pending'
    elif interest_value == 'Brighter deep sky' or interest_value == 'Fainter deep sky' or interest_value == 'Lunar & bright deep sky':
        detail_map['interest'] = 'deep sky'
    elif interest_value == 'Lunar & planetary':
        detail_map['interest'] = 'planetary'
    return detail_map


single_quote_symbol = '%1q'
double_quotes_symbol = '%2q'


def pack_quotes(string):
    return string.replace("'", single_quote_symbol).replace('"', double_quotes_symbol)


def unpack_quotes(string):
    return string.replace(single_quote_symbol, "'").replace(double_quotes_symbol, '"')

# if __name__ == '__main__':
#     print(polish_prices('$200'))

