# -*- coding: utf-8 -*-
from array import *
from datetime import datetime, date
import base64

from odoo import models, api, fields, _
from odoo.exceptions import UserError

TYPE_DON = [
    ('adhesion', 'Adhésion'),
    ('don', 'Don')
]
TYPE_CB = [
    ('Master Card', 'Master Card'),
    ('Visa', 'Visa'),
]
PLATEFORME = [
    ('iRaiser', 'iRaiser'),
    ('PayPal', 'PayPal'),
    ('Paybox', 'Paybox'),
    ('Netprelevement', 'Netprélèvement'),
    ('Alvarum', 'Alvarum'),
    ('Partenariat', 'Partenariat'),
    ('Autres', 'Autres'),
]
FORME_DON = [
    ('Compte bancaire', 'Compte bancaire'),
    ('Carte Bancaire', 'Carte Bancaire'),
    ('Cheque', 'Chèque'),
    ('Especes', 'Espèces'),
    ('Prelevement Salaire', 'Prélèvement Salaire'),
    ('Don manuel', 'Don manuel'),
]
MOYEN_PAIEMENT = [
    ('Virement bancaire', 'Virement bancaire'),
    ('Cheque', 'Chèque'),
    ('Abandon de creance', 'Abandon de Créance'),
    ('Especes', 'Espèces'),
    ('Prelevement', 'Prélèvement salaire'),
    ('Carte bancaire', 'Carte bancaire'),
    ('Compte bancaire', 'Compte bancaire'),
    ('SMS', 'SMS'),
    ('Autres', 'Autre(s)'),
]
MODE_VERSEMENT = [
    ('avec prelevement', 'avec prélèvement automatique'),
    ('sans prelevement', 'sans prélèvement automatique'),
]
FORME_DON_RECU = [
    ('Acte authentique', 'Acte authentique'),
    ('acte sous seing prive', 'Acte sous Seing privé'),
    ('declaration de don manuel', 'Déclaration de don manuel'),
    ('Don manuel', 'Don manuel'),
    ('Autres', 'Autres'),
]
TYPE_PRELEVEMENT = [
    ('Iraiser', 'Iraiser'),
    ('Netprelevement', 'Netprelevement')
]
DEVISE = [
    ('EUR', 'EUR'),
    ('XOF', 'XOF'),
    ('USD', 'USD'),
    ('GNF', 'GNF'),
    ('XAF', 'XAF'),
    ('Autre', 'Autre'),
]
TYPE_ENVOI = [
    ('Email', 'Email'),
    ('Courrier', 'Courrier')
]
NATURE_DON = [
    ('Numeraire', 'Numeraire'),
    ('Titres de Societes Cotees', 'Titres de Sociétés Côtées'),
    ('Autres', 'Autres'),
]
DROIT_REDUCTION_IMPOT = [
    ('200 du CGI IRP', '200 du CGI IRPP'),
    ('238 bis du CGI IS', '238 bis du CGI IS'),
    ('885-0 V bis A du CGI ISF', '885-0 V bis A du CGI ISF'),
]
OUIOUNON = [
    ('OUI', 'OUI'),
    ('NON', 'NON'),
]
TYPE_CB = [
    ('CB', 'CB'),
    ('VISA', 'VISA'),
    ('MasterCard', 'MasterCard'),
    ('AMEX', 'AMEX'),
]
LIBERALITE = [
    ('Don', 'Don'),
    ('Donation', 'Donation'),
    ('Legs', 'Legs'),
    ('Assurance-vie', 'Assurance-vie'),
]
RF = [
    ('R', 'R'),
    ('A', 'A'),
    ('N', 'N'),
]
SENS = [
    ('Eortant', 'Sortant'),
    ('Entrant', 'Entrant'),
]

STATES = [
    ('draft', 'Brouillon'),
    ('confirmer', 'Importé'),
    ('annuler', 'Annulé'),
]

GET_KEY = {
    'sans prélèvement automatique': 'sans prelevement',
    'avec prélèvement automatique': 'avec prelevement',
    'Titres de Sociétés Côtées': "Titres de Societes Cotees",
    'Déclaration de don manuel': "declaration de don manuel",
    'Acte sous Seing privé': "acte sous seing prive",
    'Autre(s)': "Autres",
    'Chèque': 'Cheque',
    'Abandon de Créance': 'Abandon de creance',
    'Espèces': 'Especes',
    'Prélèvement salaire': 'Prelevement',
    'Prélèvement Salaire': 'Prelevement Salaire',
    'Netprélèvement': 'Netprelevement',
    'Adhésion': 'adhesion',
    'Don': 'don',
    'Sortant': 'Eortant',
    'False': False,
}

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


