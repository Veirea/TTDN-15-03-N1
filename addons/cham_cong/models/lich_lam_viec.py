from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class LichLamViec(models.Model):
    _name = 'lich_lam_viec'
    _description = 'Lịch Đăng Ký Làm Việc'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên")
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string="Mã Định Danh", store=True, readonly=True)

    ngay_lam_viec = fields.Date('Ngày Làm Việc', required=True, default=fields.Date.context_today)
    
    gio_bat_dau = fields.Float("Giờ Bắt Đầu", required=True)
    gio_ket_thuc = fields.Float("Giờ Kết Thúc", required=True)
    tong_gio = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio', store=True)
    gio_yeu_cau_check_in = fields.Datetime('Giờ Yêu Cầu Check in')

    ca_lam_viec = fields.Selection([
        ('sang', 'Ca Sáng (08:00 - 12:00)'),
        ('chieu', 'Ca Chiều (13:00 - 17:00)'),
        ('toi', 'Ca Tối (18:00 - 22:00)')
    ], string="Ca Làm Việc", required=True)

    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ Duyệt'),
        ('da_duyet', 'Đã Duyệt'),
        ('tu_choi', 'Từ Chối')
    ], string="Trạng Thái", default="cho_duyet")

    @api.depends('gio_bat_dau', 'gio_ket_thuc')
    def _compute_tong_gio(self):
        for record in self:
            if record.gio_bat_dau and record.gio_ket_thuc and record.gio_ket_thuc > record.gio_bat_dau:
                record.tong_gio = record.gio_ket_thuc - record.gio_bat_dau
            else:
                record.tong_gio = 0.0
        

    @api.constrains('ngay_lam_viec')
    def _check_ngay_lam_viec(self):
        for record in self:
            if record.ngay_lam_viec < fields.Date.today():
                raise ValidationError("Không thể đăng ký làm việc vào ngày trong quá khứ!")

    @api.onchange('ca_lam_viec')
    def _onchange_ca_lam_viec(self):
        if self.ca_lam_viec == 'sang':
            self.gio_bat_dau = 8.0
            self.gio_ket_thuc = 12.0
        elif self.ca_lam_viec == 'chieu':
            self.gio_bat_dau = 13.0
            self.gio_ket_thuc = 17.0
        elif self.ca_lam_viec == 'toi':
            self.gio_bat_dau = 18.0
            self.gio_ket_thuc = 22.0
    @api.model
    def auto_duyet_lich_lam_viec(self):
        thoi_gian_hien_tai = fields.Datetime.now()
        lich_cho_duyet = self.search([('trang_thai', '=', 'cho_duyet')])

        for lich in lich_cho_duyet:
            if lich.create_date and (thoi_gian_hien_tai - lich.create_date) >= timedelta(minutes=1):
                if fields.Datetime.now().second % 2 == 0:
                    lich.trang_thai = 'da_duyet'
                else:
                    lich.trang_thai = 'tu_choi'