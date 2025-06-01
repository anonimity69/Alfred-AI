import tkinter as tk
import speech_recognition as sr
import threading

class SpeechToText:
    def __init__(self, label, text_box):
        ''' Initialize the SpeechToText class with a label and text box for output. '''
        self.label = label
        self.text_box = text_box
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.listening = False

    def transcribe(self):
        ''' Continuously listen for speech and transcribe it to text. '''
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio)
                    self.text_box.insert(tk.END, f"You said: {text}\n")
                    self.text_box.see(tk.END)
                except sr.WaitTimeoutError:
                    self.text_box.insert(tk.END, "Timeout — no speech detected.\n")
                except sr.UnknownValueError:
                    self.text_box.insert(tk.END, "Didn't catch that.\n")
                except sr.RequestError as e:
                    self.text_box.insert(tk.END, f"API error: {e}\n")

    def start(self):
        ''' Start listening for speech input. '''
        if not self.listening:
            self.listening = True
            self.label.config(text="Listening...")
            threading.Thread(target=self.transcribe, daemon=True).start()

    def stop(self):
        ''' Stop listening for speech input. '''
        self.listening = False
        self.label.config(text="Recognition stopped.")

    def clear(self):
        ''' Clear the text box. '''
        self.text_box.delete("1.0", tk.END)

if __name__ == "__main__":
    ''' Main function to set up the GUI and start the speech recognition. '''
    root = tk.Tk()
    root.title("Live Speech-to-Text")
    root.geometry("600x300")

    label = tk.Label(root, text="Press 'Start' and speak into your mic...", font=("Helvetica", 14))
    label.pack(pady=10)

    text_box = tk.Text(root, height=8, font=("Courier", 12), wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Instantiate the recognizer
    stt = SpeechToText(label, text_box)

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    start_button = tk.Button(button_frame, text="Start Listening", command=stt.start, width=18, bg="lightgreen")
    start_button.pack(side=tk.LEFT, padx=5)

    stop_button = tk.Button(button_frame, text="Stop", command=stt.stop, width=10, bg="lightcoral")
    stop_button.pack(side=tk.LEFT, padx=5)

    clear_button = tk.Button(button_frame, text="Clear", command=stt.clear, width=10)
    clear_button.pack(side=tk.LEFT, padx=5)

    # Start the GUI loop
    root.mainloop()