class IMPORTDONCREDITCOOP(models.Model):
    _name = 'crm.alima.import.don.credit.coop'
    _description = 'IMPORT DON CREDIT COOP'

    @api.onchange('data', 'separator')
    def import_don_template(self):
        dons = []
        if self.data and self.separator:
            # try:
            data = base64.decodestring(self.data.encode())
            separator = CORRESPONDANCE[self.separator]
            liste_data = [cell.split(separator) for cell in
                          data.decode().replace('\r', '').replace('"', '').split("\n")]
            liste_data_remove_space = [[cell.strip() for cell in line] for line in liste_data]
            dicos = self.fusion(liste_data_remove_space)
            # except:
            #    raise UserError(_("Erreur d'import, vérifier le séparateur et le fichier chargé"))
            for line in dicos:
                if 'donateur' not in line:
                    continue
                dons.append((0, 0, line))
            self.don_credit_coop_line = dons
        else:
            self.don_credit_coop_line = False

    name = fields.Char(string="Titre", required=True)
    description = fields.Text()
    datetime = fields.Datetime(readonly=True, string='Date import')
    separator = fields.Selection(SEPARATOR, default='virgule', required=True, String='Séparateur')
    nombre_de_dons_importes = fields.Integer(readonly=True)
    user_import = fields.Many2one('res.users', string="User", readonly=True)
    state = fields.Selection(STATES, default='draft', readonly=True)
    a_corriger = fields.Boolean(string='A corriger')

    filename = fields.Char('File Name')
    data = fields.Binary('Import PO')

    don_credit_coop_line = fields.One2many('crm.alima.don.template', 'don_credit_coop_id', string='Don', required=True)

    @api.model
    def default_get(self, fields):
        res = super(IMPORTDONCREDITCOOP, self).default_get(fields)
        if 'user_import' in fields:
            res.update({
                'user_import': self.env.user.id,

            })
        return res

    @api.multi
    def clear_line(self):
        self.don_credit_coop_line = False
        self.data = False

    def fusion(self, liste):
        dicos = []
        for i in range(1, len(liste)):
            dicos.append(dict(zip(liste[0], liste[i])))
        for i in range(len(dicos)):
            for key in dicos[i]:
                dicos[i][key] = GET_KEY[dicos[i][key]] if dicos[i][key] in GET_KEY else dicos[i][key]
                if key == 'montantEur':
                    dicos[i][key] = float(dicos[i][key])
                if key == 'donateur' and dicos[i][key]:
                    try:
                        dicos[i][key] = int(dicos[i][key])
                    except:
                        dicos[i][key] = self.env['crm.alima.donateur'].search([('name', '=', dicos[i][key].strip())],
                                                                              limit=1)

                if key == 'codeMedia' and dicos[i][key]:
                    try:
                        dicos[i][key] = int(dicos[i][key])
                    except:
                        code_media = self.env['crm.alima.code.media'].search([('name', '=', dicos[i][key])], limit=1)
                        if not code_media:
                            dicos[i][key] = self.env['crm.alima.code.media'].create({'name': dicos[i][key]})
                        else:
                            dicos[i][key] = code_media
                if key == 'liberalite':
                    dicos[i][key] = dicos[i][key].capitalize()
                if 'date' in key and '/' in dicos[i][key]:
                    date = dicos[i][key].split(' ')[0].split('/')
                    date[0], date[2] = date[2], date[0]
                    dicos[i][key] = '-'.join(date)

        return dicos

    @api.multi
    def action_confirmer(self):

        if not self.don_credit_coop_line:
            raise UserError(_("(re)charger le fichier d'import"))

        else:
            don = {}
            nombre_de_dons_importes = 0
            self.datetime = datetime.today()
            for line in self.don_credit_coop_line:
                don = {
                    'codeMedia': line.codeMedia.id,
                    'adhesion': line.adhesion,
                    'date': line.date,
                    'forme_don': line.forme_don,
                    'nature_don': line.nature_don,
                    'liberalite': line.liberalite,
                    'moyen_paiment': line.moyen_paiment,
                    'mode_versement': line.mode_versement,
                    'commentaire': line.commentaire,
                    'date_recep': line.date_recep,
                    'date_signature': line.date_signature,
                    'date_remise': line.date_remise,
                    'date_encais': line.date_encais,
                    'montantEur': line.montantEur,
                    'devis_origine': line.devis_origine,
                    'nom_banque': line.nom_banque,
                    'numCheque': line.numCheque,
                    'remise_globale': line.remise_globale,
                    'montant_remise_globale': line.montant_remise_globale,
                    'plateforme_paiement': line.plateforme_paiement,
                    'parametreRF': line.parametreRF,
                    'NumRecuFiscal': line.NumRecuFiscal,
                    'dateEdition': line.dateEdition,
                    'dateEnvoi': line.dateEnvoi,
                    'prelevement_en_cours': line.prelevement_en_cours,
                    'commentaire_autre': line.commentaire_autre,
                    'donateur': line.donateur.id,
                    'montantEurSave': line.montantEurSave,
                    'valide': line.valide,
                    # 'id_intersa': line.id_intersa,
                    'datetime_import': self.datetime,
                }

                don = self.env['crm.alima.don'].create(don)
                nombre_de_dons_importes += 1

            self.nombre_de_dons_importes = nombre_de_dons_importes
            self.state = 'confirmer'

    @api.multi
    def action_annuler(self):
        self.state = 'annuler'

    @api.multi
    def action_reset_to_draft(self):
        self.state = 'draft'

    @api.multi
    def action_roll_back(self):
        if self.datetime:
            self.env['crm.alima.don'].search([('datetime_import', '=', self.datetime)]).unlink()
        else:
            raise UserError(_("Roll back échoué"))
        self.state = 'draft'

    @api.multi
    def action_correction(self):
        for line in self.don_credit_coop_line:
            self.env['crm.alima.don'].search([
                ('donateur', '=', line.donateur.id),
                ('codeMedia', '=', line.codeMedia.id),
                ('date', '=', line.date),
            ]).unlink()
            self.a_corriger = False

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Peut pas supprimer un import en état %s.') % self.state)
        return super(IMPORTDONCREDITCOOP, self).unlink()


