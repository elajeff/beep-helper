import os
import tempfile
import unittest
import wave

from beep_helper import write_tone


class WriteToneTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = os.path.join(folder.name, "tone.wav")

    def read_samples(self):
        with wave.open(self.path, "rb") as wav:
            frames = wav.readframes(wav.getnframes())
        return memoryview(frames).cast("h")

    def test_each_profile_is_a_short_mono_16_bit_wav(self):
        for profile_id, seconds in [(1, 0.32), (2, 0.41), (3, 0.35)]:
            with self.subTest(profile=profile_id):
                write_tone(self.path, profile_id, 35)
                with wave.open(self.path, "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getnframes(), int(wav.getframerate() * seconds))

    def test_lower_volume_gives_a_quieter_tone(self):
        write_tone(self.path, 1, 1)
        quiet = max(map(abs, self.read_samples()))
        write_tone(self.path, 1, 100)
        loud = max(map(abs, self.read_samples()))
        self.assertLess(quiet, loud)


if __name__ == "__main__":
    unittest.main()
