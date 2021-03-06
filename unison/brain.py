"""The "Brain" class handles most of Unison's processing.

This class sets up all instances of all the necessary classes for the program.
It then runs the main loop of the program which handles the calls for the 
program feedback, SpeechToText, Switch, and TextToSpeech methods. 
"""

# Handles activity log
import logging as log

from unison.apis.speech_to_text import SpeechToText
# Import Audio I/O classes
from unison.apis.text_to_speech import TextToSpeech
# Import main program classes
from unison.classes.desktop import Desktop
from unison.classes.login import Login
from unison.classes.switch import Switch

from unison.classes.settings import Settings


class Brain:

    def __init__(self):
        """Handle core components of Unison.
        
        Note:
            Any changes made to this class should be made with caution.
        """
        # Get and set all settings, apis, and mods
        self.settings_obj = Settings()
        self.settings = self.settings_obj.set()

        # Create log and set logger settings
        self.create_logger()
        self.set_logger()

        # Initialize Audio I/O objects
        self.stt = SpeechToText(self.settings)
        self.tts = TextToSpeech(self.settings)

        # Initialize Switch object
        self.switch = Switch(self.settings, self.stt, self.tts)

        # Create directory for local file and program access
        Desktop.create(self.settings)

        # User login - Note: might overwrite some default settings!
        Login(self.settings)

        # Program control variables
        self.feedback = True

        # Set instance variables
        self.beep = self.settings["beep"]
        self.d_beep = self.settings["d_beep"]
        self.beep_v = self.settings["beep_visual"]
        self.d_beep_v = self.settings["d_beep_visual"]

    def create_logger(self):
        """Create log file.
        
        Attempt to read the .log file to verify creation.
        
        Raises:
            FileNotFoundError: Creates .log file (will occur on first run).
        """
        try:
            with open(self.settings["logger"]):
                pass
        except FileNotFoundError:
            open(self.settings["logger"], "w+")

    def set_logger(self):
        """Set basic configuration for log."""
        log.basicConfig(filename=self.settings["log_path"],
                        format=self.settings["log_format"],
                        datefmt=self.settings["date_format"],
                        level=log.DEBUG)

    def gen_feedback(self, audio, visual):
        """Generate audio and visual feedback for the user."""
        # Audio feedback
        self.tts.play_mp3(audio, clear=False)

        # Visual feedback
        print(visual)

    def process_msg(self, msg):
        """Process msg through if/else statements.
        
        Args:
            msg (str): Message to be processed.
            
        Returns:
            bool: True if a module was run, False if not.
            str: msg if the keyword was not in msg.
        """
        # Select process to run
        if self.settings["keyword"] in msg:
            # Log msg
            log.info(msg)

            # Runs switch with msg
            executed = self.switch.run(msg)

            # Handles false positives
            if executed:
                return True
            else:
                return False
        # Do not process msg
        else:
            return msg

    def run(self):
        """Run main program loop."""
        while True:
            # Program feedback
            if self.feedback:
                self.gen_feedback(self.beep, self.beep_v)

            # Listen to audio from mic
            msg = self.stt.listen()

            # Verify and process audio msg
            if msg:
                # For str consistency
                msg = msg.lower()

                # Check if msg was processed
                success = self.process_msg(msg)

                # Set feedback according to success
                if success == msg:
                    self.feedback = False
                elif success:
                    self.feedback = True
                elif not success:
                    self.feedback = False
                    self.gen_feedback(self.d_beep, self.d_beep_v)
            else:
                self.feedback = False
                continue
