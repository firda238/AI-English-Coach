# Audio Upload Demo Note

The MVP supports audio file upload for `wav`, `mp3`, and `m4a` files.

If `faster-whisper` or `whisper` is installed locally, the app tries to transcribe the audio into English text. For quick local testing, use the small `tiny.en` model:

```bash
WHISPER_MODEL_SIZE=tiny.en python scripts/test_transcription.py
```

If no local speech model is available, the app shows:

> 当前为演示模式，请使用文本输入或示例转写文本。

This fallback behavior is intentional. It keeps the course project runnable without paid speech evaluation services or a required model download.

Example transcript for demonstration:

```text
I would like to order a chicken salad and a cup of coffee, please.
```
