from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from datetime import datetime
import os
import sys
import json

# Add the parent directory to the Python path to import main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import HabitTracker

# Load settings function baked into the file
def load_settings():
    """
    Load settings from the settings.json file.
    If the file doesn't exist, return default settings.
    """
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        # Default settings if the file doesn't exist
        return {"background_color": "white", "button_color": "blue"}

class AddHabitPage(Screen):
    def __init__(self, **kwargs):
        super(AddHabitPage, self).__init__(**kwargs)
        
        # Initialize HabitTracker
        self.habit_tracker = HabitTracker()
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        self.title = Label(
            text="Add New Habit",
            font_size=dp(24),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Habit Name Input
        self.name_input = TextInput(
            hint_text="Habit Name",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(20), dp(15)]
        )
        
        # Habit Description Input
        self.description_input = TextInput(
            hint_text="Description (optional)",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            padding=[dp(20), dp(15)]
        )
        
        # Frequency Type Spinner
        self.frequency_spinner = Spinner(
            text="Daily",  # Default value
            values=("Daily", "Weekly", "Monthly", "Yearly"),
            size_hint_y=None,
            height=dp(50))
        
        # Frequency Count Input
        self.frequency_count_input = TextInput(
            hint_text="Frequency Count (e.g., 1)",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(20), dp(15)],
            input_type='number'
        )
        
        # Duration Input (in minutes)
        self.duration_input = TextInput(
            hint_text="Duration in minutes (put \"1\" if unsure)",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(20), dp(15)],
            input_type='number'
        )
        
        # Save Button (store as instance attribute)
        self.save_button = Button(
            text="Save Habit",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#2196F3"),
            color=get_color_from_hex("#FFFFFF"),
            on_press=self.save_habit
        )
        
        # Back to Main Menu Button (store as instance attribute)
        self.back_button = Button(
            text="Back to Main Menu",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#757575"),
            color=get_color_from_hex("#FFFFFF"),
            on_press=self.go_back
        )
        
        # Add widgets to layout
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.description_input)
        self.layout.add_widget(self.frequency_spinner)
        self.layout.add_widget(self.frequency_count_input)
        self.layout.add_widget(self.duration_input)
        self.layout.add_widget(self.save_button)
        self.layout.add_widget(self.back_button)
        
        # Add layout to screen
        self.add_widget(self.layout)
    
    def save_habit(self, instance):
        """Save the habit to the database."""
        name = self.name_input.text
        description = self.description_input.text
        frequency_type = self.frequency_spinner.text.lower()  # Convert to lowercase
        frequency_count = self.frequency_count_input.text
        duration_minutes = self.duration_input.text
        
        # Validate inputs
        if not name:
            self.show_error("Please enter a habit name.")
            return
        if not frequency_count.isdigit():
            self.show_error("Frequency count must be a number.")
            return
        if duration_minutes and not duration_minutes.isdigit():
            self.show_error("Duration must be a number.")
            return
        
        # Convert duration to seconds
        duration_seconds = int(duration_minutes) * 60 if duration_minutes else 0
        
        try:
            # Add the habit using HabitTracker
            self.habit_tracker.add_habit(
                name=name,
                frequency_type=frequency_type,
                frequency_count=int(frequency_count),
                duration_seconds=duration_seconds,
                description=description
            )
            
            # Clear inputs
            self.name_input.text = ""
            self.description_input.text = ""
            self.frequency_count_input.text = ""
            self.duration_input.text = ""
            
            # Show success message
            self.show_popup("Success", "Habit added successfully!")
            
            # Find the MyHabitsPage instance in the screen manager and update its habit list
            habits_page = self.manager.get_screen('habits')
            if hasattr(habits_page, 'load_habits'):
                habits_page.load_habits()
        
        except ValueError as e:
            self.show_error(str(e))
    
    def update_colors(self):
        """Update button colors based on settings."""
        settings = load_settings()
        self.save_button.background_color = get_color_from_hex({
            "blue": "#2196F3",
            "green": "#088F8F",
            "pink": "#E91E63",
        }.get(settings["button_color"], "#2196F3"))
        self.back_button.background_color = get_color_from_hex("#757575")  # Keep back button color consistent
    
    def go_back(self, instance):
        """Return to the main menu."""
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'
    
    def show_error(self, message):
        """Show an error message in a popup."""
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_popup(self, title, message):
        """Show a success message in a popup."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        message_label = Label(
            text=message,
            font_size=dp(16)
        )
        
        # Add buttons for navigation options
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        view_habits_button = Button(
            text="View My Habits",
            size_hint_x=0.5,
            background_color=get_color_from_hex("#4CAF50")  # Green
        )
        
        add_another_button = Button(
            text="Add Another",
            size_hint_x=0.5,
            background_color=get_color_from_hex("#2196F3")  # Blue
        )
        
        buttons_layout.add_widget(view_habits_button)
        buttons_layout.add_widget(add_another_button)
        
        content.add_widget(message_label)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, None),
            height=dp(200),
            auto_dismiss=True
        )
        
        # Set button callbacks
        view_habits_button.bind(on_press=lambda btn: self.navigate_to_habits(popup))
        add_another_button.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def navigate_to_habits(self, popup):
        """Navigate to the My Habits page."""
        popup.dismiss()
        self.manager.transition.direction = 'left'
        self.manager.current = 'habits'