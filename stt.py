import tkinter as tk
from RealtimeSTT import AudioToTextRecorder
import threading

class SpeechApp:
    def __init__(self, master):  
        self.master = master
        self.master.title("Alfred - Push to Talk")

        self.label = tk.Label(master, text="Press and hold to talk", font=("Arial", 14))
        self.label.pack(pady=20)

        self.output = tk.Text(master, height=10, width=50, state='disabled', wrap='word')
        self.output.pack(padx=20, pady=10)

        self.button = tk.Button(master, text="🎙 Push to Talk", font=("Arial", 16), width=20)
        self.button.pack(pady=20)

        self.button.bind('<ButtonPress>', self.start_listening)
        self.button.bind('<ButtonRelease>', self.stop_listening)

        self.recorder = AudioToTextRecorder()
        self.listening = False

    def display_message(self, message):
        self.output.config(state='normal')
        self.output.insert(tk.END, message + '\n')
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def process_text(self, text):
        self.display_message(f"🗣 {text}")

    def start_listening(self, event=None):
        if not self.listening:
            self.listening = True
            self.display_message("🟢 Listening...")
            threading.Thread(target=self.recorder.text, args=(self.process_text,), daemon=True).start()

    def stop_listening(self, event=None):
        if self.listening:
            self.recorder.stop()
            self.display_message("🛑 Stopped.")
            self.listening = False

def main():
    root = tk.Tk()
    app = SpeechApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()