################################
import os
application_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(application_path)

################################

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.popup import Popup
import json
import webbrowser

from main import HabitTracker

# Load settings from JSON file
def load_settings():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        # If settings.json doesn't exist, create it with default values
        default_settings = {
            "background_color": "white",
            "button_color": "blue"
        }
        with open("settings.json", "w") as file:
            json.dump(default_settings, file)
        return default_settings

# Save settings to JSON file
def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file)

# Load settings
settings = load_settings()

# Set window size and color based on settings
Window.size = (400, 600)
Window.clearcolor = get_color_from_hex({
    "white": "#FFFFFF",
    "gray": "#CCCCCC",
    "black": "#000000",
    "dark gray": "#666666"
}.get(settings["background_color"], "#FFFFFF"))

# Material design button class
class MDButton(Button):
    def __init__(self, **kwargs):
        super(MDButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_color = get_color_from_hex({
            "blue": "#2196F3",
            "green": "#088F8F",
            "pink": "#E91E63",
            
        }.get(settings["button_color"], "#2196F3"))
        self.color = get_color_from_hex("#FFFFFF")
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = dp(16)

# Material Card Button for main menu
class MDCardButton(Button):
    def __init__(self, **kwargs):
        super(MDCardButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_color = get_color_from_hex({
            "blue": "#2196F3",
            "green": "#088F8F",
            "pink": "#E91E63",
            
        }.get(settings["button_color"], "#2196F3"))
        self.color = get_color_from_hex("#FFFFFF")
        self.font_size = dp(18)
        self.size_hint = (1, 1)
        self.height = dp(120)

# Login Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(30))
        
        # Title
        title = Label(
            text="Welcome to Habit Tracker",
            font_size=dp(24),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(50))
        
        # Introduction text
        intro = Label(
            text="Please enter your email to get started",
            font_size=dp(16),
            color=get_color_from_hex("#757575"),
            size_hint_y=None,
            height=dp(50))
        
        # Email input
        self.email_input = TextInput(
            hint_text="Email",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(20), dp(15)])
        
        # Register button
        register_button = MDButton(
            text="Continue",
            on_press=self.register)
        
        # Skip button
        skip_button = MDButton(
            text="Skip",
            on_press=self.show_skip_popup)
        
        # Add widgets to layout
        self.layout.add_widget(title)
        self.layout.add_widget(intro)
        self.layout.add_widget(self.email_input)
        self.layout.add_widget(register_button)
        self.layout.add_widget(skip_button)
        
        # Add a filler to push content up
        self.layout.add_widget(Label(size_hint_y=1))
        
        self.add_widget(self.layout)
    
    def register(self, instance):
        email = self.email_input.text
        
        # Simple email validation
        if "@" in email and "." in email:
            # Open the URL with the email as a query parameter
            webbrowser.open(f"https://radicool.club/habit-tracker-page?username={email}")
            
            # Add the email to the SQLite database
            tracker = HabitTracker()
            tracker.add_account(email)
            
            # Set transition direction and switch screen
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'main'
        else:
            # Show error message (could be improved with a proper dialog)
            if hasattr(self, 'error_label'):
                self.error_label.text = "Please enter a valid email"
            else:
                self.error_label = Label(
                    text="Please enter a valid email",
                    color=get_color_from_hex("#F44336"),
                    size_hint_y=None,
                    height=dp(30))
                self.layout.add_widget(self.error_label, 5)  # Insert at position 5
    
    def show_skip_popup(self, instance):
        # Create a popup with a warning message
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        message = Label(
            text="You won't be able to get paid for your habits if you don't sign up with an email. Are you sure you want to skip?",
            font_size=dp(16),
            color=get_color_from_hex("#212121"))
        continue_button = MDButton(
            text="Continue",
            on_press=self.register)
        skip_button = MDButton(
            text="Skip Anyway",
            on_press=self.skip_signup)
        
        content.add_widget(message)
        content.add_widget(continue_button)
        content.add_widget(skip_button)
        
        self.popup = Popup(
            title="Skip Signup?",
            content=content,
            size_hint=(0.8, 0.5))
        self.popup.open()
    
    def skip_signup(self, instance):
        # Close the popup and proceed to the main screen
        self.popup.dismiss()
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'main'

# Main Menu Screen
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        self.title = Label(
            text="Habit Tracker",
            font_size=dp(28),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(50))
        
        # Grid for menu options (2x2)
        self.grid = GridLayout(cols=2, spacing=dp(15))
        
        # Menu buttons (store them as instance attributes)
        self.habits_button = MDCardButton(
            text="My Habits",
            on_press=lambda x: self.navigate_to('habits'))
        
        self.add_habit_button = MDCardButton(
            text="Add New Habit",
            on_press=lambda x: self.navigate_to('add_habit'))
        
        self.history_button = MDCardButton(
            text="Habit History",
            on_press=lambda x: self.navigate_to('history'))
        
        self.settings_button = MDCardButton(
            text="Settings",
            on_press=lambda x: self.navigate_to('settings'))
        
        # Add buttons to grid
        self.grid.add_widget(self.habits_button)
        self.grid.add_widget(self.add_habit_button)
        self.grid.add_widget(self.history_button)
        self.grid.add_widget(self.settings_button)
        
        # Add widgets to layout
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.grid)
        
        self.add_widget(self.layout)
    
    def update_colors(self):
        """Update button colors based on settings."""
        settings = load_settings()
        for button in [self.habits_button, self.add_habit_button, self.history_button, self.settings_button]:
            button.background_color = get_color_from_hex({
                "blue": "#2196F3",
                "green": "#088F8F",
                "pink": "#E91E63",
            }.get(settings["button_color"], "#2196F3"))
    
    def navigate_to(self, screen_name):
        # Set transition direction for navigating to section screens (left)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = screen_name
    
    def go_back(self, instance):
        # Set transition direction for returning to main menu (right)
        # This creates the effect of swiping in the opposite direction
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

# Habit Tracker App
from pages.add_habit_page import AddHabitPage
from pages.my_habits_page import MyHabitsPage
from pages.habits_history_page import HabitsHistoryPage
from pages.settings_page import SettingsPage

class HabitTrackerApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Always add the MainMenuScreen
        sm.add_widget(MainMenuScreen(name='main'))
        
        # Initialize the HabitTracker to check for existing accounts
        tracker = HabitTracker()
        account_exists = tracker.check_account_exists()
        
        # Check if an account exists
        if not account_exists:
            # No account found, show the login screen
            sm.add_widget(LoginScreen(name='login'))
            sm.current = 'login'  # Set initial screen to login
        else:
            # Account exists, go directly to main menu
            sm.current = 'main'  # Set initial screen to main
        
        # Add the other screens
        sm.add_widget(SettingsPage(name='settings'))
        sm.add_widget(MyHabitsPage(name='habits'))
        sm.add_widget(HabitsHistoryPage(name='history'))
        sm.add_widget(AddHabitPage(name='add_habit'))
        
        return sm

if __name__ == '__main__':
    HabitTrackerApp().run()