import sys
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QTimer


class RewardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kid Quest - Reward Tracker")
        self.setGeometry(300, 300, 400, 300)
        
        # Timer state
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        self.last_minute_mark = 0  # Track when we last decremented the server reward
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # 1 second
        
        # LED pulse timer
        self.led_timer = QTimer()
        self.led_timer.timeout.connect(self.turn_off_led)
        self.led_timer.setSingleShot(True)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # LED indicator (small circular indicator)
        self.led_indicator = QLabel("●")
        self.led_indicator.setAlignment(Qt.AlignCenter)
        self.led_indicator.setFixedSize(30, 30)
        self.led_indicator.setStyleSheet("font-size: 20px; color: #666666; border-radius: 15px; background-color: #f0f0f0;")
        layout.addWidget(self.led_indicator)
        
        # Timer display (prominent)
        self.timer_label = QLabel("000:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 48px; font-weight: bold; padding: 20px; color: #2E8B57;")
        layout.addWidget(self.timer_label)
        
        # Start/Pause button
        self.start_pause_button = QPushButton("Start")
        self.start_pause_button.clicked.connect(self.toggle_timer)
        self.start_pause_button.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.start_pause_button)
        
        # Reward display label (smaller now)
        self.reward_label = QLabel("Current Reward: Loading...")
        self.reward_label.setAlignment(Qt.AlignCenter)
        self.reward_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.reward_label)
        
        # Refresh button
        self.refresh_button = QPushButton("Get New Reward")
        self.refresh_button.clicked.connect(self.fetch_reward)
        layout.addWidget(self.refresh_button)
        
        # Load initial reward value
        self.fetch_reward()
    
    def fetch_reward(self):
        try:
            response = requests.get("http://127.0.0.1:8000/reward")
            response.raise_for_status()
            
            reward_data = response.json()
            
            # Debug: print the response to understand the format
            print(f"API Response: {reward_data}")
            
            # Extract minutes from response
            if isinstance(reward_data, (int, float)):
                minutes = int(reward_data)
            elif isinstance(reward_data, dict):
                # Try common dictionary keys
                if 'value' in reward_data:
                    minutes = int(reward_data['value'])
                elif 'reward' in reward_data:
                    minutes = int(reward_data['reward'])
                elif 'minutes' in reward_data:
                    minutes = int(reward_data['minutes'])
                else:
                    # Take the first numeric value found
                    for key, value in reward_data.items():
                        try:
                            minutes = int(value)
                            break
                        except (ValueError, TypeError):
                            continue
                    else:
                        minutes = 0
            else:
                try:
                    minutes = int(reward_data)
                except (ValueError, TypeError):
                    minutes = 0
            
            # Reset timer with new reward value
            self.total_seconds = minutes * 60
            self.remaining_seconds = self.total_seconds
            self.is_running = False
            self.timer.stop()
            self.last_minute_mark = minutes  # Reset minute tracking
            
            # Update UI
            self.reward_label.setText(f"Current Reward: {minutes} minutes")
            self.start_pause_button.setText("Start")
            self.update_timer_display()
            
        except requests.exceptions.ConnectionError:
            self.reward_label.setText("Error: Could not connect to server")
            QMessageBox.warning(self, "Connection Error", "Could not connect to the API server at http://127.0.0.1:8000")
        except requests.exceptions.RequestException as e:
            self.reward_label.setText("Error: Failed to fetch reward")
            QMessageBox.warning(self, "Request Error", f"Failed to fetch reward: {str(e)}")
        except Exception as e:
            self.reward_label.setText("Error: Unexpected error")
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
    
    def toggle_timer(self):
        if self.remaining_seconds <= 0:
            return
            
        if self.is_running:
            # Pause the timer
            self.timer.stop()
            self.is_running = False
            self.start_pause_button.setText("Start")
        else:
            # Start the timer
            self.timer.start()
            self.is_running = True
            self.start_pause_button.setText("Pause")
    
    def update_timer(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            
            # Check if we've crossed a minute boundary
            # Round UP to nearest minute (4:58 becomes 5 minutes)
            current_minutes_rounded = (self.remaining_seconds + 59) // 60  # This rounds up
            if current_minutes_rounded < self.last_minute_mark:
                self.last_minute_mark = current_minutes_rounded
                self.update_server_reward(current_minutes_rounded)
            
            self.update_timer_display()
        else:
            # Timer finished
            self.timer.stop()
            self.is_running = False
            self.start_pause_button.setText("Start")
            self.update_timer_display()  # This will show 00:00
    
    def update_timer_display(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        time_text = f"{minutes:03d}:{seconds:02d}"  # 3 digits for minutes, 2 for seconds
        self.timer_label.setText(time_text)
        
        # Change color based on remaining time
        if self.remaining_seconds > 60:
            color = "#2E8B57"  # Green
        elif self.remaining_seconds > 30:
            color = "#FF8C00"  # Orange
        else:
            color = "#FF6B6B"  # Red
            
        self.timer_label.setStyleSheet(f"font-size: 48px; font-weight: bold; padding: 20px; color: {color};")
    
    def pulse_led(self):
        """Pulse the LED green for 1 second to indicate server update"""
        self.led_indicator.setStyleSheet("font-size: 20px; color: #00FF00; border-radius: 15px; background-color: #90EE90;")
        self.led_timer.start(1000)  # Turn off after 1 second
    
    def turn_off_led(self):
        """Turn LED back to default gray state"""
        self.led_indicator.setStyleSheet("font-size: 20px; color: #666666; border-radius: 15px; background-color: #f0f0f0;")
    
    def update_server_reward(self, new_value):
        """Update the reward value on the server and pulse the LED"""
        try:
            response = requests.put(f"http://127.0.0.1:8000/reward?new_value={new_value}")
            response.raise_for_status()
            
            # Success - pulse the LED green
            self.pulse_led()
            print(f"Updated server reward to: {new_value}")
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to update server reward: {e}")
            # Could add a red LED pulse for errors, but keeping it simple for now


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RewardApp()
    window.show()
    sys.exit(app.exec())
