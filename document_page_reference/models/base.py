from odoo import models
from werkzeug.urls import url_encode


class Base(models.AbstractModel):
    _inherit = 'base'

    def get_direct_access_url(self):
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        return '/mail/view?' + url_encode(params)
