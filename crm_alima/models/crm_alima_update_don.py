# -*- coding: utf-8 -*-
from array import *
from datetime import datetime, date
import base64
from datetime import date

from odoo import models, api, fields, _
from odoo.exceptions import UserError

STATES = [
    ('draft', 'A importer'),
    ('done', 'Importation Réussie'),
    ('cancel', 'Importation Annulé'),
]

SEPARATOR = [
    ('virgule', 'virgule'),
    ('point_virgule', 'point virgule'),
    ('pipe', 'pipe'),
]

CORRESPONDANCE = {
    'virgule': ',',
    'point_virgule': ';',
    'pipe': '|',
}


class UpdateDon(models.Model):
    _name = 'crm.alima.update.don'
    _description = 'Update Don'

    @api.onchange('data', 'separator')
    def update_don_template(self):
        dons = []
        if self.data and self.separator:
            # try:
            data = base64.decodestring(self.data)
            separator = CORRESPONDANCE[self.separator]
            liste_data = [cell.split(separator) for cell in data.replace('\r', '').replace('"', '').split("\n")]
            liste_data_remove_space = [[cell.strip() for cell in line] for line in liste_data]
            dicos = self.fusion(liste_data_remove_space)
            # except:
            # raise UserError(_("Erreur, vérifier le séparateur et le fichier chargé"))
            for line in dicos:
                dons.append((0, 0, line))
            self.update_don_line = dons
        else:
            self.update_don_line = False

    name = fields.Char(string="Titre", required=True)
    description = fields.Text()
    datetime = fields.Datetime(readonly=True, string='Date dernière modification')
    separator = fields.Selection(SEPARATOR, default='point_virgule', required=True, String='Séparateur')
    nombre_de_dons_importes = fields.Integer(readonly=True, string="Nombre de dons modifiés")
    user_import = fields.Many2one('res.users', string="User", readonly=True)
    state = fields.Selection(STATES, default='draft', readonly=True)

    filename = fields.Char('File Name')
    data = fields.Binary('Import File')

    update_don_line = fields.One2many('crm.alima.update.don.template', 'update_don_id', string='Update Don')

    @api.model
    def default_get(self, fields):
        res = super(UpdateDon, self).default_get(fields)
        if 'user_import' in fields:
            res.update({
                'user_import': self.env.user.id,

            })
        return res

    @api.multi
    def action_confirmer(self):

        if not self.update_don_line:
            raise UserError(_("(re)charger le fichier d'import"))

        else:
            nombre_de_dons_importes = 0
            self.datetime = datetime.today()
            for line in self.update_don_line:
                self.env['crm.alima.don'].browse(line.id_don).write({
                    'NumRecuFiscal': line.NumRecuFiscal,
                    'dateEdition': line.dateEdition,
                    'dateEnvoi': line.dateEnvoi,
                    # 'id_intersa':line.id_intersa,
                })
                nombre_de_dons_importes += 1

            self.nombre_de_dons_importes = nombre_de_dons_importes
            self.state = 'done'

    @api.multi
    def action_annuler(self):
        self.state = 'cancel'

    @api.multi
    def action_reset_to_draft(self):
        self.state = 'draft'

    def fusion(self, liste):
        dicos = []
        for i in range(1, len(liste)):
            if len(liste[i]) < 4:
                continue
            dicos.append(dict(zip(liste[0], liste[i])))
        for i in range(len(dicos)):
            for key in dicos[i]:
                if 'date' in key:
                    if '/' in dicos[i][key]:
                        date = dicos[i][key].split(' ')[0].split('/')
                        date[0], date[2] = date[2], date[0]
                        dicos[i][key] = '-'.join(date)
                    elif '-' in dicos[i][key]:
                        date = dicos[i][key].split(' ')[0].split('-')
                        date[0], date[2] = date[2], date[0]
                        dicos[i][key] = '-'.join(date)
        for dico in dicos:
            dico['id_don'] = dico.pop('id')

        return dicos


class UpdateDonTemplate(models.Model):
    _name = 'crm.alima.update.don.template'
    _description = 'Update don Template'

    NumRecuFiscal = fields.Char(string="numero reçu fiscal")
    dateEdition = fields.Date(string='date édition RF')
    dateEnvoi = fields.Date(string='Date envoi RF')
    # id_intersa = fields.Char(string='ID Intersa')
    id_don = fields.Integer()

    update_don_id = fields.Many2one('crm.alima.update.don', string='Update Don')
