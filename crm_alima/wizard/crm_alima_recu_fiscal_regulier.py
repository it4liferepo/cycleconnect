from odoo import api, fields, models
from datetime import date
import time


class RecuFiscalRegulier(models.TransientModel):
    _name = 'crm.alima.recu.fiscal.regulier.template'
    _description = 'Recu Fiscal Don Regulier template'

    @api.multi
    def action_create(self):
        donateur_id = int(self.env.context.get('donateur', False))
        if donateur_id:
            donateur = self.env['crm.alima.donateur'].browse(donateur_id)
            donateur.write({
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
            return self.env['report'].get_action(donateur, 'crm_alima.report_recufiscalregulier')

        return {
            'type': 'ir.actions.act_window_close',
        }

    date_from = fields.Date(string="Date Debut", required=True)
    date_to = fields.Date(string="Date Fin", required=True)