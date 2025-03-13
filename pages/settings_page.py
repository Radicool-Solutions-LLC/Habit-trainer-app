from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
import json

class SettingsPage(Screen):
    def __init__(self, **kwargs):
        super(SettingsPage, self).__init__(**kwargs)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Main layout wrapped in a ScrollView
        self.scroll_view = ScrollView(
            size_hint=(1, None), 
            size=(Window.width, Window.height),
            bar_width=dp(10),  # Set the width of the scrollbar
            bar_color=get_color_from_hex("#757575"),  # Set the color of the scrollbar
            bar_inactive_color=get_color_from_hex("#BDBDBD")  # Set the color when the scrollbar is inactive
        )
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))  # Allow vertical scrolling
        
        # Title
        title = Label(
            text="Settings",
            font_size=dp(24),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(50)
        )
        self.layout.add_widget(title)
        
        # Placeholder Settings
        self.add_placeholder_settings()
        
        # Colors Section Header
        colors_header = Label(
            text="Colors",
            font_size=dp(20),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(40)
        )
        self.layout.add_widget(colors_header)
        
        # Background Color Settings
        background_color_label = Label(
            text="Background",
            font_size=dp(16),
            color=get_color_from_hex("#757575"),
            size_hint_y=None,
            height=dp(30)
        )
        self.layout.add_widget(background_color_label)
        
        self.background_color_spinner = Spinner(
            text=self.settings["background_color"].capitalize(),
            values=("White", "Gray", "Black", "Dark Gray"),
            size_hint_y=None,
            height=dp(50))
        self.background_color_spinner.bind(text=self.change_background_color)
        self.layout.add_widget(self.background_color_spinner)
        
        # Button Color Settings
        button_color_label = Label(
            text="Buttons",
            font_size=dp(16),
            color=get_color_from_hex("#757575"),
            size_hint_y=None,
            height=dp(30)
        )
        self.layout.add_widget(button_color_label)
        
        self.button_color_spinner = Spinner(
            text=self.settings["button_color"].capitalize(),
            values=("Blue", "Green", "Pink"),
            size_hint_y=None,
            height=dp(50))
        self.button_color_spinner.bind(text=self.change_button_color)
        self.layout.add_widget(self.button_color_spinner)
        
        # Save Button
        save_button = Button(
            text="Save Settings",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex({
                "blue": "#2196F3",
                "green": "#088F8F",
                "pink": "#E91E63",
            }.get(self.settings["button_color"], "#2196F3")),
            color=get_color_from_hex("#FFFFFF"),
            on_press=self.save_settings
        )
        self.layout.add_widget(save_button)
        
        # Back button
        back_button = Button(
            text="Back to Main Menu",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex({
                "blue": "#2196F3",
                "green": "#088F8F",
                "pink": "#E91E63",
            }.get(self.settings["button_color"], "#2196F3")),
            color=get_color_from_hex("#FFFFFF"),
            on_press=self.go_back
        )
        self.layout.add_widget(back_button)
        
        # Add the layout to the ScrollView
        self.scroll_view.add_widget(self.layout)
        
        # Add the ScrollView to the screen
        self.add_widget(self.scroll_view)
    
    def add_placeholder_settings(self):
        """Add placeholder settings for Create PIN, Update Account, Enable 2FA, and Enable Login on Homescreen."""
        # Create PIN
        create_pin_button = Button(
            text="Create PIN (Coming Soon)",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#757575"),
            color=get_color_from_hex("#FFFFFF"),
            disabled=True  # Disabled for now
        )
        self.layout.add_widget(create_pin_button)
        
        # Update Account
        update_account_button = Button(
            text="Update Account (Coming Soon)",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#757575"),
            color=get_color_from_hex("#FFFFFF"),
            disabled=True  # Disabled for now
        )
        self.layout.add_widget(update_account_button)
        
        # Enable 2FA
        enable_2fa_button = Button(
            text="Enable 2FA (Coming Soon)",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#757575"),
            color=get_color_from_hex("#FFFFFF"),
            disabled=True  # Disabled for now
        )
        self.layout.add_widget(enable_2fa_button)
        
        # Enable Login on Homescreen
        enable_login_button = Button(
            text="Enable Login on Homescreen (Coming Soon)",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#757575"),
            color=get_color_from_hex("#FFFFFF"),
            disabled=True  # Disabled for now
        )
        self.layout.add_widget(enable_login_button)
    
    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"background_color": "white", "button_color": "blue"}
    
    def save_settings(self, instance):
        self.settings["background_color"] = self.background_color_spinner.text.lower()
        self.settings["button_color"] = self.button_color_spinner.text.lower()
        with open("settings.json", "w") as file:
            json.dump(self.settings, file)
        self.show_popup("Success", "Settings saved successfully!")
        
        # Update the app's colors immediately
        self.update_app_colors()
    
    def change_background_color(self, instance, value):
        color_map = {
            "White": "#FFFFFF",
            "Gray": "#CCCCCC",
            "Black": "#000000",
            "Dark Gray": "#666666"
        }
        Window.clearcolor = get_color_from_hex(color_map.get(value, "#FFFFFF"))
    
    def change_button_color(self, instance, value):
        color_map = {
            "Blue": "#2196F3",
            "Green": "#088F8F",
            "Pink": "#E91E63",
        }
        self.settings["button_color"] = value.lower()
        for child in self.layout.children:
            if isinstance(child, Button):
                child.background_color = get_color_from_hex(color_map.get(value, "#2196F3"))
    
    def update_app_colors(self):
        """Update colors across all screens."""
        for screen in self.manager.screens:
            if hasattr(screen, 'update_colors'):
                screen.update_colors()
    
    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()