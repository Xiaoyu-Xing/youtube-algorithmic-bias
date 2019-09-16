class YouTubePlayerException(RuntimeError):
    def __init__(self, msg: str, video: str):
        self.msg: str = msg
        self.video: str = video

    def __repr__(self):
        return repr("Below error occurred during viewing video {}: {}".format(self.video, self.msg))