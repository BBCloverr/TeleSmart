import mysql.connector
import json


with open("apikeys.json") as config:
    database_data = json.loads(config.read())["mysql"]


class TelescopeDatabase:
    def __init__(self):
        # There are two tables named user and details in the schema
        self.db = mysql.connector.connect(
            host=database_data["host"],
            user=database_data["user"],
            passwd=database_data["passwd"],
            database=database_data["database"]
        )
        self.curser = self.db.cursor()

    def insert_data(self, data_dictionary, table):
        if table == 'details':
            data_insert_command = "INSERT INTO details (name, optical_design, aperture, focal_length, focal_ratio, mount, resolution)" \
                         " VALUES ('{name}','{optical_design}','{aperture}','{focal_length}','{focal_ratio}','{mount}','{resolution}')"
        elif table == 'user':
            data_insert_command = "INSERT INTO user (experience, budget, interest, portable, astrophoto, setup)" \
                         " VALUES ('{experience}', '{price}', '{interest}', '{portable}', '{astrophoto}', '{setup}')"
        else:
            raise ValueError('incorrect value for table parameter. use "user" or "details" as the value for table')

        self.curser.execute(data_insert_command.format(**data_dictionary))
        self.db.commit()

    def show_table(self, table_name):
        self.curser.execute('SELECT * FROM {table_name}'.format(table_name=table_name))
        return self.curser.fetchall()

    def get_telescope_data(self, user_dictionary):

        def translate_user_dictionary(_user_dictionary, mode):
            translation_table = {
                "portable": [{1: "yes", 0: "no"}, {"yes": 1, "no": 0}],
                "astrophoto": [{1: "yes", 0: "no"}, {"yes": 1, "no": 0}],
                "setup": [{1: "simple", 2: "moderate", 3: "complex"}, {"simple": 1, "moderate": 2, "complex": 3}],
                "telescope_portability": [{1: "yes", 0: "no"}],
                "telescope_astrophotography": [{1: "yes", 0: "no"}],
                "telescope_setup": [{1: "simple", 2: "moderate", 3: "complex"}]
            }

            for label in _user_dictionary.keys():
                if label in translation_table.keys():
                    _user_dictionary[label] = translation_table[label][mode][_user_dictionary[label]]
            return _user_dictionary

        telescope_data_map = {}
        sql_get_command = '''
        select details.name,  details.aperture,  details.focal_length,  details.focal_ratio,  details.mount,  details.optical_design, user.budget,  details.resolution, user.portable, user.astrophoto, user.setup
        from details inner join user on details.id = user.id 
        where user.experience = "{experience}" and user.budget <= {budget} and user.interest = "{interest}" and user.portable >= {portable} and user.astrophoto >= {astrophoto} and user.setup <= {setup}
        order by user.astrophoto asc, user.portable asc, user.setup desc, user.budget desc
        limit 1;
        '''

        telescope_data_keys = ['name', 'aperture', 'focal length', 'focal ratio', 'mount', 'optical design', 'price',
                               'resolution', 'telescope_portability', 'telescope_astrophotography', 'telescope_setup']

        user_dictionary = translate_user_dictionary(user_dictionary, mode=1)

        self.curser.execute(sql_get_command.format(**user_dictionary))

        try:
            telescope_data_values = self.curser.fetchone()

            for i in range(len(telescope_data_keys)):
                telescope_data_map[telescope_data_keys[i]] = telescope_data_values[i]
            telescope_data_map = telescope_data_map | user_dictionary
            output = translate_user_dictionary(telescope_data_map, mode=0)

        except TypeError:
            telescope_data_map = None
            output = telescope_data_map

        return output

    def exists(self, name):
        is_there = False
        self.curser.execute(f'SELECT COUNT(*) FROM details WHERE name = "{name}";')
        if self.curser.fetchone()[0] != 0:
            is_there = True
        return is_there

    # this doesn't actually differentiate and show which rows are updated and which aren't.
    # it just shows you which rows it cycled through
    def update_price(self, name, new_price, show_details=False):
        get_id_code = f'SELECT id FROM details WHERE name = "{name}";'
        self.curser.execute(get_id_code)
        telescope_id = self.curser.fetchone()[0]
        self.curser.execute(f"UPDATE user SET budget = {new_price} WHERE id = {telescope_id};")
        self.db.commit()
        if show_details:
            print(f"successfully updated the price of telescope with id: {telescope_id}")
