# -*- coding: utf-8 -*-
from datetime import datetime, date
import base64

from odoo import models, api, fields, _
from odoo.exceptions import UserError

STATES = [
    ('draft', 'Brouillon'),
    ('confirmer', 'Importé'),
    ('annuler', 'Annulé'),
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

MOTIF_FIN_ENGAGEMENT = [
    ('decision_solthis', 'Décision Solthis'),
    ('upgrade', 'Upgrade'),
    ('downgrade', 'downgrade'),
    ('incidents_paiement', 'Incidents de paiement'),
    ('autres', 'Autres'),
]

PERIODICITE = [
    ('un_mois', '1 mois'),
    ('deux_mois', '2 mois'),
    ('trois_mois', '3 mois'),
    ('quatre_mois', '4 mois'),
    ('six_mois', '6 mois'),
    ('douze_mois', '12 mois'),
]

STATUT_ENGAGEMENT = [
    ('actif', 'Actif'),
    ('suspendu_temporairement', 'Suspendu Temporairement'),
    ('inactif', 'Inactif'),
]


class IMPORTENGAGEMENT(models.Model):
    _name = 'crm.alima.import.engagement'
    _description = 'IMPORT ENGAGEMENT'

    @api.onchange('data', 'separator')
    def import_engagement_template(self):
        engagements = []
        if self.data and self.separator:
            try:
                data = base64.decodestring(self.data)
                separator = CORRESPONDANCE[self.separator]
                liste_data = [cell.split(separator) for cell in data.replace('\r', '').replace('"', '').split("\n")]
                liste_data_remove_space = [[cell.strip() for cell in line] for line in liste_data]
                dicos = self.fusion(liste_data_remove_space)
            except:
                raise UserError(_("Erreur d'import, vérifier le séparateur et le fichier chargé"))
            for line in dicos:
                if 'donateur' not in line:
                    continue
                engagements.append((0, 0, line))
            self.engagement_line = engagements
        else:
            self.engagement_line = False

    name = fields.Char(string="Titre", required=True)
    description = fields.Text()
    datetime = fields.Datetime(readonly=True, string='Date import')
    separator = fields.Selection(SEPARATOR, default='virgule', required=True, String='Séparateur')
    nombre_de_engagements_importes = fields.Integer(readonly=True)
    user_import = fields.Many2one('res.users', string="User", readonly=True)
    state = fields.Selection(STATES, default='draft', readonly=True)

    filename = fields.Char('File Name')
    data = fields.Binary('Import PO')

    engagement_line = fields.One2many('crm.alima.engagement.template', 'engagement_id', string='Engagement',
                                      required=True)

    @api.model
    def default_get(self, fields):
        res = super(IMPORTENGAGEMENT, self).default_get(fields)
        if 'user_import' in fields:
            res.update({
                'user_import': self.env.user.id,

            })
        return res

    @api.multi
    def clear_line(self):
        self.engagement_line = False
        self.data = False

    def fusion(self, liste):
        dicos = []
        for i in range(1, len(liste)):
            dicos.append(dict(zip(liste[0], liste[i])))
        for i in range(len(dicos)):
            for key in dicos[i]:
                # dicos[i][key] = GET_KEY[dicos[i][key]] if dicos[i][key] in GET_KEY else dicos[i][key]
                if key == 'montant':
                    dicos[i][key] = float(dicos[i][key])
                if key == 'donateur' and dicos[i][key]:
                    try:
                        dicos[i][key] = int(dicos[i][key])
                    except:
                        dicos[i][key] = self.env['crm.alima.donateur'].search([('name', '=', dicos[i][key].strip())],
                                                                              limit=1)

                if key in ['code_media', 'code_media_origine', 'code_media_engagement_modifie'] and dicos[i][key]:
                    try:
                        dicos[i][key] = int(dicos[i][key])
                    except:
                        code_media = self.env['crm.alima.code.media'].search([('name', '=', dicos[i][key])], limit=1)
                        if not code_media:
                            dicos[i][key] = self.env['crm.alima.code.media'].create({'name': dicos[i][key]})
                        else:
                            dicos[i][key] = code_media
                if 'date' in key:
                    if '/' in dicos[i][key]:
                        date = dicos[i][key].split(' ')[0].split('/')
                        date[0], date[2] = date[2], date[0]
                        dicos[i][key] = '-'.join(date)
                    elif '-' in dicos[i][key]:
                        date = dicos[i][key].split(' ')[0].split('-')
                        date[0], date[2] = date[2], date[0]
                        dicos[i][key] = '-'.join(date)

        return dicos

    @api.multi
    def action_confirmer(self):

        if not self.engagement_line:
            raise UserError(_("(re)charger le fichier d'import"))

        else:
            engagement = {}
            nombre_de_engagements_importes = 0
            self.datetime = datetime.today()
            for line in self.engagement_line:
                engagement = {
                    'donateur': line.donateur.id,
                    'code_media_origine': line.code_media_origine.id,
                    'code_media': line.code_media.id,
                    'date_accord_mandat': line.date_accord_mandat,
                    'date_fin_mandat': line.date_fin_mandat,
                    'date_fin_engagement': line.date_fin_engagement,
                    'motif_fin_engagement': line.motif_fin_engagement,
                    'code_media_engagement_modifie': line.code_media_engagement_modifie,
                    'montant': line.montant,
                    'periodicite': line.periodicite,
                    'statut_engagement': line.statut_engagement,
                    'date_premier_prelevement': line.date_premier_prelevement,
                    'date_dernier_prelevement': line.date_dernier_prelevement,
                    'montant_supplementaire_prochain_prelevement': line.montant_supplementaire_prochain_prelevement,
                    'date_prochain_prelevement': line.date_prochain_prelevement,
                    'nom_banque': line.nom_banque,
                    'numero_iban': line.numero_iban,
                    'code_bic': line.code_bic,
                    'code_identifiant_debiteur': line.code_identifiant_debiteur,
                    'reference_unique_mandat': line.reference_unique_mandat,
                    'identifiant_cb': line.identifiant_cb,
                    'date_expiration_cb': line.date_expiration_cb,
                    'remarques': line.remarques,
                    'id_matricule': line.id_matricule,
                    'datetime_import': self.datetime,
                }

                engagement = self.env['crm.alima.engagements'].create(engagement)
                nombre_de_engagements_importes += 1

            self.nombre_de_engagements_importes = nombre_de_engagements_importes
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
            self.env['crm.alima.engagements'].search([('datetime_import', '=', self.datetime)]).unlink()
        else:
            raise UserError(_("Roll back échoué"))
        self.state = 'draft'

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Peut pas supprimer un import en état %s.') % self.state)
        return super(IMPORTENGAGEMENT, self).unlink()


class EngagementTemplate(models.Model):
    _name = 'crm.alima.engagement.template'
    _description = 'Engagement Template'

    donateur = fields.Many2one('crm.alima.donateur', string='donateur', required=True)
    code_media_origine = fields.Many2one('crm.alima.code.media', string='code media origine', ondelete='restrict')
    code_media = fields.Many2one('crm.alima.code.media', string='code media', ondelete='restrict')

    date_accord_mandat = fields.Date(string='Date d\'accord du mandat')
    date_engagement_mandat = fields.Date(string='Date d\'engagement du mandat')
    date_fin_mandat = fields.Date(string='Date de fin du mandat')
    date_fin_engagement = fields.Date(string='Date fin engagement')
    motif_fin_engagement = fields.Selection(MOTIF_FIN_ENGAGEMENT, string='Motif fin d\'engagement')
    code_media_engagement_modifie = fields.Many2one('crm.alima.code.media', string='code media engagement modifié',
                                                    ondelete='restrict')
    montant = fields.Float(string="Montant")
    periodicite = fields.Selection(PERIODICITE, string='Periodicité')
    statut_engagement = fields.Selection(STATUT_ENGAGEMENT, string='Statut d\'engagement')
    date_premier_prelevement = fields.Date(string='Date premier prélèvement')
    date_dernier_prelevement = fields.Date(string='Date dernier prélèvement')
    montant_supplementaire_prochain_prelevement = fields.Float(
        string='Montant supplémentaire exceptionnel du prochain prélèvement')
    date_prochain_prelevement = fields.Date(string='Date prochain prélèvement')
    nom_banque = fields.Char(string='Nom banque')
    numero_iban = fields.Char(string='Numéro IBAN')
    code_bic = fields.Char(string='Code BIC')
    code_identifiant_debiteur = fields.Char(string='Code identifiant débiteur')
    reference_unique_mandat = fields.Char(string='Référence unique de mandat')
    identifiant_cb = fields.Char(string='Identifiant CB')
    date_expiration_cb = fields.Char(string='Date d\'expiration CB')
    remarques = fields.Char(string='Remarques')
    id_matricule = fields.Integer(string='Id Matricule')

    engagement_id = fields.Many2one('crm.alima.import.engagement', string='ENGAGEMENT')
