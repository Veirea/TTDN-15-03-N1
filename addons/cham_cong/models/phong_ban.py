from odoo import models, fields

class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin phòng ban'
    _rec_name ='ten_phong_ban'

    ten_phong_ban = fields.Char("Tên Phòng Ban", required=True)
    nhan_vien_ids = fields.One2many("nhan_vien","phong_ban", string="Nhân viên")
    # lich_lam_viec_ids = fields.One2many('lich_lam_viec', "phong_ban", string="Lịch Làm Việc")