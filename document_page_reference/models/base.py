from odoo import models
from werkzeug.urls import url_encode


class Base(models.AbstractModel):
    _inherit = 'base'

    def get_direct_access_url(self, model=False):
        self.ensure_one()
        params = {
            'model': model or self._name,
            'id': self.id,
        }
        return '/web#' + url_encode(params)
