# Libraries Packages
import datetime


class dataType:
    def set_column_type_date(self, data, column, option):
        __dates = []

        if option == 1:
            data[column] = data[column].str.slice(0, 10)

            for row in data[column]:
                __date = row.split("-")
                __dates.append(datetime.date(int(__date[0]), int(__date[1]), int(__date[2])).strftime("%Y-%m-%d"))

        elif option == 2:
            for row in data[column]:
                __date = row.split("-")
                __dates.append(datetime.date(int(__date[0]), int(__date[1]), int(__date[2])).strftime("%d/%m/%Y"))

        elif option == 3:
            data[column] = data[column].str.slice(0, 10)

            for row in data[column]:
                __date = row.split("-")
                __dates.append(datetime.date(int(__date[0]), int(__date[1]), int(__date[2])).strftime("%d/%m/%Y"))

        data[column] = __dates

    def set_column_type_float(self, data, column):
        data[column] = data[column].astype(float)

    def set_column_type_integer(self, data, column):
        data[column] = data[column].astype(int)

    def set_column_type_string(self, data, column):
        data[column] = data[column].astype(str)
