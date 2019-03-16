class XLSUser:

    def __init__(self, last_name, first_name, email, position, departments, is_pt, account_type):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.position = position
        self.departments = departments
        self.is_pt = is_pt  # set as int, returned as bool
        self.account_type = account_type  # set as int, returned as int

##############################

    def get_last_name(self):
        return self.last_name

    def get_first_name(self):
        return self.first_name

    def get_full_name(self):
        last_name = self.get_last_name()
        first_name = self.get_first_name()

        full_name = first_name + ' ' + last_name

        return full_name

##############################

    def get_email(self):
        return self.email

##############################

    def get_position(self):
        return self.position

    def get_departments(self):
        return self.departments

##############################

    def get_is_pt(self):
        if self.is_pt == 0:
            is_pt = False
        elif self.is_pt == 1:
            is_pt = True
        else:
            raise ValueError('is_pt invalid int:', self.is_pt)

        return is_pt

##############################

    def get_account_type(self):
        return self.account_type
