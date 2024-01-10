import pathlib
import datetime


class DateUtilsBase:
    fmt = "%a, %d %b %Y %X GMT"

    @staticmethod
    def get_http_date(timestamp: datetime.datetime.timestamp = None) -> str:
        """
        Format a timestamp as an HTTP date
        NOTE: strftime() doesn't seem to like self.fmt
        """
        if not timestamp:
            timestamp = datetime.datetime.now().timestamp()

        return datetime.datetime.fromtimestamp(timestamp).strftime(
            format="%a, %d %b %Y %X GMT"
        )

    def http_date_is_greater_than(self, date1: str, date2: str) -> bool:
        """
        Compare HTTP dates
        """
        date1_datetime = datetime.datetime.strptime(date1, self.fmt)
        date2_datetime = datetime.datetime.strptime(date2, self.fmt)

        return date1_datetime > date2_datetime


class FileUtilsBase:
    @staticmethod
    def get_file_last_modified_time_in_s(path: pathlib.Path) -> float:
        """
        Get file last modified time statistic
        """
        return path.stat().st_mtime

    def get_file_last_modified_time_as_string(self, input_path: str) -> str:
        """
        Get file last modified time statistic and stringify it
        """
        path = pathlib.Path(input_path)
        timestamp = self.get_file_last_modified_time_in_s(path)
        return DateUtilsBase.get_http_date(timestamp)


DateUtils = DateUtilsBase()
FileUtils = FileUtilsBase()
