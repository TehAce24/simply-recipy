import tkinter
from typing import Any
import customtkinter
import os
import requests
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv
from ratelimit import limits

# Initiates dotenv and retrieve api key
load_dotenv()
api_key = os.getenv("api_key")

# URL for API
base_url = "https://api.spoonacular.com/"

image_url = ""
recipe_str = ""
item_str = ""

# Appends list from Ctk.Entry
entries: list = []
entry_num: list = []
store_image: list = []
image_label = []

# For saving recipe
name_save: list = []
items_save: list = []
direction_save: list = []

# Max amount of
# calls measured in seconds
api_call_time = 30


def slider_value(*args: tuple[Any, ...]) -> int:
    # Updates value for slider
    # and changes fridge_label
    # to value of slider
    global fridge_label

    value = int(slider_1.get())
    slider_text.configure(text=value)

    if fridge_label:
        fridge_label.grid_forget()

    if value == 1:
        fridge4.grid(row=4, column=1)
        fridge_label = fridge4
    elif value == 2:
        fridge3.grid(row=4, column=1)
        fridge_label = fridge3
    elif value == 3:
        fridge2.grid(row=4, column=1)
        fridge_label = fridge2
    elif value == 4:
        fridge1.grid(row=4, column=1)
        fridge_label = fridge1
    elif value == 5:
        fridge.grid(row=4, column=1)
        fridge_label = fridge
    return value


def slider_entries() -> None:
    global entry
    button_submit1.grid_forget()
    slider_frame.grid_forget()
    title1.grid_forget()

    title2.grid(column=0, columnspan=2)
    entry_frame.grid(row=1, column=1, padx=20, pady=20, columnspan=2)
    n = int(slider_1.get())
    for i in range(n):
        entry = customtkinter.CTkEntry(entry_frame)
        entry.grid(row=1 + i, column=1, padx=1, pady=1)
        entries.append(entry)
        entry_numbers = customtkinter.CTkLabel(entry_frame, text=f'({i + 1})')
        entry_numbers.grid(row=1 + i, padx=1, pady=1)
        entry_num.append(entry_numbers)
    button_submit2.grid(row=6, column=0, padx=20, pady=20, columnspan=2)


def main():
    # Main function for extracting API
    if image_label:
        image_label.grid_forget()
    while True:
        try:
            entry_items: list = get_items(entries)
            entry: bool = valid_items(entry_items)
            if not entry:
                error_label.grid(column=1)
                break
            elif entry:
                title2.grid_forget()
                check_error()
                item_strings: str = join_items(entry_items)

                recipe: requests.Response = api_recipe_by_ingredients(item_strings, base_url, api_key)
                data: dict = recipe.json()
                print_items(data)

                title: int = get_title_id(data)
                images: str = get_image(data)

                recipe_image(images)
                recipe_steps: requests.Response = api_recipe_instructions(title, base_url, api_key)
                steps: dict = recipe_steps.json()
                print_instructions(steps)
                break
        except Exception as e:
            print(e)
            api_error.grid(column=1)
            break


def get_items(entry_item: list) -> list:
    items = []
    for o in entry_item:
        i = o.get()
        items.append(i)
    return items


def valid_items(items: list) -> bool:
    """
    :param items: Items from entries: list
    :return: Boolean for validating
    """
    for string in items:
        if any(char.isdigit() for char in string):
            return False
        elif string == "":
            return False
    else:
        return True


def join_items(i: list) -> str:
    items_str = ','.join(i)
    return items_str


def check_error():
    # Removes error label if valid_items returned False
    if error_label:
        error_label.grid_forget()
    if api_error:
        api_error.grid_forget()
    if error_label:
        error_label.grid_forget()


@limits(calls=5, period=api_call_time)
def api_recipe_by_ingredients(i: str, url: str, key: str) -> requests.Response:
    """
    limit decorator is set to 5 calls every 30 seconds.
    :param i: List of ingredients.
    :param url: URL from Spoonacular API.
    :param key: api key.
    :return: Return response status
    """
    url = f"{url}recipes/findByIngredients?apiKey={key}&ingredients={i}&number=1&ignorePantry=false"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    else:
        return response


