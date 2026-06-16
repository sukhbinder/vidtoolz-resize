import vidtoolz


# 1. Stretch to 1920×1080 (changes aspect ratio)
# Equivalent to resizing directly in MoviePy:
# ffmpeg -i input.mp4 -vf "scale=1920:1080" -c:a copy output.mp4
#
# 2. Crop top and bottom to preserve proportions
# Crop 180 pixels from the top and 180 pixels from the bottom:
# ffmpeg -i input.mp4 -vf "crop=1920:1080:0:180" -c:a copy output.mp4
#
# 3. Auto-center crop to 1920×1080
# Works for any input height ≥ 1080:
# ffmpeg -i input.mp4 -vf "crop=1920:1080:0:(ih-1080)/2" -c:a copy output.mp4
#
# 4. Letterbox instead of crop
# If you want the entire 1920×1440 frame preserved and fit inside a 1920×1080 canvas:
# ffmpeg -i input.mp4 \
# -vf "scale=1440:1080,pad=1920:1080:240:0" \
# -c:a copy output.mp4


# Using moviepy
#
# Option 1: Resize directly to 1920×1080 (stretches image)
# from moviepy import VideoFileClip
# clip = VideoFileClip("input.mp4")
# clip = clip.resized((1920, 1080))
# clip.write_videofile("output.mp4")
#
# Option 2: Crop to 16:9 while preserving proportions (recommended)
# from moviepy import VideoFileClip
# clip = VideoFileClip("input.mp4")
# clip = clip.cropped(
#     y1=180,
#     y2=1260
# )
# clip.write_videofile("output.mp4")
#
# Option 3: Auto-center crop to 1920×1080
# from moviepy import VideoFileClip
# clip = VideoFileClip("input.mp4")
# target_h = 1080
# y1 = (clip.h - target_h) // 2
# clip = clip.cropped(
#     x1=0,
#     y1=y1,
#     x2=clip.w,
#     y2=y1 + target_h
# )
# clip.write_videofile("output.mp4")
#
#
def create_parser(subparser):
    parser = subparser.add_parser("resize", description="Resize video using python")
    # Add subprser arguments here.
    parser.add_argument("-test", "--test", type=str, help="Example argument")
    return parser


class ViztoolzPlugin:
    """Resize video using python"""

    __name__ = "resize"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        # add actual call here
        pass

    def hello(self, args):
        # this routine will be called when "vidtoolz "resize is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


resize_plugin = ViztoolzPlugin()
