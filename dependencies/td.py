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

        telescope_data_map = {}
        sql_get_command = '''
        SELECT id, budget FROM user WHERE
        experience = "{experience}" AND
        interest = "{interest}" AND
        portable = "{portable}" AND
        astrophoto = "{astrophoto}" AND
        setup = "{setup}" AND
        budget <= {budget}
        ORDER BY ABS({budget} - budget) LIMIT 1;
        '''

        telescope_data_keys = ['name', 'optical design', 'aperture', 'focal length', 'focal ratio', 'mount',
                               'resolution']

        self.curser.execute(sql_get_command.format(**user_dictionary))

        try:
            user_table_output = self.curser.fetchone()

            telescope_id = user_table_output[0]
            self.curser.execute(f'SELECT name, optical_design, aperture, focal_length, focal_ratio, mount, resolution FROM details WHERE id = {telescope_id};')
            telescope_data_values = self.curser.fetchone()

            for i in range(len(telescope_data_keys)):
                telescope_data_map[telescope_data_keys[i]] = telescope_data_values[i]
            telescope_data_map['price'] = user_table_output[1]

        except TypeError:
            telescope_data_map = None

        return telescope_data_map

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
