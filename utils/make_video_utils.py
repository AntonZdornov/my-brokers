import ffmpeg


def make_video_ffpy(
    cover_path: str, audio_path: str, output_path: str, audio_bitrate: str = "320k"
):
    (
        ffmpeg.input(cover_path, loop=1, framerate=30)  # статичная картинка
        .filter("format", pix_fmts="yuv420p")
        .output(
            ffmpeg.input(audio_path).audio,
            output_path,
            vcodec="libx264",
            acodec="aac",
            audio_bitrate=audio_bitrate,
            shortest=None,  # обрежет по длине аудио
            tune="stillimage",
        )
        .overwrite_output()
        .run()
    )
