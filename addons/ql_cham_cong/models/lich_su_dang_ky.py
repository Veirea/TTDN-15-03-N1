from odoo import fields, api, models
class LichSuDangKy(models.Model):
    _name = 'lich_su_dang_ky'
    _description = 'Lịch sử đăng ký ca làm việc'

    lich_lam_viec_id = fields.Many2one('lich_lam_viec', string="Lịch Làm Việc", required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", related='lich_lam_viec_id.nhan_vien_id')
    ca_lam_viec = fields.Selection(related='lich_lam_viec_id.ca_lam_viec', string="Ca Làm Việc")
    ngay_lam_viec = fields.Date(related='lich_lam_viec_id.ngay_lam_viec', string="Ngày Làm Việc")
    trang_thai = fields.Selection(related='lich_lam_viec_id.trang_thai', string="Trạng Thái")
    ghi_chu = fields.Text(string="Ghi Chú")