def print_items(data: dict) -> None:
    """
    :param data: The JSON data received from Spoonaculars API.
    """
    global image_url

    # Allows textbox to be edited
    # then deletes any previous text
    textbox_recipe.configure(state="normal")
    textbox_directions.configure(state="normal")
    textbox_directions.delete('0.0', 'end')
    textbox_recipe.delete('0.0', 'end')

    for recipe in data:
        recipe_name = recipe["title"]
        recipe_label.configure(text=recipe_name)
        name_save.append(recipe_name)
        label_frame.grid(row=2, column=1, padx=5, pady=5)

        image = recipe["image"]
        image_url = image

        # Used Ingredients are ingredients the User has input.
        for used_ingredient in recipe["usedIngredients"]:
            original_used = used_ingredient["original"]
            items_save.append(original_used)
            textbox_recipe.insert("0.0", text=original_used + '\n')

        # Missed Ingredients are other
        # ingredients the User did not input.
        for missed_ingredient in recipe["missedIngredients"]:
            original_missed = missed_ingredient["original"]
            items_save.append(original_missed)
            textbox_recipe.insert("end", text=original_missed + '\n')

    # Disables textbox after
    # inserting recipe to textbox
    textbox_recipe.configure(state="disabled")
    textbox_directions.configure(state="disabled")


def get_title_id(data: dict) -> int:
    # id number of recipe for
    # instructions and images.
    id_number = None
    for i in data:
        id_number = i["id"]
    return id_number


@limits(calls=5, period=api_call_time)
def api_recipe_instructions(num: int, url: str, key: str) -> requests.Response:
    # Calls are limited to 5 every 30 seconds
    url = f"{url}recipes/{num}/analyzedInstructions?apiKey={key}&stepBreakdown=false"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    else:
        return response


def print_instructions(data: dict) -> None:
    textbox_directions.configure(state="normal")
    for i in data:
        steps = i["steps"]
        for step in steps:
            number = step["number"]
            directions = step["step"]
            direction_save.append(f"{number}. {directions}")
            textbox_directions.insert("end", text=f'\n{number}. {directions} \n')
    textbox_directions.configure(state="disabled")


def get_image(data: dict) -> str:
    image = None
    for images in data:
        image = images["image"]
    return image


def recipe_image(url) -> None:
    global image_label
    if fridge_label:
        fridge_label.grid_forget()

    response = requests.get(url, params={'apiKey': api_key})
    image_data = response.content
    image = Image.open(BytesIO(image_data))
    store_image = ImageTk.PhotoImage(image)
    image_label = customtkinter.CTkLabel(image_frame, image=store_image, text='')
    image_label.grid(column=1)


def save_dialog():
    text1 = textbox_recipe.get('0.0', 'end')
    text2 = textbox_directions.get('0.0', 'end')

    if any(char.isalpha() for char in text1 and text2):
        if textbox_error:
            textbox_error.grid_forget()
        dialog = customtkinter.CTkInputDialog(text="Save as..:")
        file_name: str = dialog.get_input()
        print(f"File: {file_name}.txt")
        if file_name is not None:
            return save_recipe(file_name)
    elif text1 or text2 == "\n" or "":
        textbox_error.grid(row=3)
        print("box is empty")


def save_recipe(file_name: str):
    # Locate current directory path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(f"{file_name}.txt", "w", newline="") as file:
            file.write(f"Name: {name_save}\n")
            file.write(f"Ingredients:\n")
            for i in items_save:
                file.write(f"- {i}\n")
            file.write(f"\n----Directions----\n")
            for s in direction_save:
                file.write(f"{s}\n")
            print(f"File saved to {dir_path}\\{file_name}.txt")
            return file
    except OSError as e:
        print(e)


