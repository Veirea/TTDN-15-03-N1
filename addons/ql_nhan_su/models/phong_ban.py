from odoo import models, fields

class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin phòng ban'
    _rec_name ='ten_phong_ban'

    ten_phong_ban = fields.Char("Tên Phòng Ban", required=True)
    nhan_vien_ids = fields.One2many("nhan_vien","phong_ban_id", string="Nhân viên")