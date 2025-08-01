import sys
import signal
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, QTimer


class RewardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kid Quest - Reward Tracker")
        self.setGeometry(300, 300, 600, 500)
        
        # Timer state
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        self.last_minute_mark = 0  # Track when we last decremented the server reward
        self.internet_status = "off"  # Track current internet state
        
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
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top section with LEDs in upper left (fixed height)
        top_layout = QHBoxLayout()
        
        # LED indicators (left side)
        led_container = QWidget()
        led_container.setFixedHeight(60)  # Fixed height to prevent stretching
        led_widget_layout = QVBoxLayout(led_container)
        
        # First LED with label - Modern square design
        sync_led_layout = QVBoxLayout()
        self.sync_led = QLabel()
        self.sync_led.setFixedSize(16, 16)
        self.sync_led.setStyleSheet("""
            background-color: #666666; 
            border: 2px solid #333333;
            border-radius: 3px;
        """)
        sync_label = QLabel("Sync")
        sync_label.setAlignment(Qt.AlignCenter)
        sync_label.setStyleSheet("font-size: 9px; color: #666666; margin-top: 2px;")
        sync_led_layout.addWidget(self.sync_led)
        sync_led_layout.addWidget(sync_label)
        
        # Second LED with label - Modern square design
        internet_led_layout = QVBoxLayout()
        self.internet_led = QLabel()
        self.internet_led.setFixedSize(16, 16)
        self.internet_led.setStyleSheet("""
            background-color: #FF4444; 
            border: 2px solid #CC0000;
            border-radius: 3px;
        """)  # Red for off
        internet_label = QLabel("Internet")
        internet_label.setAlignment(Qt.AlignCenter)
        internet_label.setStyleSheet("font-size: 9px; color: #666666; margin-top: 2px;")
        internet_led_layout.addWidget(self.internet_led)
        internet_led_layout.addWidget(internet_label)
        
        # Horizontal layout for LEDs
        leds_layout = QHBoxLayout()
        leds_layout.addLayout(sync_led_layout)
        leds_layout.addLayout(internet_led_layout)
        leds_layout.addStretch()  # Push LEDs to the left
        
        led_widget_layout.addLayout(leds_layout)
        led_widget_layout.addStretch()  # Push LEDs to the top
        
        top_layout.addWidget(led_container)
        top_layout.addStretch()  # Fill remaining space
        
        main_layout.addLayout(top_layout)
        
        # Rest of the content
        content_layout = QVBoxLayout()
        
        # Timer display (prominent)
        self.timer_label = QLabel("000:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 72px; 
            font-weight: bold; 
            padding: 30px;
            color: #2E8B57;
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            letter-spacing: 8px;
        """)
        content_layout.addWidget(self.timer_label)
        
        # Start/Pause button
        self.start_pause_button = QPushButton("START")
        self.start_pause_button.clicked.connect(self.toggle_timer)
        self.start_pause_button.setStyleSheet("""
            QPushButton {
                font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                font-size: 20px; 
                font-weight: bold;
                padding: 15px 30px;
                color: #FFFFFF;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #2E7D32);
                border: 2px solid #1B5E20;
                border-radius: 8px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66BB6A, stop:1 #4CAF50);
                border: 2px solid #2E7D32;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2E7D32, stop:1 #1B5E20);
            }
        """)
        content_layout.addWidget(self.start_pause_button)
        
        # Tasks section
        tasks_label = QLabel("Tasks")
        tasks_label.setAlignment(Qt.AlignCenter)
        tasks_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        content_layout.addWidget(tasks_label)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)  # Title, Reward, Status, Action
        self.tasks_table.setHorizontalHeaderLabels(["Title", "Reward", "Status", "Action"])
        
        # Make table scrollable and expandable
        self.tasks_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tasks_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Disable row selection
        self.tasks_table.setSelectionMode(QTableWidget.NoSelection)
        
        # Column sizing
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.setColumnWidth(0, 200)  # Title column wider
        self.tasks_table.setColumnWidth(1, 80)   # Reward column narrow
        self.tasks_table.setColumnWidth(2, 80)   # Status column narrow
        
        # Table styling
        self.tasks_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #CCCCCC;
                selection-background-color: #E3F2FD;
                alternate-background-color: #F5F5F5;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
            }
            QHeaderView::section {
                background-color: #37474F;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Enable alternating row colors
        self.tasks_table.setAlternatingRowColors(True)
        
        content_layout.addWidget(self.tasks_table, 1)  # Give table stretch factor of 1 to expand
        
        # Add content to main layout
        main_layout.addLayout(content_layout)
        
        # Turn off internet when app starts
        self.set_internet("off")
        
        # Load initial reward value and tasks
        self.fetch_reward()
        self.fetch_tasks()
    
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
            
            # Turn off internet when getting new reward (timer not running)
            self.set_internet("off")
            
            # Update UI
            self.start_pause_button.setText("START")
            self.update_timer_display()
            
        except requests.exceptions.ConnectionError:
            QMessageBox.warning(self, "Connection Error", "Could not connect to the API server at http://127.0.0.1:8000")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Request Error", f"Failed to fetch reward: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
    
    def toggle_timer(self):
        if self.remaining_seconds <= 0:
            return
            
        if self.is_running:
            # Pause the timer - turn OFF internet
            self.timer.stop()
            self.is_running = False
            self.start_pause_button.setText("START")
            self.set_internet("off")
        else:
            # Start the timer - turn ON internet
            self.timer.start()
            self.is_running = True
            self.start_pause_button.setText("PAUSE")
            self.set_internet("on")
    
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
            # Timer finished - turn OFF internet
            self.timer.stop()
            self.is_running = False
            self.start_pause_button.setText("START")
            self.set_internet("off")
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
            
        self.timer_label.setStyleSheet(f"""
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 72px; 
            font-weight: bold; 
            padding: 30px;
            color: {color};
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            letter-spacing: 8px;
        """)
    
    def pulse_led(self):
        """Pulse the sync LED green for 1 second to indicate server update"""
        self.sync_led.setStyleSheet("""
            background-color: #00DD00; 
            border: 2px solid #00AA00;
            border-radius: 3px;
        """)
        self.led_timer.start(1000)  # Turn off after 1 second
    
    def turn_off_led(self):
        """Turn sync LED back to default gray state"""
        self.sync_led.setStyleSheet("""
            background-color: #666666; 
            border: 2px solid #333333;
            border-radius: 3px;
        """)
    
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
    
    def set_internet(self, state):
        """Turn internet on or off and update LED indicator"""
        try:
            response = requests.post("http://127.0.0.1:8000/networking", 
                                   json={"state": state})
            response.raise_for_status()
            
            self.internet_status = state
            if state == "on":
                # Green LED for internet ON
                self.internet_led.setStyleSheet("""
                    background-color: #00DD00; 
                    border: 2px solid #00AA00;
                    border-radius: 3px;
                """)
            else:
                # Red LED for internet OFF  
                self.internet_led.setStyleSheet("""
                    background-color: #FF4444; 
                    border: 2px solid #CC0000;
                    border-radius: 3px;
                """)
            
            print(f"Internet turned {state}")
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to control internet: {e}")
    
    def fetch_tasks(self):
        """Fetch pending and working tasks from API"""
        try:
            # Get pending tasks
            pending_response = requests.get("http://127.0.0.1:8000/tasks/?status=pending")
            pending_response.raise_for_status()
            pending_tasks = pending_response.json()
            
            # Get working tasks
            working_response = requests.get("http://127.0.0.1:8000/tasks/?status=working")
            working_response.raise_for_status()
            working_tasks = working_response.json()
            
            # Combine and display tasks
            all_tasks = pending_tasks + working_tasks
            self.populate_tasks_table(all_tasks)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch tasks: {e}")
            QMessageBox.warning(self, "Error", f"Failed to fetch tasks: {str(e)}")
    
    def populate_tasks_table(self, tasks):
        """Populate the tasks table with task data"""
        self.tasks_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # Task ID (hidden, we'll store it in the button)
            task_id = task.get('id', '')
            
            # Title
            title_item = QTableWidgetItem(task.get('title', ''))
            self.tasks_table.setItem(row, 0, title_item)
            
            # Reward
            reward_item = QTableWidgetItem(str(task.get('reward', 0)))
            self.tasks_table.setItem(row, 1, reward_item)
            
            # Status
            status = task.get('status', '')
            status_item = QTableWidgetItem(status.capitalize())
            self.tasks_table.setItem(row, 2, status_item)
            
            # Action button (only for pending tasks)
            if status == 'pending':
                start_button = QPushButton("START")
                start_button.setStyleSheet("""
                    QPushButton {
                        font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                        font-size: 10px; 
                        font-weight: bold;
                        padding: 5px 10px;
                        color: #FFFFFF;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #2196F3, stop:1 #1565C0);
                        border: 1px solid #0D47A1;
                        border-radius: 4px;
                        letter-spacing: 1px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #42A5F5, stop:1 #2196F3);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #1565C0, stop:1 #0D47A1);
                    }
                """)
                start_button.clicked.connect(lambda checked, tid=task_id: self.start_task(tid))
                self.tasks_table.setCellWidget(row, 3, start_button)
            else:
                # Working tasks don't get a button
                working_item = QTableWidgetItem("In Progress")
                working_item.setFlags(Qt.ItemIsEnabled)  # Make it read-only
                self.tasks_table.setItem(row, 3, working_item)
    
    def start_task(self, task_id):
        """Start a pending task by changing its status to working"""
        # Clear the table immediately to prevent multiple clicks
        self.tasks_table.setRowCount(0)
        
        try:
            response = requests.put(f"http://127.0.0.1:8000/tasks/{task_id}/status",
                                  json={"action": "start"})
            response.raise_for_status()
            
            print(f"Started task {task_id}")
            # Refresh the tasks table to show updated status
            self.fetch_tasks()
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to start task {task_id}: {e}")
            QMessageBox.warning(self, "Error", f"Failed to start task: {str(e)}")
            # Re-populate the table even if there was an error
            self.fetch_tasks()
    
    def closeEvent(self, event):
        """Handle app closing - turn off internet"""
        print("App closing - turning off internet")
        self.set_internet("off")
        event.accept()


def signal_handler(signum, frame):
    """Handle Ctrl+C and other signals - turn off internet"""
    print("\nReceived signal, turning off internet and exiting...")
    try:
        requests.post("http://127.0.0.1:8000/networking", json={"state": "off"})
    except:
        pass
    sys.exit(0)

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app = QApplication(sys.argv)
    window = RewardApp()
    window.show()
    sys.exit(app.exec())
