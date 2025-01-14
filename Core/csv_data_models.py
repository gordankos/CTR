
from Core.daily_intake import DailyIntake
from Core.product import Product, NutritionData
from Core.recipe import Recipe
from Core.savefile_functions import savefile_header, dict_to_dataclass
from Core.ctr_data import CTRData, SavefileExtension
from Settings.app_env import Program_Version


import os
import json
import zipfile
from io import TextIOWrapper
from timeit import default_timer as timer


class CsvDataModel:
    def __init__(self, filepath: str = "", delimiter: str = ";"):
        """
        CTR csv savefile data model base class.
        """
        self.filepath = filepath
        self.delimiter = delimiter

    @property
    def data_model_identifier(self) -> str:
        return ""

    def csv_data(self, ctr_data: CTRData) -> str:
        pass

    def read_csv_data(self, csv_file, ctr_data: CTRData) -> None:
        pass

    def write_savefile(self, ctr_data: CTRData) -> None:
        print(f"Exporting {self.data_model_identifier}... filepath {self.filepath}")
        start = timer()

        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self.csv_data(ctr_data))
        f.close()

        end = timer()
        print(f"{self.data_model_identifier} saved in", end - start, "s")

    def read_savefile(self, ctr_data: CTRData) -> None:
        print(f"Importing {self.data_model_identifier}... filepath {self.filepath}")
        start = timer()

        with open(self.filepath, "r", encoding="utf-8") as f:
            self.read_csv_data(csv_file=f.readlines(), ctr_data=ctr_data)

        end = timer()
        print(f"{self.data_model_identifier} imported in", end - start, "s")


class InformationDataModel(CsvDataModel):
    def __init__(self, filepath: str = "", delimiter: str = ";"):
        """
        CTR Information data model for exporting and importing general CTR data.
        """
        super().__init__(filepath, delimiter)

    @property
    def data_model_identifier(self) -> str:
        return "Daily Intake Data"

    def csv_data(self, ctr_data: CTRData) -> str:
        data = savefile_header(savefile_type="Information", program_version=Program_Version)
        data += "\n"

        data += ctr_data.convert_to_csv()

        return data

    def read_csv_data(self, csv_file, ctr_data: CTRData) -> None:
        ctr_filename = csv_file[4].strip()
        ctr_filepath = csv_file[5].strip()
        favorite_products = json.loads(csv_file[6])
        favorite_recipes = json.loads(csv_file[7])
        target_nutrition_data = json.loads(csv_file[8])

        ctr_data.filename = ctr_filename
        ctr_data.filepath = ctr_filepath
        ctr_data.favorite_products = set(favorite_products)
        ctr_data.favorite_recipes = set(favorite_recipes)
        ctr_data.nutrition_targets = dict_to_dataclass(NutritionData, target_nutrition_data)


class DailyIntakeDataModel(CsvDataModel):
    def __init__(self, filepath: str = "", delimiter: str = ";"):
        """
        Daily intake data model for exporting and importing the Daily intake record.
        """
        super().__init__(filepath, delimiter)

    @property
    def data_model_identifier(self) -> str:
        return "Daily Intake Data"

    def csv_data(self, ctr_data: CTRData) -> str:
        data = savefile_header(savefile_type="Daily Intake Data", program_version=Program_Version)
        data += "\n"

        n_items = len(ctr_data.daily_intake_record)
        data += str(n_items) + "\n"       # Number of items in the daily intake dictionary

        for item in ctr_data.daily_intake_record.values():
            data += f"{item.convert_to_csv(self.delimiter)}\n"

        return data

    def read_csv_data(self, csv_file, ctr_data: CTRData) -> None:
        catalogue_data: dict[str, DailyIntake] = {}

        n_line = 4
        n_items = int(csv_file[n_line])

        for n in range(n_line + 1, n_line + n_items + 1):
            csv_line = csv_file[n]
            intake_data = DailyIntake.convert_from_csv(csv_line, delimiter=self.delimiter)
            catalogue_data[intake_data.date] = intake_data

        ctr_data.clear_daily_intake_data()
        ctr_data.daily_intake_record = catalogue_data


class CatalogueDataModel(CsvDataModel):
    def __init__(self, filepath: str = "", delimiter: str = ";"):
        """
        Catalogue data model for exporting and importing the Product catalogue.
        """
        super().__init__(filepath, delimiter)

    @property
    def data_model_identifier(self) -> str:
        return "Product Catalogue Data"

    def csv_data(self, ctr_data: CTRData) -> str:
        data = savefile_header(savefile_type="Catalogue Data", program_version=Program_Version)
        data += "\n"

        n_items = len(ctr_data.product_catalogue)
        data += str(n_items) + "\n"       # Number of items in the catalogue dictionary

        for item in ctr_data.product_catalogue.values():
            data += f"{item.convert_to_csv(self.delimiter)}\n"

        return data

    def read_csv_data(self, csv_file, ctr_data: CTRData) -> None:
        catalogue_data: dict[int, Product] = {}

        n_line = 4
        n_items = int(csv_file[n_line])

        for n in range(n_line + 1, n_line + n_items + 1):
            csv_line = csv_file[n]
            item = Product.convert_from_csv(csv_line, delimiter=self.delimiter)
            catalogue_data[item.item_id] = item

        ctr_data.clear_catalogue_data()
        ctr_data.product_catalogue = ctr_data.product_catalogue | catalogue_data


