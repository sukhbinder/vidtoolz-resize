import shlex
import subprocess

import vidtoolz
from moviepy import CompositeVideoClip, VideoFileClip
import os


def determine_output_path(input_file, output_file):
    input_dir, input_filename = os.path.split(input_file)
    name, _ = os.path.splitext(input_filename)

    if output_file:
        output_dir, output_filename = os.path.split(output_file)
        if not output_dir:  # If no directory is specified, use input file's directory
            return os.path.join(input_dir, output_filename)
        return output_file
    else:
        return os.path.join(input_dir, f"{name}_text.mp4")


def create_parser(subparser):
    parser = subparser.add_parser(
        "resize",
        description="Resize, crop, or letterbox videos",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input video file",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output video file name (default: %(default)s)",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["stretch", "crop", "center-crop", "letterbox"],
        default="center-crop",
        help="Resize mode (default: center-crop)",
    )

    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=1920,
        help="Target width (default: 1920)",
    )

    parser.add_argument(
        "-ht",
        "--height",
        type=int,
        default=1080,
        help="Target height (default: 1080)",
    )

    parser.add_argument(
        "--crop-top",
        type=int,
        default=180,
        help="Pixels to crop from top (crop mode only)",
    )

    parser.add_argument(
        "--crop-bottom",
        type=int,
        default=180,
        help="Pixels to crop from bottom (crop mode only)",
    )

    parser.add_argument(
        "-um",
        "--use-moviepy",
        action="store_true",
        help="Use MoviePy instead of FFmpeg",
    )

    return parser


def run_ffmpeg(args):
    target_w = args.width
    target_h = args.height
    output = determine_output_path(args.input, args.output)
    if args.mode == "stretch":
        vf = f"scale={target_w}:{target_h}"

    elif args.mode == "crop":
        vf = f"crop={target_w}:{target_h}:" f"0:{args.crop_top}"

    elif args.mode == "center-crop":
        # Scale while preserving aspect ratio, then center crop.
        vf = (
            f"scale={target_w}:{target_h}:"
            "force_original_aspect_ratio=increase,"
            f"crop={target_w}:{target_h}"
        )

    elif args.mode == "letterbox":
        vf = (
            f"scale={target_w}:{target_h}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={target_w}:{target_h}:"
            "(ow-iw)/2:(oh-ih)/2"
        )

    else:
        raise ValueError(f"Unsupported mode: {args.mode}")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        args.input,
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        output,
    ]

    print("Running FFmpeg:")
    print(shlex.join(cmd))

    subprocess.run(cmd, check=True)


def run_moviepy(args):
    clip = VideoFileClip(args.input)

    target_w = args.width
    target_h = args.height

    output = determine_output_path(args.input, args.output)
    try:
        if args.mode == "stretch":
            result = clip.resized((target_w, target_h))

        elif args.mode == "crop":
            result = clip.cropped(
                x1=0,
                y1=args.crop_top,
                x2=clip.w,
                y2=clip.h - args.crop_bottom,
            )

            if result.w != target_w or result.h != target_h:
                result = result.resized((target_w, target_h))

        elif args.mode == "center-crop":
            scale = max(
                target_w / clip.w,
                target_h / clip.h,
            )

            resized = clip.resized(scale)

            x1 = max(0, (resized.w - target_w) // 2)
            y1 = max(0, (resized.h - target_h) // 2)

            result = resized.cropped(
                x1=x1,
                y1=y1,
                x2=x1 + target_w,
                y2=y1 + target_h,
            )

        elif args.mode == "letterbox":
            scale = min(
                target_w / clip.w,
                target_h / clip.h,
            )

            resized = clip.resized(scale)

            result = CompositeVideoClip(
                [resized.with_position("center")],
                size=(target_w, target_h),
            ).with_duration(clip.duration)

            if clip.audio is not None:
                result.audio = clip.audio

        else:
            raise ValueError(f"Unsupported mode: {args.mode}")

        result.write_videofile(
            output,
            codec="libx264",
            audio_codec="aac",
        )

    finally:
        clip.close()

        try:
            result.close()
        except Exception:
            pass


class ViztoolzPlugin:
    """Resize video using FFmpeg (default) or MoviePy."""

    __name__ = "resize"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        if args.use_moviepy:
            print("Using MoviePy backend")
            run_moviepy(args)
        else:
            print("Using FFmpeg backend")
            run_ffmpeg(args)

    def hello(self, args):
        print("Hello! This is the resize vidtoolz plugin.")


resize_plugin = ViztoolzPlugin()
