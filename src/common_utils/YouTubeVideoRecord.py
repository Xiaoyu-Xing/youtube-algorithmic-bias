import datetime


class YouTubeVideoRecord:
    def __init__(self):
        self.source: str = "Unknown"
        self.approximated_uploaded_time: datetime.datetime = None
        self.video_length: int = -1
        self.views: int = -1
        self.query_time: datetime.datetime = None
        self.href: str = "Unknown"
        self.title: str = "Unknown"

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            if self.href == o.href or self.title in o.title or o.title in self.title:
                return True
        return False

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return repr(YouTubeVideoRecord.encoder(self))

    def __hash__(self) -> int:
        return hash((self.href, self.title))

    @staticmethod
    def encoder(o):
        if isinstance(o, YouTubeVideoRecord):
            return {
                "href": o.href,
                "title": o.title,
                "source": o.source,
                "approximated uploaded time":
                    o.approximated_uploaded_time.strftime("%m/%d/%Y %H:%M:%S")
                    if o.approximated_uploaded_time else "Unknown",
                "video length": str(o.video_length) + " seconds",
                "views": str(o.views),
                "query time": o.query_time.strftime("%m/%d/%Y %H:%M:%S")
                if o.query_time else "Unknown"
            }
        else:
            type_name = o.__class__.__name__
            raise TypeError(f"Object of type '{type_name}' is not serializable")

    @staticmethod
    def decoder(o):
        record = YouTubeVideoRecord()
        if "href" in o:
            record.href = o["href"]
        if "title" in o:
            record.title = o["title"]
        if "source" in o:
            record.source = o["source"]
        if "approximated uploaded time" in o:
            record.approximated_uploaded_time = \
                datetime.datetime.strptime(o["approximated uploaded time"], "%m/%d/%Y %H:%M:%S") \
                if o["approximated uploaded time"] != "Unknown" else None
        if "video length" in o:
            record.video_length = int(o["video length"].split()[0])
        if "views" in o:
            record.views = int(o["views"])
        if "query time" in o:
            record.query_time = datetime.datetime.strptime(o["query time"], "%m/%d/%Y %H:%M:%S") \
                if o["query time"] != "Unknown" else None
        return record


def test_encoder_decoder():
    dic = {"href": "https://www.youtube.com/watch?v=vI6zefu_kss",
           "title": "WATCH LIVE: Robert Mueller is testifying on his report, Trump and Russia",
           "source": "PBS NewsHour Streamed",
           "approximated uploaded time": "08/16/2019 16:51:13",
           "video length": "28800 seconds",
           "views": '506804',
           "query time": "09/15/2019 16:51:13",
           }
    record = YouTubeVideoRecord.decoder(dic)
    print(type(record))
    print(dic)
    string = YouTubeVideoRecord.encoder(record)
    print(string)


if __name__ == "__main__":
    test_encoder_decoder()
