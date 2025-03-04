from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DonXinPhep(models.Model):
    _name = "don_xin_phep"
    _description = "Đơn Xin Phép"

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên", required=True)
    loai_phep = fields.Selection([
        ('nghi_phep', 'Nghỉ Phép'),
        ('nghi_om', 'Nghỉ Ốm'),
        ('cong_tac', 'Công Tác')
    ], string="Loại Phép", required=True)
    
    ngay_bat_dau = fields.Date("Ngày Bắt Đầu", required=True)
    ngay_ket_thuc = fields.Date("Ngày Kết Thúc", required=True)
    so_ngay = fields.Integer("Số Ngày", compute="_compute_so_ngay", store=True)

    ly_do = fields.Text("Lý Do")
    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ Duyệt'),
        ('da_duyet', 'Đã Duyệt'),
        ('tu_choi', 'Từ Chối')
    ], string="Trạng Thái", default='cho_duyet')

    nguoi_duyet_id = fields.Many2one('res.users', string="Người Duyệt")

    @api.depends('ngay_bat_dau', 'ngay_ket_thuc')
    def _compute_so_ngay(self):
        for record in self:
            if record.ngay_bat_dau and record.ngay_ket_thuc:
                record.so_ngay = (record.ngay_ket_thuc - record.ngay_bat_dau).days + 1
            else:
                record.so_ngay = 0

    def auto_xu_ly_don_xin_phep(self):
        for record in self.search([('trang_thai', '=', 'cho_duyet')]):
            if record.so_ngay <= 7:
                record.trang_thai = 'da_duyet'
            else:
                record.trang_thai = 'tu_choi'
