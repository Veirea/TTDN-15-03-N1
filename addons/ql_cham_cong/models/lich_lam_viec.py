from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import random

class LichLamViec(models.Model):
    _name = 'lich_lam_viec'
    _description = 'Quản lý lịch làm việc của nhân viên'

    ca_lam_viec = fields.Selection([
        ('sang', 'Ca Sáng (08:00 - 12:00)'),
        ('chieu', 'Ca Chiều (13:00 - 17:00)'),
        ('toi', 'Ca Tối (18:00 - 22:00)')
    ], string="Ca Làm Việc", required=True, tracking=True)
    
    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ Duyệt'),
        ('da_duyet', 'Đã Duyệt'),
        ('tu_choi', 'Từ Chối')
    ], string="Trạng Thái", default="cho_duyet", tracking=True)

    loai_cong_viec = fields.Selection([
    ('van_phong', 'Làm việc tại văn phòng'),
    ('tu_xa', 'Làm việc từ xa'),
    ('hop', 'Họp'),
    ('dao_tao', 'Đào tạo'),
    ('khac', 'Khác'),
    ], string="Loại công việc", default="van_phong")

    lap_lai = fields.Selection([
    ('khong', 'Không lặp lại'),
    ('hang_tuan', 'Hàng tuần'),
    ('hang_thang', 'Hàng tháng'),
    ], string="Lặp lại", default="khong")
    
    muc_do_uu_tien = fields.Selection([
    ('cao', 'Cao'),
    ('trung_binh', 'Trung bình'),
    ('thap', 'Thấp'),
    ], string="Mức độ ưu tiên", default="trung_binh")
    
    ngay_ket_thuc_lap_lai = fields.Date(string="Ngày kết thúc lặp lại")
    ngay_lam_viec = fields.Date(string="Ngày làm việc", default=fields.Date.today(), required=True)
    gio_bat_dau = fields.Float("Giờ Bắt Đầu" )
    gio_ket_thuc = fields.Float("Giờ Kết Thúc")
    tong_gio = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio', store=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên")
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", compute='_compute_phong_ban_va_chuc_vu', store=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", compute='_compute_phong_ban_va_chuc_vu', store=True)
    mo_ta = fields.Text(string="Mô tả")


    @api.depends('gio_bat_dau', 'gio_ket_thuc')
    def _compute_tong_gio(self):
        for record in self:
            if record.gio_bat_dau and record.gio_ket_thuc:
                if record.gio_ket_thuc >= record.gio_bat_dau:
                    record.tong_gio = record.gio_ket_thuc - record.gio_bat_dau
                else:
                    record.tong_gio = (24 - record.gio_bat_dau) + record.gio_ket_thuc
            else:
                record.tong_gio = 0.00

    @api.constrains('ngay_lam_viec')
    def _check_ngay_lam_viec(self):
        for record in self:
            if record.ngay_lam_viec < fields.Date.today():
                raise ValidationError("Không thể đăng ký làm việc vào ngày trong quá khứ!")
            
    @api.onchange('ca_lam_viec')
    def _onchange_ca_lam_viec(self):
        if self.ca_lam_viec == 'sang':
            self.gio_bat_dau = 8.00
            self.gio_ket_thuc = 12.00
        elif self.ca_lam_viec == 'chieu':
            self.gio_bat_dau = 13.00
            self.gio_ket_thuc = 17.00
        elif self.ca_lam_viec == 'toi':
            self.gio_bat_dau = 18.00
            self.gio_ket_thuc = 22.00
    

    @api.depends('nhan_vien_id')
    def _compute_phong_ban_va_chuc_vu(self):
        for record in self:
            if record.nhan_vien_id:
                record.phong_ban_id = record.nhan_vien_id.phong_ban_id
                record.chuc_vu_id = record.nhan_vien_id.chuc_vu_id
            else:
                record.phong_ban_id = False
                record.chuc_vu_id = False
    


    @api.model
    def create(self, vals):
        """Tự động duyệt hoặc từ chối ngay khi tạo"""
        record = super(LichLamViec, self).create(vals)
        record.trang_thai = random.choice(['da_duyet', 'tu_choi'])  
        return record
    

    