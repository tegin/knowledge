# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

try:
    from jinja2.sandbox import SandboxedEnvironment
    from jinja2 import Undefined

    class Context(SandboxedEnvironment.context_class):
        def resolve(self, key):
            res = super().resolve(key)
            if not isinstance(res, Undefined):
                return res
            return self.parent['ref'](key)

    class Environment(SandboxedEnvironment):
        context_class = Context

    mako_template_env = Environment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=False,
    )
except Exception:
    _logger.error("Jinja2 is not available")


class DocumentPage(models.Model):
    _name = 'document.page'
    _inherit = ['document.page', 'portal.mixin']

    reference = fields.Char()
    content_parsed = fields.Html(compute='_compute_content_parsed')

    @api.depends('history_head')
    def _compute_content_parsed(self):
        for record in self:
            record.content_parsed = record.get_content()

    @api.constrains('reference')
    def _check_reference(self):
        for record in self:
            if not record.reference:
                continue
            if self.search([
                ('reference', '=', record.reference),
                ('id', '!=', record.id)]
            ):
                raise ValidationError(_('Reference must be unique'))

    def get_reference(self, code):
        document = self.search([('reference', '=', code)])
        if not document:
            return code
        if self.env.context.get('raw_reference', False):
            return document.display_name
        return '<a href="%s">%s</a>' % (
            document.get_share_url(), document.display_name)

    def _get_template_variables(self):
        return {'ref': self.get_reference}

    def get_content(self):
        content = self.content
        mako_env = mako_template_env
        template = mako_env.from_string(tools.ustr(content))
        return template.render(self._get_template_variables())

    def get_raw_content(self):
        return self.with_context(raw_reference=True).get_content()
