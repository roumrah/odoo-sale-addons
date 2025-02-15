# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Product(models.Model):

    _inherit = "product.product"

    rented_product_ids = fields.One2many(
        "product.template", "rental_service_id", "Rented Products"
    )

    @api.onchange("can_be_rented")
    def _if_can_be_rented__then_sale_ok(self):
        if self.can_be_rented:
            self.sale_ok = True

    @api.constrains("uom_id")
    def _check_rental_service_is_in_days(self):
        self.mapped("rented_product_ids")._check_rental_service_is_in_days()
