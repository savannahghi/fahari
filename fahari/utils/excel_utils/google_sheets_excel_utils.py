from typing import Sequence

from googleapiclient.discovery import build


def read_spreadsheet(spreadsheet_id: str, range_name: str) -> Sequence[Sequence[str]]:
    """Retrieve the specified data from the given Google spreadsheet."""

    sheet_service = build("sheets", "v4").spreadsheets()
    result = sheet_service.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()

    return result.get("values", tuple())
