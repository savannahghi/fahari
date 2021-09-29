from typing import Optional

from openpyxl.workbook import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework.renderers import BaseRenderer


class ExcelIORenderer(BaseRenderer):
    """Renderer for excel io data."""

    media_type = "application/xlsx"
    format = "xlsx"

    def render(self, data: Optional[Workbook], accepted_media_type=None, renderer_context=None):
        return save_virtual_workbook(data) if data else bytes()
