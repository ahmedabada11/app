import os
import threading
import json
import urllib.request
import urllib.parse
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

class DownloaderApp(App):
    def build(self):
        self.selected_quality = "720"
        self.is_audio = False

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(
            text="Media Downloader Pro",
            font_size='24sp',
            size_hint=(1, 0.12),
            bold=True,
            color=(0.2, 0.7, 1, 1)
        )
        layout.add_widget(title)

        self.url_input = TextInput(
            hint_text="ضع رابط الفيديو هنا (TikTok, YouTube, Facebook...)",
            multiline=False,
            font_size='16sp',
            size_hint=(1, 0.12),
            padding=[10, 10]
        )
        layout.add_widget(self.url_input)

        self.quality_grid = GridLayout(cols=4, spacing=10, size_hint=(1, 0.15))
        self.buttons = []
        options = [
            ("1080p", "1080", False),
            ("720p", "720", False),
            ("480p", "480", False),
            ("MP3 صوت", "720", True)
        ]

        for text, q, audio in options:
            btn = Button(text=text, font_size='14sp')
            btn.q = q
            btn.is_audio = audio
            btn.bind(on_press=self.select_quality)
            self.quality_grid.add_widget(btn)
            self.buttons.append(btn)
        layout.add_widget(self.quality_grid)

        self.status_label = Label(
            text="اختر الجودة واضغط بدء التحميل",
            font_size='14sp',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.status_label)

        self.progress_bar = ProgressBar(max=100, value=0, size_hint=(1, 0.08))
        layout.add_widget(self.progress_bar)

        self.download_btn = Button(
            text="بدء التحميل المباشر",
            font_size='20sp',
            size_hint=(1, 0.15),
            background_color=(0.1, 0.8, 0.3, 1)
        )
        self.download_btn.bind(on_press=self.start_download)
        layout.add_widget(self.download_btn)

        return layout

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

    def select_quality(self, btn):
        for b in self.buttons:
            b.background_color = (1, 1, 1, 1)
        btn.background_color = (0.2, 0.7, 1, 1)
        self.selected_quality = btn.q
        self.is_audio = btn.is_audio
        self.update_status(f"تم اختيار: {btn.text}")

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("يرجى إدخال الرابط أولاً!")
            return

        self.download_btn.disabled = True
        self.update_status("جاري تجهيز الرابط المباشر...")
        self.progress_bar.value = 20
        threading.Thread(target=self._worker, args=(url,), daemon=True).start()

    def _worker(self, url):
        try:
            api_url = "https://co.wuk.sh/api/json"
            payload = json.dumps({
                "url": url,
                "vQuality": self.selected_quality,
                "isAudioOnly": self.is_audio
            }).encode('utf-8')

            req = urllib.request.Request(
                api_url,
                data=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=20) as response:
                res_data = json.loads(response.read().decode('utf-8'))

            download_link = res_data.get("url")
            if not download_link:
                self.update_status("تعذر استخراج رابط التحميل، تأكد من صحة الرابط.")
                return

            self.update_status("تم الحصول على الرابط! جاري التحميل...")
            self.progress_bar.value = 50

            ext = "mp3" if self.is_audio else "mp4"
            filename = f"media_download.{ext}"
            save_folder = "/sdcard/Download" if os.path.exists("/sdcard/Download") else "."
            save_path = os.path.join(save_folder, filename)

            urllib.request.urlretrieve(download_link, save_path)
            self.progress_bar.value = 100
            self.update_status("اكتمل التحميل بنجاح في مجلد Downloads!")
        except Exception:
            self.update_status("حدث خطأ أثناء الاتصال أو جلب الوسائط.")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.download_btn, 'disabled', False))

if __name__ == '__main__':
    DownloaderApp().run()