def reset():
    # Clears all entries and widgets
    if entry_frame:
        entry_frame.grid_forget()
    if label_frame:
        label_frame.grid_forget()

    for entry_boxes in entries:
        entry_boxes.destroy()
    for entry_numbers in entry_num:
        entry_numbers.destroy()

    textbox_recipe.configure(state="normal")
    textbox_directions.configure(state="normal")
    textbox_directions.delete('0.0', 'end')
    textbox_recipe.delete('0.0', 'end')
    textbox_recipe.configure(state="disabled")
    textbox_directions.configure(state="disabled")

    entry_num.clear()
    entries.clear()

    button_submit1.grid(row=2, column=1, padx=20, pady=5, columnspan=2)
    slider_frame.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
    title1.grid(row=0, column=3, padx=5, pady=5)
    fridge_label.grid(row=4, column=1)

    if image_label:
        image_label.grid_forget()


def theme_mode(choice):
    if choice == 'Light':
        customtkinter.set_appearance_mode('light')
        button_exit.configure(text_color='black')
        button_home.configure(text_color='black')
        button_save.configure(text_color='black')
    else:
        customtkinter.set_appearance_mode('dark')
        button_exit.configure(text_color='white')
        button_home.configure(text_color='white')
        button_save.configure(text_color='white')


