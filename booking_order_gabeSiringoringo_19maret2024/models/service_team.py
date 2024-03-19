from odoo import fields, models

class ServiceTeam(models.Model):
    _name = 'service.team'
    _description = 'Service Team'
    
    name = fields.Char(
        string="Team Name",
        required=True,
    )
    team_leader = fields.Many2one(
        'res.users',
        string="Team Leader",
        required=True,
    )
    team_members = fields.Many2many(
        'res.users',
        string="Team Members",
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )