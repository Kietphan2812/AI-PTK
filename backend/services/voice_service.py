"""
Voice Service - Nhận diện giọng nói tiếng Việt cho AI PTK (Speech-to-Text)
Sử dụng sounddevice thu âm trực tiếp và Google Speech Recognition API tiếng Việt (vi-VN).
Sáng lập và phát triển bởi Phan Tấn Kiệt.
"""

import io
import wave
import time
from pathlib import Path

try:
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr
    HAS_VOICE = True
except Exception:
    HAS_VOICE = False


class VoiceService:
    """Dịch vụ thu âm và nhận dạng giọng nói tiếng Việt tức thì."""

    @classmethod
    def is_available(cls) -> bool:
        return HAS_VOICE

    @classmethod
    def record_and_recognize(cls, duration_seconds: int = 4, language: str = "vi-VN") -> dict:
        """Thu âm từ micro trong `duration_seconds` và chuyển thành văn bản tiếng Việt."""
        if not HAS_VOICE:
            return {
                "success": False,
                "error": "Chưa cài đặt thư viện sounddevice hoặc speech_recognition.",
                "text": "",
            }

        sample_rate = 16000
        channels = 1

        try:
            # 1. Thu âm từ Micro
            recording = sd.rec(
                int(duration_seconds * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                dtype="int16"
            )
            sd.wait()

            # 2. Đóng gói vào WAV buffer trong RAM
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(recording.tobytes())

            wav_buffer.seek(0)

            # 3. Nhận dạng bằng Google Speech Recognition
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            with sr.AudioFile(wav_buffer) as source:
                audio = recognizer.record(source)

            text = recognizer.recognize_google(audio, language=language)
            return {
                "success": True,
                "text": text.strip(),
                "error": "",
            }

        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Không nhận diện được giọng nói (âm thanh quá nhỏ hoặc im lặng). Vui lòng nói to và rõ hơn!",
                "text": "",
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Lỗi kết nối dịch vụ giọng nói Google: {e}",
                "text": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Lỗi thiết bị thu âm: {e}",
                "text": "",
            }
