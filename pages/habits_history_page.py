from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window  
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

class HabitsHistoryPage(Screen):
    def __init__(self, **kwargs):
        super(HabitsHistoryPage, self).__init__(**kwargs)
        
        # Initialize HabitTracker
        self.habit_tracker = HabitTracker()
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        self.title = Label(
            text="Habit History",
            font_size=dp(24),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Scrollable area for habit history
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - dp(150)))
        self.history_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.history_grid.bind(minimum_height=self.history_grid.setter('height'))
        
        # Load habit history
        self.load_habit_history()
        
        # Add the grid to the scroll view
        self.scroll_view.add_widget(self.history_grid)
        
        # Back button (store as instance attribute)
        self.back_button = Button(
            text="Back to Main Menu",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#2196F3"),
            color=get_color_from_hex("#FFFFFF"),
            on_press=self.go_back
        )
        
        # Add widgets to layout
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.back_button)
        
        # Add layout to screen
        self.add_widget(self.layout)
        
        # Update colors based on settings
        self.update_colors()  # Add this line
    
    def load_habit_history(self):
        """Load habit completion history from the database and display it."""
        # Fetch all habit completions
        completions = self.habit_tracker.get_all_completions()
        
        # Clear existing history
        self.history_grid.clear_widgets()
        
        if not completions:
            # Show a message if no habit history is found
            no_history_label = Label(
                text="No habit history found.",
                font_size=dp(16),
                color=get_color_from_hex("#757575"),
                size_hint_y=None,
                height=dp(50)
            )
            self.history_grid.add_widget(no_history_label)
        else:
            # Add each completion to the grid
            for completion in completions:
                completion_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(100))
                
                # Habit name
                habit = self.habit_tracker.get_habit(completion['habit_id'])
                habit_name = habit['name'] if habit else "Unknown Habit"
                
                name_label = Label(
                    text=f"Habit: {habit_name}",
                    font_size=dp(18),
                    color=get_color_from_hex("#212121"),
                    size_hint_y=None,
                    height=dp(30)
                )
                
                # Completion time
                completion_time = datetime.fromisoformat(completion['completion_time']).strftime("%Y-%m-%d %H:%M:%S")
                time_label = Label(
                    text=f"Completed at: {completion_time}",
                    font_size=dp(14),
                    color=get_color_from_hex("#757575"),
                    size_hint_y=None,
                    height=dp(20)
                )
                
                # Duration (if available)
                duration_label = Label(
                    text=f"Duration: {completion['duration_seconds']} seconds" if completion['duration_seconds'] else "Duration: N/A",
                    font_size=dp(14),
                    color=get_color_from_hex("#757575"),
                    size_hint_y=None,
                    height=dp(20)
                )
                
                # Add labels to completion layout
                completion_layout.add_widget(name_label)
                completion_layout.add_widget(time_label)
                completion_layout.add_widget(duration_label)
                
                # Add completion layout to grid
                self.history_grid.add_widget(completion_layout)
    
    def update_colors(self):
        """Update button colors based on settings."""
        settings = load_settings()
        self.back_button.background_color = get_color_from_hex({
            "blue": "#2196F3",
            "green": "#088F8F",
            "pink": "#E91E63",
        }.get(settings["button_color"], "#2196F3"))
    
    def go_back(self, instance):
        """Return to the main menu."""
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'