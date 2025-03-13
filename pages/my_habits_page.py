from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Line
from kivy.uix.textinput import TextInput
import os
import sys
import json
import webbrowser
from datetime import datetime

# Add the parent directory to the Python path to import main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import HabitTracker

# Load settings function baked into the file
def load_settings():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"background_color": "white", "button_color": "blue"}

class MyHabitsPage(Screen):
    def __init__(self, **kwargs):
        super(MyHabitsPage, self).__init__(**kwargs)
        
        # Initialize HabitTracker
        self.habit_tracker = HabitTracker()
        
        # Path for the daily habits completion JSON file
        self.daily_habits_file = "daily_habits_completion.json"
        
        # Initialize or load the daily habits completion tracking
        self.initialize_daily_habits_tracking()
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        self.title = Label(
            text="My Habits",
            font_size=dp(24),
            color=get_color_from_hex("#212121"),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Scrollable area for habits
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - dp(150)))
        self.habits_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.habits_grid.bind(minimum_height=self.habits_grid.setter('height'))
        
        # Add habits to the grid
        self.load_habits()
        
        # Add the grid to the scroll view
        self.scroll_view.add_widget(self.habits_grid)
        
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
        self.update_colors()
    
    def initialize_daily_habits_tracking(self):
        """Initialize or load the daily habits completion tracking system."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if file exists and if it's for today
        if os.path.exists(self.daily_habits_file):
            try:
                with open(self.daily_habits_file, "r") as file:
                    data = json.load(file)
                    if data.get("date") == today:
                        # File exists and is for today, use it
                        self.completed_habits = data.get("completed_habits", {})
                        print(f"Loaded existing habits completion data for {today}")
                        return
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading daily habits file: {e}")
        
        # If we get here, we need to create a new file for today
        self.completed_habits = {}
        self.save_daily_habits_tracking()
        print(f"Created new habits completion tracking for {today}")
    
    def save_daily_habits_tracking(self):
        """Save the daily habits completion tracking to JSON file."""
        today = datetime.now().strftime("%Y-%m-%d")
        data = {
            "date": today,
            "completed_habits": self.completed_habits
        }
        
        try:
            with open(self.daily_habits_file, "w") as file:
                json.dump(data, file, indent=2)
            print(f"Saved habits completion data for {today}")
        except Exception as e:
            print(f"Error saving daily habits file: {e}")
    
    def get_streak_icon_path(self, streak):
        """Return the appropriate icon path based on streak milestone."""
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons')
        
        if streak >= 21:
            return os.path.join(icons_dir, 'streak_21.png')
        elif streak >= 15:
            return os.path.join(icons_dir, 'streak_15.png')
        elif streak >= 7:
            return os.path.join(icons_dir, 'streak_7.png')
        else:
            return os.path.join(icons_dir, 'streak_1.png')
    
    def format_frequency(self, frequency_type, frequency_count):
        """Format frequency in a more readable way (e.g., '3x daily' instead of 'daily (3 times)')."""
        if frequency_count == 1:
            return frequency_type.capitalize()
        else:
            return f"{frequency_count}x {frequency_type}"
   
    def load_habits(self):
        """Load habits from the database and display them."""
        habits = self.habit_tracker.get_habits()
        
        # Clear existing habits
        self.habits_grid.clear_widgets()
        
        if not habits:
            # Show a message if no habits are found
            no_habits_label = Label(
                text="No habits found. Add a new habit to get started!",
                font_size=dp(16),
                color=get_color_from_hex("#757575"),
                size_hint_y=None,
                height=dp(50)
            )
            self.habits_grid.add_widget(no_habits_label)
        else:
            # Add each habit to the grid
            for habit in habits:
                habit_id = habit['id']
                
                # Check if habit is completed and how many times
                times_completed = self.get_habit_completion_count(habit_id)
                max_completions = habit['frequency_count'] if habit['frequency_type'] == 'daily' else 1
                is_fully_completed = times_completed >= max_completions
                
                # Create a container for the habit
                habit_container = BoxLayout(
                    orientation='vertical',
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(150),
                    padding=dp(10)
                )
                
                # Main content layout (left side info, right side buttons)
                main_content = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(100)
                )
                
                # Left side - info about habit
                info_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=0.7)
                
                # Create a horizontal layout for streak icon and name
                name_row_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(30),
                    spacing=dp(10)  # Add spacing between icon and name
                )
                
                # Add streak icon based on milestone
                streak_icon_path = self.get_streak_icon_path(habit['streak'])
                if os.path.exists(streak_icon_path):
                    streak_icon = Image(
                        source=streak_icon_path,
                        size_hint_x=None,
                        width=dp(24),
                        pos_hint={'center_y': 0.5}  # Center vertically
                    )
                    name_row_layout.add_widget(streak_icon)
                
                # Habit name with strikethrough if fully completed
                name_text = habit['name']
                name_label = Label(
                    text=f"Name: {name_text}",
                    font_size=dp(18),
                    color=get_color_from_hex("#212121" if not is_fully_completed else "#AAAAAA"),
                    size_hint_y=None,
                    height=dp(30),
                    markup=True,
                    halign='left',
                    valign='middle',
                    text_size=(None, dp(30))
                )
                
                # Apply strikethrough if fully completed
                if is_fully_completed:
                    name_label.text = f"Name: [s]{name_text}[/s]"
                
                # Add name label to name row layout
                name_row_layout.add_widget(name_label)
                
                # Habit frequency with updated formatting
                formatted_frequency = self.format_frequency(habit['frequency_type'], habit['frequency_count'])
                frequency_label = Label(
                    text=f"Frequency: {formatted_frequency}",
                    font_size=dp(14),
                    color=get_color_from_hex("#757575"),
                    size_hint_y=None,
                    height=dp(20)
                )
                
                # Habit streak
                streak_label = Label(
                    text=f"Streak: {habit['streak']} days",
                    font_size=dp(14),
                    color=get_color_from_hex("#757575"),
                    size_hint_y=None,
                    height=dp(20)
                )
                
                # Status layout for completion checkmark and count
                status_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None, 
                    height=dp(30)
                )
                
                # Show completion status
                if times_completed > 0:
                    # For habits that can be completed multiple times
                    if max_completions > 1:
                        status_text = f"✓ {times_completed}/{max_completions}"
                    else:
                        status_text = "✓"
                    
                    status_label = Label(
                        text=status_text,
                        font_size=dp(20),
                        color=get_color_from_hex("#4CAF50"),  # Green color
                        size_hint_x=None,
                        width=dp(80) if max_completions > 1 else dp(30)
                    )
                    status_layout.add_widget(status_label)
                
                # Add all components to info_layout
                info_layout.add_widget(name_row_layout)  # Add the combined row with icon and name
                info_layout.add_widget(frequency_label)
                info_layout.add_widget(streak_label)
                info_layout.add_widget(status_layout)
                
                # Right side - buttons
                buttons_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_x=0.3)
                
                # Complete habit button
                completion_available = times_completed < max_completions
                complete_button = Button(
                    text="Do Habit",
                    size_hint_y=0.5,
                    background_color=get_color_from_hex("#4CAF50" if completion_available else "#CCCCCC"),  # Green for available, gray for unavailable
                    color=get_color_from_hex("#FFFFFF"),
                    disabled=not completion_available  # Disable if already fully completed
                )
                # Set button press callback with habit_id
                complete_button.bind(on_press=lambda btn, id=habit_id: self.open_habit_url(id))
                
                # Edit/Delete habit button
                edit_delete_button = Button(
                    text="Edit/Remove",
                    size_hint_y=0.5,
                    background_color=get_color_from_hex("#F44336"),  # Red for "delete"
                    color=get_color_from_hex("#FFFFFF")
                )
                # Set button press callback with habit_id
                edit_delete_button.bind(on_press=lambda btn, id=habit_id: self.show_edit_delete_options(id))
                
                # Add buttons to buttons_layout
                buttons_layout.add_widget(complete_button)
                buttons_layout.add_widget(edit_delete_button)
                
                # Add info_layout and buttons_layout to main_content
                main_content.add_widget(info_layout)
                main_content.add_widget(buttons_layout)
                
                # Add main_content to habit_container
                habit_container.add_widget(main_content)
                
                # Add a separator line
                separator = BoxLayout(size_hint_y=None, height=dp(1))
                with separator.canvas:
                    Color(0.9, 0.9, 0.9)
                    Line(points=[0, 0, Window.width, 0], width=1)
                habit_container.add_widget(separator)
                
                # Add habit_container to habits_grid
                self.habits_grid.add_widget(habit_container) 
    
    def get_habit_completion_count(self, habit_id):
        """Get the number of times a habit has been completed today."""
        habit_id_str = str(habit_id)  # Convert to string to use as dict key
        return self.completed_habits.get(habit_id_str, 0)
    
    def show_edit_delete_options(self, habit_id):
        """Show a popup with edit and delete options."""
        # Get the habit info
        habit = self.habit_tracker.get_habit(habit_id)
        
        if not habit:
            return
        
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        title_label = Label(
            text=f"Options for '{habit['name']}'",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        
        buttons = BoxLayout(orientation='vertical', spacing=dp(10))
        
        edit_button = Button(
            text="Edit Habit",
            background_color=get_color_from_hex("#2196F3"),  # Blue
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None,
            height=dp(50)
        )
        
        delete_button = Button(
            text="Delete Habit",
            background_color=get_color_from_hex("#F44336"),  # Red
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = Button(
            text="Cancel",
            background_color=get_color_from_hex("#9E9E9E"),  # Gray
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None,
            height=dp(50)
        )
        
        buttons.add_widget(edit_button)
        buttons.add_widget(delete_button)
        buttons.add_widget(cancel_button)
        
        content.add_widget(title_label)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Habit Options",
            content=content,
            size_hint=(0.8, None),
            height=dp(250),
            auto_dismiss=True
        )
        
        # Set button callbacks
        edit_button.bind(on_press=lambda btn: self.show_edit_habit_form(habit_id, popup))
        delete_button.bind(on_press=lambda btn: self.confirm_delete_habit(habit_id, popup))
        cancel_button.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def show_edit_habit_form(self, habit_id, parent_popup=None):
        """Show a form to edit habit details."""
        # Dismiss the parent popup if provided
        if parent_popup:
            parent_popup.dismiss()
        
        # Get the current habit details
        habit = self.habit_tracker.get_habit(habit_id)
        
        if not habit:
            return
        
        # Create form layout
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Form fields
        form_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        form_grid.bind(minimum_height=form_grid.setter('height'))
        
        # Name field
        name_label = Label(
            text="Name:",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            halign='right'
        )
        name_input = TextInput(
            text=habit['name'],
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        # Description field
        desc_label = Label(
            text="Description:",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            halign='right'
        )
        desc_input = TextInput(
            text=habit.get('description', ''),
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        
        # Frequency type field
        freq_type_label = Label(
            text="Frequency:",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            halign='right'
        )
        
        freq_type_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(40))
        
        # Create frequency type buttons
        freq_types = ['daily', 'weekly', 'monthly', 'yearly']
        freq_buttons = {}
        
        for freq_type in freq_types:
            freq_buttons[freq_type] = Button(
                text=freq_type.capitalize(),
                background_color=get_color_from_hex("#2196F3" if freq_type == habit['frequency_type'] else "#BBBBBB"),
                color=get_color_from_hex("#FFFFFF")
            )
            freq_type_layout.add_widget(freq_buttons[freq_type])
        
        # Store the currently selected frequency type
        self.selected_freq_type = habit['frequency_type']
        
        # Set up button callbacks for frequency selection
        for freq_type, button in freq_buttons.items():
            button.bind(on_press=lambda btn, ft=freq_type: self.select_frequency(ft, freq_buttons))
        
        # Frequency count field
        freq_count_label = Label(
            text="Count:",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            halign='right'
        )
        freq_count_input = TextInput(
            text=str(habit['frequency_count']),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        # Duration field - CHANGED FROM SECONDS TO MINUTES
        duration_label = Label(
            text="Duration (min):",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            halign='right'
        )
        # Convert seconds to minutes for display
        duration_minutes = int(habit['duration_seconds'] / 60)
        duration_input = TextInput(
            text=str(duration_minutes),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        # Add form fields to grid
        form_grid.add_widget(name_label)
        form_grid.add_widget(name_input)
        form_grid.add_widget(desc_label)
        form_grid.add_widget(desc_input)
        form_grid.add_widget(freq_type_label)
        form_grid.add_widget(freq_type_layout)
        form_grid.add_widget(freq_count_label)
        form_grid.add_widget(freq_count_input)
        form_grid.add_widget(duration_label)
        form_grid.add_widget(duration_input)
        
        # Buttons layout
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        cancel_button = Button(
            text="Cancel",
            background_color=get_color_from_hex("#9E9E9E"),  # Gray
            color=get_color_from_hex("#FFFFFF"),
            size_hint_x=0.5
        )
        
        save_button = Button(
            text="Save Changes",
            background_color=get_color_from_hex("#4CAF50"),  # Green
            color=get_color_from_hex("#FFFFFF"),
            size_hint_x=0.5
        )
        
        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(save_button)
        
        # Add all layouts to main content
        content.add_widget(form_grid)
        content.add_widget(buttons_layout)
        
        # Create and show popup
        popup = Popup(
            title=f"Edit Habit: {habit['name']}",
            content=content,
            size_hint=(0.9, 0.9),
            auto_dismiss=False
        )
        
        # Set button callbacks
        cancel_button.bind(on_press=popup.dismiss)
        save_button.bind(on_press=lambda btn: self.save_edited_habit(
            habit_id,
            popup,
            name_input.text,
            desc_input.text,
            self.selected_freq_type,
            freq_count_input.text,
            duration_input.text,
            habit.get('preferred_times', [])
        ))
        
        popup.open()
    
    def select_frequency(self, freq_type, buttons):
        """Handle frequency type selection in the edit form."""
        self.selected_freq_type = freq_type
        
        # Update button colors
        for ft, button in buttons.items():
            button.background_color = get_color_from_hex("#2196F3" if ft == freq_type else "#BBBBBB")
    
    def save_edited_habit(self, habit_id, popup, name, description, frequency_type, 
                          frequency_count, duration_minutes, preferred_times):
        """Save the edited habit details to the database."""
        try:
            # Validate inputs
            if not name.strip():
                self.show_error_popup("Habit name cannot be empty.")
                return
            
            try:
                frequency_count = int(frequency_count)
                if frequency_count <= 0:
                    self.show_error_popup("Frequency count must be greater than 0.")
                    return
            except ValueError:
                self.show_error_popup("Frequency count must be a valid number.")
                return
            
            try:
                # Convert minutes to seconds for storage
                duration_minutes = int(duration_minutes) if duration_minutes else 0
                if duration_minutes < 0:
                    self.show_error_popup("Duration cannot be negative.")
                    return
                duration_seconds = duration_minutes * 60
            except ValueError:
                self.show_error_popup("Duration must be a valid number.")
                return
            
            # Update the habit in the database
            updated_habit = self.habit_tracker.update_habit(
                habit_id,
                name=name,
                description=description,
                frequency_type=frequency_type,
                frequency_count=frequency_count,
                duration_seconds=duration_seconds,  # Store as seconds in database
                preferred_times=preferred_times
            )
            
            if updated_habit:
                # Refresh the habits display
                self.load_habits()
                
                # Dismiss the popup
                popup.dismiss()
                
                # Show success message
                self.show_info_popup(f"Habit '{name}' updated successfully!")
            else:
                self.show_error_popup("Failed to update habit.")
        except Exception as e:
            self.show_error_popup(f"Error updating habit: {e}")
    
    def confirm_delete_habit(self, habit_id, parent_popup=None):
        """Show a confirmation popup before deleting a habit."""
        # Dismiss the parent popup if provided
        if parent_popup:
            parent_popup.dismiss()
        
        # Get the habit info for the popup message
        habit = self.habit_tracker.get_habit(habit_id)
        
        if not habit:
            return
        
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        message = Label(
            text=f"Are you sure you want to delete the habit '{habit['name']}'?\n\nThis action cannot be undone.",
            font_size=dp(16)
        )
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        cancel_button = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_color=get_color_from_hex("#9E9E9E")  # Gray
        )
        
        confirm_button = Button(
            text="Delete",
            size_hint_x=0.5,
            background_color=get_color_from_hex("#F44336")  # Red
        )
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(confirm_button)
        
        content.add_widget(message)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Confirm Deletion",
            content=content,
            size_hint=(0.8, None),
            height=dp(200),
            auto_dismiss=True
        )
        
        # Set button callbacks
        cancel_button.bind(on_press=popup.dismiss)
        confirm_button.bind(on_press=lambda btn: self.delete_habit(habit_id, popup))
        
        popup.open()
    
    def delete_habit(self, habit_id, popup):
        """Delete a habit from the database."""
        try:
            self.habit_tracker.delete_habit(habit_id)
            print(f"Habit {habit_id} deleted")
            
            # If the habit was marked as completed, remove it from the completed_habits dictionary
            habit_id_str = str(habit_id)
            if habit_id_str in self.completed_habits:
                del self.completed_habits[habit_id_str]
                self.save_daily_habits_tracking()
            
            # Refresh the habits display
            self.load_habits()
            
            # Dismiss the popup
            popup.dismiss()
            
            # Show success message
            self.show_info_popup("Habit deleted successfully!")
        except Exception as e:
            print(f"Error deleting habit: {e}")
            self.show_error_popup(f"Error deleting habit: {e}")
    
    def show_error_popup(self, message):
        """Show an error popup with a message."""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        error_message = Label(
            text=message,
            font_size=dp(16)
        )
        ok_button = Button(
            text="OK",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#F44336")  # Red
        )
        
        content.add_widget(error_message)
        content.add_widget(ok_button)
        
        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.8, None),
            height=dp(200),
            auto_dismiss=True
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_info_popup(self, message):
        """Show an information popup with a message."""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        info_message = Label(
            text=message,
            font_size=dp(16)
        )
        ok_button = Button(
            text="OK",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#4CAF50")  # Green
        )
        
        content.add_widget(info_message)
        content.add_widget(ok_button)
        
        popup = Popup(
            title="Information",
            content=content,
            size_hint=(0.8, None),
            height=dp(200),
            auto_dismiss=True
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def open_habit_url(self, habit_id):
        """Generate a URL with habit information and open it."""
        # Get habit information from database
        habit = self.habit_tracker.get_habit(habit_id)
        
        if not habit:
            self.show_error_popup(f"Could not find habit with ID: {habit_id}")
            return
        
        # Get user email
        username = HabitTracker.get_current_user(self)  
        
        # Extract relevant information
        duration_seconds = habit.get('duration_seconds', 0)
        streak = habit.get('streak', 0)
        
        # Build URL with query parameters
        url = f"https://radicool.club/habit-tracker-page?username={username}&duration_seconds={duration_seconds}&streak={streak}"
        
        # Add bonus codes if available
        bonus_codes = self.habit_tracker.get_bonus_codes(include_used=False)
        if bonus_codes:
            # Take the first unused bonus code as an example
            # You might want to implement a selection mechanism
            bonus_code = bonus_codes[0]['code']
            url += f"&bonus_code={bonus_code}"
        
        print(f"Opening URL for ads: {url}")
        
        webbrowser.open(url)
        
        
        # For demo purposes, immediately simulate a verification response
        self.simulate_verification_response(habit_id, None) 

    def simulate_verification_response(self, habit_id, hash_code=None):
        print(f"Habit ID: {habit_id}")

        habit_id_str = str(habit_id)
        habit = self.habit_tracker.get_habit(habit_id)

        if not habit:
            self.show_error_popup(f"Could not find habit with ID: {habit_id}")
            return

        # Get current completion count
        current_completions = self.completed_habits.get(habit_id_str, 0)
        max_completions = habit["frequency_count"] if habit["frequency_type"] == "daily" else 1

        # Check if the habit can still be completed
        if current_completions < max_completions:
            try:
                # Record the completion in the database
                updated_habit = self.habit_tracker.record_completion(habit_id)
                
                # Update the local completion count
                self.completed_habits[habit_id_str] = current_completions + 1
                self.save_daily_habits_tracking()
                
                # Refresh the UI to reflect changes
                self.load_habits()
                
                print(f"Habit {habit_id} marked as completed ({self.completed_habits[habit_id_str]}/{max_completions} times today).")
                print(f"Updated habit: {updated_habit}")
            except Exception as e:
                self.show_error_popup(f"Error recording habit completion: {e}")
        else:
            print(f"Habit {habit_id} has already been completed the maximum allowed times today.")
    def mark_habit_completed(self, habit_id):
        """Mark a habit as completed in the JSON file if allowed."""
        habit_id_str = str(habit_id)

        # Get habit details
        habit = self.habit_tracker.get_habit(habit_id)
        if not habit:
            print(f"Error: Habit ID {habit_id} not found.")
            return
        
        # Check if the habit allows multiple completions per day
        max_completions = habit["frequency_count"] if habit["frequency_type"] == "daily" else 1
        current_completions = self.completed_habits.get(habit_id_str, 0)

        if current_completions < max_completions:
            self.completed_habits[habit_id_str] = current_completions + 1
            self.save_daily_habits_tracking()
            self.load_habits()  # Refresh the UI
        else:
            print(f"Habit {habit_id} has already been completed today.")

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
