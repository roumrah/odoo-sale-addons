# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CommissionTargetRate(models.Model):
    _name = "commission.target.rate"
    _description = "Commission Target Rate"
    _order = "slice_from"

    target_id = fields.Many2one("commission.target", required=True, index=True)
    slice_from = fields.Float(required=True)
    slice_to = fields.Float(required=True)
    commission_percentage = fields.Float(required=True)
    max_amount = fields.Monetary(compute="_compute_max_amount", store=True)
    completion_rate = fields.Float(copy=False, readonly=True)
    subtotal = fields.Monetary(copy=False, readonly=True)
    company_id = fields.Many2one("res.company", related="target_id.company_id")
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    def _update_rate(self):
        self.completion_rate = self._compute_completion_rate()
        self.subtotal = self._compute_subtotal()

    def _compute_completion_rate(self):
        total = self.target_id.base_amount

        slice_from, slice_to = self._get_absolute_slice_amounts()
        if total <= slice_from:
            return 0

        elif total <= slice_to:
            full_slice = slice_to - slice_from
            completion = total - slice_from
            return completion / full_slice * 100

        else:
            return 100

    def _compute_subtotal(self):
        slice_from, slice_to = self._get_absolute_slice_amounts()
        return (
            (slice_to - slice_from)
            * self.completion_rate
            / 100
            * self.commission_percentage
        )

    def _get_absolute_slice_amounts(self):
        target = self.target_id.target_amount
        absolute_slice_from = self.slice_from * target
        absolute_slice_to = self.slice_to * target
        return absolute_slice_from, absolute_slice_to

    @api.depends("slice_from", "slice_to", "target_id.target_amount")
    def _compute_max_amount(self):
        for rate in self:
            absolute_bottom, absolute_top = rate._get_absolute_slice_amounts()
            rate.max_amount = absolute_top - absolute_bottom

    @api.constrains("slice_from", "slice_to")
    def _validate_slices(self):
        for rate in self:
            if rate.slice_to < rate.slice_from:
                raise ValidationError(
                    "The upper bound should be greater than the lower bound."
                )
