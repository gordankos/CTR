"""
Utility module enabling image conversion from .png to .ico in development environment

"""

from Settings.app_env import working_directory

from PIL import Image


def png_to_ico(png_path, ico_path):
    image = Image.open(png_path)
    image.save(ico_path, format="ICO")

    print(f'Converted {png_path} to {ico_path}')


if __name__ == "__main__":
    png_to_ico(
        png_path=working_directory + "logo.png",
        ico_path=working_directory + "logo.ico"
    )
