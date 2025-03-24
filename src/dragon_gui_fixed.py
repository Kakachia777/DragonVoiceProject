# Log application start
logging.info("Starting DragonVoice application")

class DragonVoiceGUI:
    def animate_level_meter(self):
        """Animate the level meter to show microphone activity"""
        if not hasattr(self, 'recording_active') or not self.recording_active:
            # Stop animation if recording is not active
            self._update_level_meter(0)  # Reset to zero
            return

        try:
            # Get current audio level from the whisper recognizer
            if hasattr(self, 'whisper_recognizer') and self.whisper_recognizer:
                # Check if the get_audio_level method exists
                if hasattr(self.whisper_recognizer, 'get_audio_level'):
                    volume = self.whisper_recognizer.get_audio_level() * 100
                else:
                    # Fallback to using audio_data directly
                    if hasattr(self.whisper_recognizer, 'audio_data') and self.whisper_recognizer.audio_data:
                        latest_chunk = self.whisper_recognizer.audio_data[-1]
                        volume = np.sqrt(np.mean(latest_chunk**2)) * 200  # Scale for visibility
                    else:
                        volume = random.randint(10, 30)  # Fallback to random values
            else:
                # Generate random level for testing if no recognizer
                volume = random.randint(10, 30)

            # Update the level meter
            self._update_level_meter(volume)

            # Update status indicator
            if hasattr(self, 'status_value_3'):
                if volume > 70:
                    self.status_value_3.configure(text="Speaking")
                    if hasattr(self, 'status_indicator_3'):
                        self.status_indicator_3.configure(fg_color=self.colors["status_red"])
                elif volume > 30:
                    self.status_value_3.configure(text="Active")
                    if hasattr(self, 'status_indicator_3'):
                        self.status_indicator_3.configure(fg_color=self.colors["status_yellow"])
                else:
                    self.status_value_3.configure(text="Listening")
                    if hasattr(self, 'status_indicator_3'):
                        self.status_indicator_3.configure(fg_color=self.colors["status_green"])

            # Continue animation if recording is still active
            if self.recording_active:
                self.app.after(100, self.animate_level_meter)
        except Exception as e:
            logging.error(f"Error in level meter animation: {str(e)}")
            # Try to continue animation despite error
            if hasattr(self, 'recording_active') and self.recording_active:
                self.app.after(100, self.animate_level_meter)
