# -*- coding: utf-8 -*-
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io

text = "Xin chào! Đây là Raspberry Pi 5 đọc tiếng Việt."

# Chuy?n text thành âm thanh, l?u vào b? nh?
tts = gTTS(text=text, lang='vi')
fp = io.BytesIO()
tts.write_to_fp(fp)
fp.seek(0)

# Dùng pydub ?? phát tr?c ti?p t? b? nh?
audio = AudioSegment.from_file(fp, format="mp3")
play(audio)