import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                               QLineEdit, QListWidget, QListWidgetItem, QInputDialog, 
                               QMessageBox, QFileDialog, QApplication, QDialog, QFormLayout,
                               QRadioButton, QButtonGroup, QDialogButtonBox, QScrollArea,
                               QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase

class FoodInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Food Item")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        form_layout.addRow("Food Name:", self.name_input)

        self.per_100g_radio = QRadioButton("Per 100g")
        self.per_item_radio = QRadioButton("Per Item")
        self.per_100g_radio.setChecked(True)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.per_100g_radio)
        radio_layout.addWidget(self.per_item_radio)
        form_layout.addRow("Input Type:", radio_layout)

        self.calories_input = QLineEdit()
        form_layout.addRow("Calories:", self.calories_input)

        self.protein_input = QLineEdit()
        form_layout.addRow("Protein (g):", self.protein_input)

        self.fat_input = QLineEdit()
        form_layout.addRow("Fat (g):", self.fat_input)

        self.carbs_input = QLineEdit()
        form_layout.addRow("Carbs (g):", self.carbs_input)

        self.quantity_input = QLineEdit()
        self.quantity_label = QLabel("Grams:")
        form_layout.addRow(self.quantity_label, self.quantity_input)

        layout.addLayout(form_layout)

        self.per_100g_radio.toggled.connect(self.update_quantity_label)
        self.per_item_radio.toggled.connect(self.update_quantity_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_quantity_label(self):
        if self.per_100g_radio.isChecked():
            self.quantity_label.setText("Grams:")
        else:
            self.quantity_label.setText("Number of Items:")

    def get_values(self):
        return {
            "name": self.name_input.text(),
            "per_100g": self.per_100g_radio.isChecked(),
            "calories": float(self.calories_input.text() or 0),
            "protein": float(self.protein_input.text() or 0),
            "fat": float(self.fat_input.text() or 0),
            "carbs": float(self.carbs_input.text() or 0),
            "quantity": float(self.quantity_input.text() or 0)
        }

class MacroCalculator(QWidget):
    def __init__(self, user_folder):
        super().__init__()
        self.user_folder = user_folder
        self.settings = self.load_settings()
        self.food_items = self.load_food_items()
        self.setup_ui()
        self.load_user_settings()
        self.update_food_list()
        if self.settings:  # Only calculate BMR if settings are available
            self.initial_bmr_calculation()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Set Orbitron font
        font_id = QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "font", "Orbitron", "Orbitron-VariableFont_wght.ttf"))
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"
        self.setFont(QFont(font_family, 10))

        # BMR Calculator
        bmr_group = QGroupBox("BMR Calculator")
        bmr_layout = QFormLayout()

        self.age_input = QSpinBox()
        self.age_input.setRange(15, 80)
        self.age_input.setValue(30)
        self.age_input.setToolTip("Enter your age (15-80 years)")
        bmr_layout.addRow("Age:", self.age_input)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female"])
        self.gender_input.setToolTip("Select your biological sex")
        bmr_layout.addRow("Gender:", self.gender_input)

        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(0, 300)
        self.height_input.setValue(180)
        self.height_input.setDecimals(2)
        self.height_unit = QComboBox()
        self.height_unit.addItems(["cm", "inches", "ft/in"])
        self.height_unit.currentTextChanged.connect(self.update_height_input)
        self.height_input.setToolTip("Enter your height (e.g., 180 cm, 70.87 inches, or 5'11\")")
        
        self.height_feet = QSpinBox()
        self.height_feet.setRange(0, 9)
        self.height_feet.setValue(5)
        self.height_feet.setToolTip("Feet")
        self.height_feet.hide()
        
        self.height_inches = QDoubleSpinBox()
        self.height_inches.setRange(0, 11.99)
        self.height_inches.setValue(11)
        self.height_inches.setDecimals(2)
        self.height_inches.setToolTip("Inches")
        self.height_inches.hide()
        
        height_layout = QHBoxLayout()
        height_layout.addWidget(self.height_input)
        height_layout.addWidget(self.height_feet)
        height_layout.addWidget(self.height_inches)
        height_layout.addWidget(self.height_unit)
        bmr_layout.addRow("Height:", height_layout)

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 500)
        self.weight_input.setValue(70)
        self.weight_input.setDecimals(2)
        self.weight_unit = QComboBox()
        self.weight_unit.addItems(["kg", "lbs"])
        self.weight_input.setToolTip("Enter your weight (e.g., 70 kg or 154.32 lbs)")
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(self.weight_input)
        weight_layout.addWidget(self.weight_unit)
        bmr_layout.addRow("Weight:", weight_layout)

        self.body_fat_input = QDoubleSpinBox()
        self.body_fat_input.setRange(0, 100)
        self.body_fat_input.setValue(15)
        self.body_fat_input.setSuffix("%")
        self.body_fat_input.setToolTip("Enter your body fat percentage (required for Katch-McArdle formula)")
        bmr_layout.addRow("Body Fat %:", self.body_fat_input)

        self.bmr_formula = QComboBox()
        self.bmr_formula.addItems([
            "Mifflin-St Jeor (1990)",
            "Harris-Benedict (1919, revised 1984)",
            "Katch-McArdle (1996)"
        ])
        self.bmr_formula.setToolTip("Select the BMR calculation formula")
        bmr_layout.addRow("BMR Formula:", self.bmr_formula)

        self.bmr_result = QLabel("BMR: Not calculated")
        bmr_layout.addRow(self.bmr_result)

        self.calories_burned = QDoubleSpinBox()
        self.calories_burned.setRange(0, 10000)
        self.calories_burned.setValue(1000)
        self.calories_burned.setToolTip("Enter the total calories burned through exercise per week")
        bmr_layout.addRow("Calories Burned Via Exercise Per Week:", self.calories_burned)

        calculate_bmr_button = QPushButton("Calculate BMR")
        calculate_bmr_button.clicked.connect(self.calculate_bmr)
        bmr_layout.addRow(calculate_bmr_button)

        bmr_group.setLayout(bmr_layout)
        layout.addWidget(bmr_group)

        # Food list
        food_group = QGroupBox("Food Items")
        food_layout = QVBoxLayout()

        self.food_list = QListWidget()
        self.food_list.setMaximumHeight(200)
        food_layout.addWidget(self.food_list)

        button_layout = QHBoxLayout()
        add_food_button = QPushButton("Add Food Item")
        add_food_button.clicked.connect(self.add_food_item)
        remove_food_button = QPushButton("Remove Food Item")
        remove_food_button.clicked.connect(self.remove_food_item)
        edit_food_button = QPushButton("Edit Food Item")
        edit_food_button.clicked.connect(self.edit_food_item)
        
        button_layout.addWidget(add_food_button)
        button_layout.addWidget(remove_food_button)
        button_layout.addWidget(edit_food_button)
        food_layout.addLayout(button_layout)

        food_group.setLayout(food_layout)
        layout.addWidget(food_group)

        # Totals
        totals_group = QGroupBox("Nutrition Totals")
        totals_layout = QHBoxLayout()
        self.calories_label = QLabel("Calories: 0")
        self.protein_label = QLabel("Protein: 0g")
        self.fat_label = QLabel("Fat: 0g")
        self.carbs_label = QLabel("Carbs: 0g")
        totals_layout.addWidget(self.calories_label)
        totals_layout.addWidget(self.protein_label)
        totals_layout.addWidget(self.fat_label)
        totals_layout.addWidget(self.carbs_label)
        totals_group.setLayout(totals_layout)
        layout.addWidget(totals_group)

        # Net Gain/Loss
        self.net_result = QLabel("Net Gain/Loss: 0 Calories/day")
        layout.addWidget(self.net_result)

        # Buttons
        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        save_button = QPushButton("Save to File")
        save_button.clicked.connect(self.save_to_file)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

        self.load_user_settings()
        self.update_food_list()

    def load_settings(self):
        settings_path = os.path.join(self.user_folder, "macro_calculator_settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        settings = {
            "age": self.age_input.value(),
            "gender": self.gender_input.currentText(),
            "height": self.height_input.value(),
            "height_unit": self.height_unit.currentText(),
            "height_feet": self.height_feet.value(),
            "height_inches": self.height_inches.value(),
            "weight": self.weight_input.value(),
            "weight_unit": self.weight_unit.currentText(),
            "body_fat": self.body_fat_input.value(),
            "bmr_formula": self.bmr_formula.currentText(),
            "calories_burned": self.calories_burned.value()
        }
        settings_path = os.path.join(self.user_folder, "macro_calculator_settings.json")
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def load_user_settings(self):
        if self.settings:
            self.age_input.setValue(self.settings.get("age", 30))
            self.gender_input.setCurrentText(self.settings.get("gender", "Male"))
            self.height_input.setValue(self.settings.get("height", 180))
            self.height_unit.setCurrentText(self.settings.get("height_unit", "cm"))
            self.height_feet.setValue(self.settings.get("height_feet", 5))
            self.height_inches.setValue(self.settings.get("height_inches", 11))
            self.weight_input.setValue(self.settings.get("weight", 70))
            self.weight_unit.setCurrentText(self.settings.get("weight_unit", "kg"))
            self.body_fat_input.setValue(self.settings.get("body_fat", 15))
            self.bmr_formula.setCurrentText(self.settings.get("bmr_formula", "Mifflin-St Jeor (1990)"))
            self.calories_burned.setValue(self.settings.get("calories_burned", 1000))
        
        self.update_height_input()

    def remove_food_item(self):
        current_item = self.food_list.currentItem()
        if current_item:
            item_name = current_item.text().split(" - ")[0]
            self.food_items.pop(item_name, None)
            self.save_food_items()
            self.update_food_list()

    def edit_food_item(self):
        current_item = self.food_list.currentItem()
        if current_item:
            item_name = current_item.text().split(" - ")[0]
            item_data = self.food_items[item_name]
            
            dialog = FoodInputDialog(self)
            dialog.name_input.setText(item_name)
            dialog.calories_input.setText(str(item_data["calories"] / item_data["quantity"] * (100 if item_data["per_100g"] else 1)))
            dialog.protein_input.setText(str(item_data["protein"] / item_data["quantity"] * (100 if item_data["per_100g"] else 1)))
            dialog.fat_input.setText(str(item_data["fat"] / item_data["quantity"] * (100 if item_data["per_100g"] else 1)))
            dialog.carbs_input.setText(str(item_data["carbs"] / item_data["quantity"] * (100 if item_data["per_100g"] else 1)))
            dialog.quantity_input.setText(str(item_data["quantity"]))
            dialog.per_100g_radio.setChecked(item_data["per_100g"])
            dialog.per_item_radio.setChecked(not item_data["per_100g"])
            
            if dialog.exec_():
                values = dialog.get_values()
                self.food_items.pop(item_name, None)  # Remove old item
                if values["per_100g"]:
                    factor = values["quantity"] / 100
                else:
                    factor = values["quantity"]
                self.food_items[values["name"]] = {
                    "calories": values["calories"] * factor,
                    "protein": values["protein"] * factor,
                    "fat": values["fat"] * factor,
                    "carbs": values["carbs"] * factor,
                    "quantity": values["quantity"],
                    "per_100g": values["per_100g"]
                }
                self.save_food_items()
                self.update_food_list()

    def update_height_input(self):
        unit = self.height_unit.currentText()
        if unit == "ft/in":
            self.height_input.hide()
            self.height_feet.show()
            self.height_inches.show()
        else:
            self.height_input.show()
            self.height_feet.hide()
            self.height_inches.hide()

    def load_food_items(self):
        file_path = os.path.join(self.user_folder, "macro_calculator_items.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def save_food_items(self):
        file_path = os.path.join(self.user_folder, "macro_calculator_items.json")
        with open(file_path, 'w') as f:
            json.dump(self.food_items, f, indent=4)

    def update_food_list(self):
        self.food_list.clear()
        for name, data in self.food_items.items():
            item = QListWidgetItem(f"{name} - {data['quantity']} {'g' if data['per_100g'] else 'items'}")
            self.food_list.addItem(item)
        self.calculate_totals()

    def add_food_item(self):
        dialog = FoodInputDialog(self)
        if dialog.exec_():
            values = dialog.get_values()
            name = values["name"]
            if name:
                if values["per_100g"]:
                    factor = values["quantity"] / 100
                else:
                    factor = values["quantity"]
                self.food_items[name] = {
                    "calories": values["calories"] * factor,
                    "protein": values["protein"] * factor,
                    "fat": values["fat"] * factor,
                    "carbs": values["carbs"] * factor,
                    "quantity": values["quantity"],
                    "per_100g": values["per_100g"]
                }
                self.save_food_items()
                self.update_food_list()

    def calculate_totals(self):
        total_calories = total_protein = total_fat = total_carbs = 0
        for data in self.food_items.values():
            total_calories += data['calories']
            total_protein += data['protein']
            total_fat += data['fat']
            total_carbs += data['carbs']

        self.calories_label.setText(f"Calories: {total_calories:.1f}")
        self.protein_label.setText(f"Protein: {total_protein:.1f}g")
        self.fat_label.setText(f"Fat: {total_fat:.1f}g")
        self.carbs_label.setText(f"Carbs: {total_carbs:.1f}g")

        self.calculate_net_gain_loss(total_calories)

    def calculate_bmr(self):
        age = self.age_input.value()
        gender = self.gender_input.currentText()
        weight = self.weight_input.value()
        body_fat = self.body_fat_input.value() / 100

        # Handle height based on the selected unit
        height_unit = self.height_unit.currentText()
        if height_unit == "cm":
            height = self.height_input.value()
        elif height_unit == "inches":
            height = self.height_input.value() * 2.54  # Convert inches to cm
        else:  # ft/in
            feet = self.height_feet.value()
            inches = self.height_inches.value()
            height = (feet * 12 + inches) * 2.54  # Convert to cm

        if self.weight_unit.currentText() == "lbs":
            weight *= 0.453592  # Convert lbs to kg

        formula = self.bmr_formula.currentText().split(" (")[0]  # Get just the formula name

        if formula == "Mifflin-St Jeor":
            if gender == "Male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
        elif formula == "Harris-Benedict":
            if gender == "Male":
                bmr = 13.397 * weight + 4.799 * height - 5.677 * age + 88.362
            else:
                bmr = 9.247 * weight + 3.098 * height - 4.330 * age + 447.593
        else:  # Katch-McArdle
            lean_body_mass = weight * (1 - body_fat)
            bmr = 370 + 21.6 * lean_body_mass

        self.bmr_result.setText(f"BMR: {bmr:.0f} Calories/day")
        self.calculate_net_gain_loss(self.calculate_total_calories())
        self.save_settings()  # Save settings after BMR calculation

    def initial_bmr_calculation(self):
            age = self.age_input.value()
            gender = self.gender_input.currentText()
            weight = self.weight_input.value()
            body_fat = self.body_fat_input.value() / 100

            # Handle height based on the selected unit
            height_unit = self.height_unit.currentText()
            if height_unit == "cm":
                height = self.height_input.value()
            elif height_unit == "inches":
                height = self.height_input.value() * 2.54  # Convert inches to cm
            else:  # ft/in
                feet = self.height_feet.value()
                inches = self.height_inches.value()
                height = (feet * 12 + inches) * 2.54  # Convert to cm

            if self.weight_unit.currentText() == "lbs":
                weight *= 0.453592  # Convert lbs to kg

            formula = self.bmr_formula.currentText().split(" (")[0]  # Get just the formula name

            if formula == "Mifflin-St Jeor":
                if gender == "Male":
                    bmr = 10 * weight + 6.25 * height - 5 * age + 5
                else:
                    bmr = 10 * weight + 6.25 * height - 5 * age - 161
            elif formula == "Harris-Benedict":
                if gender == "Male":
                    bmr = 13.397 * weight + 4.799 * height - 5.677 * age + 88.362
                else:
                    bmr = 9.247 * weight + 3.098 * height - 4.330 * age + 447.593
            else:  # Katch-McArdle
                lean_body_mass = weight * (1 - body_fat)
                bmr = 370 + 21.6 * lean_body_mass

            self.bmr_result.setText(f"BMR: {bmr:.0f} Calories/day")
            self.calculate_net_gain_loss(self.calculate_total_calories())

    def calculate_total_calories(self):
        return sum(data['calories'] for data in self.food_items.values())

    def calculate_net_gain_loss(self, total_calories):
        try:
            bmr = float(self.bmr_result.text().split(":")[1].split()[0])
        except (IndexError, ValueError):
            bmr = 0  # Set BMR to 0 if it hasn't been calculated yet
        
        calories_burned = self.calories_burned.value() / 7  # Convert weekly to daily
        net = total_calories - bmr - calories_burned
        self.net_result.setText(f"Net Gain/Loss: {net:.0f} Calories/day")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        text = self.get_output_text()
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "Totals and food items copied to clipboard!")

    def save_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Totals", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.get_output_text())
            QMessageBox.information(self, "Saved", f"Totals and food items saved to {file_path}")
            os.startfile(os.path.dirname(file_path))

    def get_output_text(self):
        output = "Macro Calculator Results:\n\n"
        output += f"{self.bmr_result.text()}\n"
        output += f"Calories Burned Via Exercise: {self.calories_burned.value():.1f} Calories/week\n\n"
        output += "Daily Intake:\n"
        output += f"{self.calories_label.text()}\n"
        output += f"{self.protein_label.text()}\n"
        output += f"{self.fat_label.text()}\n"
        output += f"{self.carbs_label.text()}\n\n"
        output += f"{self.net_result.text()}\n\n"
        output += "Food Items:\n"
        for name, data in self.food_items.items():
            output += f"{name} - {data['quantity']} {'g' if data['per_100g'] else 'items'}\n"
            output += f"  Calories: {data['calories']:.1f}, "
            output += f"Protein: {data['protein']:.1f}g, "
            output += f"Fat: {data['fat']:.1f}g, "
            output += f"Carbs: {data['carbs']:.1f}g\n"
        return output

def show_macro_calculator(parent, user_folder):
    return MacroCalculator(user_folder)