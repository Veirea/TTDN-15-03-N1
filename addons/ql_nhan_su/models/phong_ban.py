from odoo import models, fields, api

class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin phòng ban'
    _rec_name ='ten_phong_ban'

    ten_phong_ban = fields.Char("Tên Phòng Ban", required=True)
    nhan_vien_ids = fields.One2many("nhan_vien","phong_ban_id", string="Nhân viên")
    # so_luong_lich_lam_viec = fields.Integer(string='Số lượng lịch làm việc', compute='_tinh_so_luong_lich_lam_viec', store=True)

    # @api.depends('nhan_vien_ids.lich_lam_viec_ids')
    # def _tinh_so_luong_lich_lam_viec(self):
    #     for phong_ban in self:
    #         # Lấy tất cả lịch làm việc của các nhân viên trong phòng ban
    #         lich_lam_viec = self.env['lich_lam_viec'].search([
    #             ('nhan_vien_id', 'in', phong_ban.nhan_vien_ids.ids),
    #         ])
    #         phong_ban.so_luong_lich_lam_viec = len(lich_lam_viec)