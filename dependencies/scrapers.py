from dependencies import utilities, decorators


# the scrapers may be fucked if it found any string with single quotes
headers = {'User-Agent': 'Mozilla/5.0'}


@ decorators.timer
@ decorators.log_outputs
def scrape_orion(show_details=False, show_records=False):
    i = 0
    item_url_list = []
    data_of_all_telescopes = []
    resolution = experience = optical_design = optical_diameter = focal_length = focal_ratio = mount_type = interest = eyepieces = focuser = weight = name = None

    core_url = 'https://www.telescope.com/'

    endpoint_map = {
        'beginner': 'All-Telescopes/User-Level/Beginner-Telescopes/rc/2162/pc/2134/2044.uts?currentIndex=0&pageSize=81&defaultPageSize=20&mode=viewall&categoryId=2134&subCategoryId=2044&type=thumbnail2level',
        'intermediate': 'All-Telescopes/User-Level/Intermediate-Telescopes/rc/2162/pc/2134/2045.uts?currentIndex=0&pageSize=22&defaultPageSize=20&mode=viewall&categoryId=2134&subCategoryId=2045&type=thumbnail2level',
        'advanced': 'All-Telescopes/User-Level/Advanced-Telescopes/rc/2162/pc/2134/2046.uts?currentIndex=0&pageSize=62&defaultPageSize=20&mode=viewall&categoryId=2134&subCategoryId=2046&type=thumbnail2level'
    }

    specs_map = {'User level': experience,
                 'Optical design': optical_design,
                 'Optical diameter': optical_diameter,
                 'Focal length': focal_length,
                 'Focal ratio': focal_ratio,
                 'Mount type': mount_type,
                 'Resolving power': resolution,
                 'Best for viewing': interest,
                 'Eyepieces': eyepieces,
                 'Focuser': focuser,
                 'Weight, fully assembled': weight
                 }

    title_to_name_map = {'User level': 'experience',
                         'Optical design': 'optical_design',
                         'Optical diameter': 'aperture',
                         'Focal length': 'focal_length',
                         'Focal ratio': 'focal_ratio',
                         'Mount type': 'mount',
                         'Resolving power': 'resolution',
                         'Best for viewing': 'interest',
                         'Eyepieces': 'eyepieces',
                         'Focuser': 'focuser',
                         'Weight, fully assembled': 'weight'
                         }

    # maybe not the best way to get dictionary value but others i found are just as dogshit
    # gets instance
    for endpoint_key in endpoint_map:
        soup = utilities.get_soup(core_url + endpoint_map[endpoint_key], headers)
        telescopes = soup.find_all('div', class_='thumbnail-content')

        # collects all telescope/page urls
        for telescope in telescopes:
            telescope_url = telescope.a['href']
            item_url_list.append(telescope_url)

    # goes to each page and gathers all necessary data
    for item_url in item_url_list:
        spec_rows = []
        i += 1

        soup = utilities.get_soup(core_url + item_url, headers=headers)
        specs_table = soup.find('ul', class_='tab-content')
        all_specs = specs_table.find_all('li')
        for spec in all_specs:
            telescope_title = utilities.get_title(spec)
            telescope_value = utilities.get_value(spec.div, 'attr-value')
            spec_rows.append([telescope_title, telescope_value])

        specs_raw_output = utilities.get_telescope_specs(specs_map, spec_rows)
        specs_polished_output = utilities.assemble_output_dictionary(specs_raw_output, title_to_name_map)

        specs_polished_output['name'] = utilities.get_value(soup, 'item-name')

        price_block = utilities.get_price_block(soup)
        try:
            specs_polished_output['price'] = utilities.get_value(price_block, 'fl price')
        except AttributeError:
            specs_polished_output['price'] = utilities.get_value(price_block, 'current-price only center price')
        finally:
            specs_polished_output['price'] = utilities.polish_prices(specs_polished_output['price'])

        utilities.show_results(i, show_details, show_records, specs_polished_output)

        data_of_all_telescopes.append(specs_polished_output)

    if show_details:
        print(f'sucessfully gathered all {i} telescopes')

    return data_of_all_telescopes
    # it appears that it ignores empty specs


def scrape_celestron(show_details=True, show_records=False):
    telescope_data = []
    core_url = 'https://www.go-astronomy.com/telescopes/'
    main_url = core_url + 'celestron-telescopes.php'
    i = 0

    # upper level
    soup = utilities.get_soup(main_url, {'User-Agent': 'Mozilla/5.0'})
    telescopes = soup.find('table').find('tbody').find_all('tr')

    price = optical_design = aperture = focal_length = focal_ratio = mount = resolution = None

    specs_map = {
        'Approx price:': price,
        'Optical design:': optical_design,
        'Aperture:': aperture,
        'Focal Length:': focal_length,
        'Focal Ratio:': focal_ratio,
        'Dawes Limit:': resolution,
        'Mount:': mount
    }

    title_to_name_map = {
        'Approx price:': 'price',
        'Optical design:': 'optical design',
        'Aperture:': 'aperture',
        'Focal Length:': 'focal length',
        'Focal Ratio:': 'focal ratio',
        'Dawes Limit:': 'resolution',
        'Mount:': 'mount'
    }

    for telescope in telescopes:
        i += 1
        spec_rows = []

        detail = telescope.find('td')
        telescope_endpoint = detail.a['href']

        # lower level
        deep_soup = utilities.get_soup(core_url + telescope_endpoint, headers=headers)
        specs = deep_soup.find('table').find('tbody').find_all('tr')

        for spec in specs:
            split_spec = spec.find_all('td')
            spec_rows.append([split_spec[0].text, split_spec[1].text])

        specs_raw_output = utilities.get_telescope_specs(specs_map, spec_rows)
        specs_polished_output = utilities.assemble_output_dictionary(specs_raw_output, title_to_name_map)
        specs_polished_output['name'] = deep_soup.find_all('h1')[2].text
        specs_polished_output['price'] = utilities.polish_prices(specs_polished_output['price'])

        utilities.show_results(i, show_details, show_records, specs_polished_output)

    if show_details:
        print(f'sucessfully gathered all {i} telescopes')

    return telescope_data


if __name__ == '__main__':
    # scrape_orion(show_details=True, show_records=True)
    scrape_orion()