class RecipesDataModel(CsvDataModel):
    def __init__(self, filepath: str = "", delimiter: str = ";"):
        """
        Recipe data model for exporting and importing the Products catalogue.
        """
        super().__init__(filepath, delimiter)

    @property
    def data_model_identifier(self) -> str:
        return "Recipe Data"

    def csv_data(self, ctr_data: CTRData) -> str:
        data = savefile_header(savefile_type="Recipe Data", program_version=Program_Version)
        data += "\n"

        n_items = len(ctr_data.recipes_record)
        data += str(n_items) + "\n"       # Number of recipes in the recipes dictionary

        for item in ctr_data.recipes_record.values():
            data += f"{item.convert_to_csv(self.delimiter)}\n"

        return data

    def read_csv_data(self, csv_file, ctr_data: CTRData) -> None:
        recipe_data: dict[int, Recipe] = {}

        n_line = 4
        n_items = int(csv_file[n_line])

        for n in range(n_line + 1, n_line + n_items + 1):
            csv_line = csv_file[n]
            recipe = Recipe.convert_from_csv(
                csv_line,
                product_catalogue=ctr_data.product_catalogue,
                delimiter=self.delimiter)
            recipe_data[recipe.item_id] = recipe

        ctr_data.clear_recipe_data()
        ctr_data.recipes_record = ctr_data.recipes_record | recipe_data


class CTRDataModel:
    def __init__(self, filepath: str = "", delimiter: str = ";"):
        self.filepath = filepath
        self.delimiter = delimiter

        self.ctr_info_filename = f"CTR Information{SavefileExtension.INFORMATION.value}"
        self.product_catalogue_filename = f"Product Catalogue{SavefileExtension.CATALOGUE.value}"
        self.recipes_filename = f"Recipes{SavefileExtension.RECIPES.value}"
        self.daily_intake_filename = f"Daily Intake Data{SavefileExtension.DAILY_INTAKE.value}"

        self.report_messages: list[str] = []

    def write_savefile(self, ctr_data: CTRData):
        print(f"Saving CTR Data file to {self.filepath}.")
        start = timer()

        ctr_data.filepath = str(self.filepath)
        with zipfile.ZipFile(self.filepath, "w") as ctr_savefile:
            ctr_info = InformationDataModel(self.filepath).csv_data(ctr_data)
            ctr_savefile.writestr(zinfo_or_arcname=self.ctr_info_filename, data=ctr_info)

            product_catalogue_data = CatalogueDataModel(self.filepath).csv_data(ctr_data)
            ctr_savefile.writestr(zinfo_or_arcname=self.product_catalogue_filename, data=product_catalogue_data)

            recipes_data = RecipesDataModel(self.filepath).csv_data(ctr_data)
            ctr_savefile.writestr(zinfo_or_arcname=self.recipes_filename, data=recipes_data)

            daily_intake_data = DailyIntakeDataModel(self.filepath).csv_data(ctr_data)
            ctr_savefile.writestr(zinfo_or_arcname=self.daily_intake_filename, data=daily_intake_data)

        end = timer()
        print("CTR Data saved in", end - start, "s")

    def read_savefile(self):
        msg = f"Opening CTR Data savefile {self.filepath}."
        # self.report_messages.append(msg)
        print(msg)

        start = timer()

        ctr_data = CTRData("CTR Savefile")

        if not os.path.exists(self.filepath):
            msg = f"Error: Path {self.filepath} does not exist!"
            # self.report_messages.append(msg)
            print(msg)
            return ctr_data

        with zipfile.ZipFile(self.filepath, "r") as ctr_savefile:
            file_list: list[zipfile.ZipInfo] = ctr_savefile.filelist
            filenames = [file.filename for file in file_list]

            if self.ctr_info_filename in filenames:
                # print(f"CTR Information data is in file list at index {filenames.index(self.ctr_info_filename)}")
                with ctr_savefile.open(self.ctr_info_filename, mode="r") as savefile:
                    csv_data = list(TextIOWrapper(savefile, encoding="utf-8", newline="\n"))
                    InformationDataModel().read_csv_data(csv_file=csv_data, ctr_data=ctr_data)

            if self.product_catalogue_filename in filenames:
                # print(f"Product catalogue is in file list at index {filenames.index(self.product_catalogue_filename)}")
                with ctr_savefile.open(self.product_catalogue_filename, mode="r") as savefile:
                    csv_data = list(TextIOWrapper(savefile, encoding="utf-8", newline="\n"))
                    CatalogueDataModel().read_csv_data(csv_file=csv_data, ctr_data=ctr_data)

            if self.recipes_filename in filenames:
                # print(f"Recipes data is in file list at index {filenames.index(self.recipes_filename)}")
                with ctr_savefile.open(self.recipes_filename, mode="r") as savefile:
                    csv_data = list(TextIOWrapper(savefile, encoding="utf-8", newline="\n"))
                    RecipesDataModel().read_csv_data(csv_file=csv_data, ctr_data=ctr_data)

            if self.daily_intake_filename in filenames:
                # print(f"Daily intake data is in file list at index {filenames.index(self.daily_intake_filename)}")
                with ctr_savefile.open(self.daily_intake_filename, mode="r") as savefile:
                    csv_data = list(TextIOWrapper(savefile, encoding="utf-8", newline="\n"))
                    DailyIntakeDataModel().read_csv_data(csv_file=csv_data, ctr_data=ctr_data)

        end = timer()
        print("CTR Data opened in", end - start, "s")

        return ctr_data