class DonTemplate(models.Model):
    _name = 'crm.alima.don.template'
    _description = 'Don Template'

    codeMedia = fields.Many2one('crm.alima.code.media', string='code media', ondelete='restrict')
    adhesion = fields.Selection(OUIOUNON, string="Adhesion")
    date = fields.Date(string="Date du don", required=True)
    forme_don = fields.Selection(FORME_DON_RECU, index=True, string='forme du don')
    nature_don = fields.Selection(NATURE_DON, string="Nature du don")
    liberalite = fields.Selection(LIBERALITE, string='Liberalite')
    moyen_paiment = fields.Selection(MOYEN_PAIEMENT, string="Moyen de paiement")
    mode_versement = fields.Selection(MODE_VERSEMENT, string="Mode de versement")
    commentaire = fields.Text(string="Commentaire")
    date_recep = fields.Date(string='Date de récéption du chèque')
    date_signature = fields.Date(string='Date de signature du chèque')
    date_remise = fields.Date(string='Date de remise du chèque')
    date_encais = fields.Date(string='Date d\'encaissement du chèque')
    montantEur = fields.Float(string="Montant du don en Euro")
    devis_origine = fields.Selection(DEVISE, string='Devis d\'origine')
    nom_banque = fields.Char(string='Non banque')
    numCheque = fields.Char(string='Numero cheque')
    remise_globale = fields.Boolean(string="remise globale")
    montant_remise_globale = fields.Float(string="montant remise globale")
    plateforme_paiement = fields.Selection(PLATEFORME, string='plateforme de paiement')
    parametreRF = fields.Selection(RF, string='RF')
    NumRecuFiscal = fields.Char(string="numero reçu fiscal")
    dateEdition = fields.Date(string='date édition RF')
    dateEnvoi = fields.Date(string='Date envoi RF')
    prelevement_en_cours = fields.Boolean(string='Prelevement en cours')
    commentaire_autre = fields.Text(string="Commentaire")
    donateur = fields.Many2one('crm.alima.donateur', string='donateur', required=True, ondelete='cascade')
    montantEurSave = fields.Float(string='Montant du don en Euro sauvegarder')
    valide = fields.Boolean(dafault=False, string='Validation creation')
    # id_intersa = fields.Char(string='ID Intersa')

    don_credit_coop_id = fields.Many2one('crm.alima.import.don.credit.coop', string='CREDIT COOP')
