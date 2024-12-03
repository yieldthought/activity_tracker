import time
from datetime import datetime
from Quartz.CoreGraphics import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID
)
from pynput import mouse, keyboard
from database import DatabaseHandler
from config import CODING_APPS, TALKING_APPS, IDLE_TIMEOUT, DB_PATH

class ActivityTracker:
    def __init__(self):
        self.db = DatabaseHandler(DB_PATH)
        self.last_activity_time = datetime.now()
        self.last_window = None
        self.current_activity_start = datetime.now()
        self.current_activity_type = None
        
        # Setup activity monitors
        self.mouse_listener = mouse.Listener(on_move=self.on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)
        
    def on_activity(self, *args):
        self.last_activity_time = datetime.now()

    def get_active_window(self):
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        for window in window_list:
            if window.get('kCGWindowLayer', 0) == 0:  # Active window is usually at layer 0
                app_name = window.get('kCGWindowOwnerName', '')
                return app_name
        return None

    def get_activity_type(self, window_name):
        if not window_name:
            return 'other'
        if window_name in CODING_APPS:
            return 'coding'
        if window_name in TALKING_APPS:
            return 'talking'
        return 'other'

    def is_idle(self):
        idle_duration = (datetime.now() - self.last_activity_time).total_seconds()
        return idle_duration > IDLE_TIMEOUT

    def log_current_activity(self):
        if self.current_activity_type:
            end_time = datetime.now()
            self.db.log_activity(
                self.current_activity_type,
                self.current_activity_start,
                end_time
            )
            self.current_activity_start = end_time

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            print("Activity tracking started. Press Ctrl+C to stop.")
            while True:
                current_window = self.get_active_window()
                
                if self.is_idle():
                    new_activity_type = 'idle'
                else:
                    new_activity_type = self.get_activity_type(current_window)

                # Log activity if type changed
                if new_activity_type != self.current_activity_type:
                    self.log_current_activity()
                    self.current_activity_type = new_activity_type

                # Always log current activity to keep stats current
                self.log_current_activity()

                # Update display every second
                summary, total_time = self.db.get_summary()
                if total_time > 0:
                    stats = {
                        'coding': summary.get('coding', 0),
                        'talking': summary.get('talking', 0),
                        'other': summary.get('other', 0),
                        'idle': summary.get('idle', 0)
                    }
                    
                    # Calculate percentages
                    percentages = {k: (v / total_time) * 100 for k, v in stats.items()}
                    
                    # Convert seconds to hours and minutes for display
                    def format_time(seconds):
                        h = seconds // 3600
                        m = (seconds % 3600) // 60
                        return f"{h}h {m}m"

                    print(f"\rCoding: {percentages['coding']:0.1f}% ({format_time(stats['coding'])} - {stats['coding']}s) | "
                          f"Talking: {percentages['talking']:0.1f}% ({format_time(stats['talking'])} - {stats['talking']}s) | "
                          f"Other: {percentages['other']:0.1f}% ({format_time(stats['other'])} - {stats['other']}s) | "
                          f"Idle: {percentages['idle']:0.1f}% ({format_time(stats['idle'])} - {stats['idle']}s)", 
                          end='', flush=True)

                time.sleep(1)  # Check every second

        except KeyboardInterrupt:
            self.log_current_activity()
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            print("\n")  # Add newline after interrupt

    def print_summary(self):
        summary, total_time = self.db.get_summary()
        print("\nToday's Activity Summary:")
        for activity_type, duration in summary.items():
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            percentage = (duration / total_time * 100) if total_time > 0 else 0
            print(f"{activity_type}: {hours}h {minutes}m ({percentage:.1f}%)")

def main():
    tracker = ActivityTracker()
    try:
        print("Activity tracking started. Press Ctrl+C to stop and see summary.")
        tracker.start()
    except KeyboardInterrupt:
        tracker.print_summary()

if __name__ == '__main__':
    main()