if __name__ == '__main__':
    """Main GUI"""
    root = customtkinter.CTk()
    root.title("Simply Recipe")
    root.rowconfigure(1, weight=1)
    root.columnconfigure(1, weight=5)

    """Theme"""
    customtkinter.set_appearance_mode('light')
    customtkinter.set_default_color_theme('green')

    """Frames"""
    tabview = customtkinter.CTkTabview(root)
    tabview.add("Ingredients")
    tabview.add("Directions")
    tabview.set("Ingredients")
    label_frame = customtkinter.CTkFrame(root, corner_radius=10, border_width=0,
                                         fg_color='seagreen4')
    textbox_recipe_frame = customtkinter.CTkFrame(tabview.tab("Ingredients"), height=200,
                                                  corner_radius=5, border_width=5)
    textbox_step_frame = customtkinter.CTkFrame(tabview.tab("Directions"), height=200,
                                                corner_radius=5, border_width=5)
    menu_frame = customtkinter.CTkFrame(root)
    slider_frame = customtkinter.CTkFrame(root, border_color='seagreen4', border_width=2)
    entry_frame = customtkinter.CTkFrame(root)
    image_frame = customtkinter.CTkFrame(root, fg_color='transparent')

    """Images"""
    fridge_image = customtkinter.CTkImage(Image.open("assets/images/fridge.png"), size=(200, 200))
    fridge_image1 = customtkinter.CTkImage(Image.open("assets/images/fridge1.png"), size=(200, 200))
    fridge_image2 = customtkinter.CTkImage(Image.open("assets/images/fridge2.png"), size=(200, 200))
    fridge_image3 = customtkinter.CTkImage(Image.open("assets/images/fridge3.png"), size=(200, 200))
    fridge_image4 = customtkinter.CTkImage(Image.open("assets/images/fridge4.png"), size=(200, 200))
    fridge = customtkinter.CTkLabel(image_frame, image=fridge_image, text="")
    fridge1 = customtkinter.CTkLabel(image_frame, image=fridge_image1, text="")
    fridge2 = customtkinter.CTkLabel(image_frame, image=fridge_image2, text="")
    fridge3 = customtkinter.CTkLabel(image_frame, image=fridge_image3, text="")
    fridge4 = customtkinter.CTkLabel(image_frame, image=fridge_image4, text="")
    fridge_label = fridge2
    logo_image = customtkinter.CTkImage(Image.open("assets/images/logo.png"), size=(250, 90))
    home_icon = customtkinter.CTkImage(Image.open("assets/images/home.png"))
    save_icon = customtkinter.CTkImage(Image.open("assets/images/save.png"))
    exit_icon = customtkinter.CTkImage(Image.open("assets/images/exit.png"))

    """Buttons"""
    button_submit1 = customtkinter.CTkButton(root, text='Submit', command=slider_entries)
    button_submit2 = customtkinter.CTkButton(entry_frame, text='Submit', command=main)
    button_exit = customtkinter.CTkButton(menu_frame, text='Exit', command=root.quit, image=exit_icon,
                                          compound='left', anchor='w', height=50, border_spacing=0,
                                          fg_color='transparent', text_color='black')
    button_save = customtkinter.CTkButton(menu_frame, text='Save', command=save_dialog, image=save_icon,
                                          compound='left', anchor='w', height=50, border_spacing=0,
                                          fg_color='transparent', text_color='black')
    button_home = customtkinter.CTkButton(menu_frame, text='Home', command=reset, image=home_icon,
                                          compound='left', anchor='w', height=50, border_spacing=0,
                                          fg_color='transparent', text_color='black')

    """Slider"""
    slider_1 = customtkinter.CTkSlider(slider_frame, from_=1, to=5, command=slider_value, corner_radius=20,
                                       progress_color='darkgreen', number_of_steps=10)
    slider_text = customtkinter.CTkLabel(slider_frame, text='3', font=('Helvetica ', 16))
    slider_text_arrow = customtkinter.CTkLabel(slider_frame, text='▼')

    """Textbox"""
    textbox_recipe = customtkinter.CTkTextbox(textbox_recipe_frame, width=300, font=('Helvetica ', 12),
                                              wrap='word')
    textbox_recipe.configure(state="disabled")
    textbox_directions = customtkinter.CTkTextbox(textbox_step_frame, width=300, font=('Helvetica ', 12),
                                                  wrap='word')
    textbox_directions.configure(state="disabled")

    """Labels"""
    title1 = customtkinter.CTkLabel(slider_frame, text="# of Items",
                                    bg_color='transparent')
    title2 = customtkinter.CTkLabel(entry_frame, text="What's in the Fridge?", font=('Helvetica ', 16))
    recipe_label = customtkinter.CTkLabel(label_frame, text=recipe_str, font=('Helvetica ', 16))
    error_label = customtkinter.CTkLabel(entry_frame, text="Invalid input(s)", text_color='red')
    textbox_error = customtkinter.CTkLabel(menu_frame, text="Search recipe first...", text_color='red')
    api_error = customtkinter.CTkLabel(entry_frame, text="Too many requests, please wait...", text_color='red')
    save_error = customtkinter.CTkLabel(menu_frame, text="Invalid file name...", text_color='red')
    logo_label = customtkinter.CTkLabel(menu_frame, image=logo_image, text="")
    theme_label = customtkinter.CTkLabel(menu_frame, text="Theme")

    """Theme box"""
    combo_var = customtkinter.StringVar(value="Dark")

    theme = customtkinter.CTkComboBox(menu_frame, values=["Light", "Dark"],
                                         command=theme_mode, state='readonly')
    theme.set("Light")

    """Place widgets and frames"""
    logo_label.grid(row=0, pady=20)
    image_frame.grid(row=4, column=1)
    slider_frame.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
    menu_frame.grid(row=0, column=0, sticky='ns', rowspan=8)
    menu_frame.grid_rowconfigure(2, weight=1)
    menu_frame.grid_columnconfigure(2, weight=1)
    textbox_recipe_frame.grid(padx=5, pady=5)
    textbox_step_frame.grid(padx=5, pady=5)
    button_submit1.grid(row=2, column=1, padx=20, pady=5, columnspan=2)
    slider_1.grid(row=1, column=2, padx=10, pady=5, columnspan=4)
    slider_text.grid(row=1, column=1, padx=10, pady=10)
    slider_text_arrow.grid(row=1, column=2, padx=0, sticky='w')
    title1.grid(row=0, column=3, padx=5, pady=5)
    textbox_recipe.grid(padx=5, pady=5)
    textbox_directions.grid(padx=5, pady=5)
    tabview.grid(row=5, column=1)
    button_home.grid(row=1, sticky='new')
    button_save.grid(row=2, sticky='new')
    button_exit.grid(row=8, sticky='ew')
    fridge_label.grid(row=4, column=1)
    recipe_label.grid(row=0, column=0, padx=5, pady=5)
    theme.grid(row=6)
    theme_label.grid(row=5)

    """Loop keeps Tkinter open"""
    root.mainloop()
