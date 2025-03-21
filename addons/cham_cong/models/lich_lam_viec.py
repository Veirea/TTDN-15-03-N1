from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import random

class LichLamViec(models.Model):
    _name = 'lich_lam_viec'
    _description = 'Lịch Đăng Ký Làm Việc'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên")
    ngay_lam_viec = fields.Date('Ngày Làm Việc', required=True, default=fields.Date.context_today)
    gio_bat_dau = fields.Float("Giờ Bắt Đầu", required=True)
    gio_ket_thuc = fields.Float("Giờ Kết Thúc", required=True)
    tong_gio = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio', store=True)
    so_buoi_di_muon = fields.Integer(string="Số buổi đi muộn", compute="_compute_thong_ke", store=True)  
    so_buoi_nghi = fields.Integer("Số Buổi Nghỉ", compute="_compute_thong_ke", store=True)
    chuc_vu = fields.Many2one("chuc_vu", string="Chức vụ")
    phong_ban = fields.Many2one('phong_ban', string="Phòng Ban")
    
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
        """Tính tổng giờ làm việc"""
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
        """Kiểm tra ngày làm việc không được là ngày trong quá khứ"""
        for record in self:
            if record.ngay_lam_viec < fields.Date.today():
                raise ValidationError("Không thể đăng ký làm việc vào ngày trong quá khứ!")

    @api.onchange('ca_lam_viec')
    def _onchange_ca_lam_viec(self):
        """Thay đổi giờ bắt đầu và kết thúc theo ca làm việc"""
        if self.ca_lam_viec == 'sang':
            self.gio_bat_dau = 8.00
            self.gio_ket_thuc = 12.00
        elif self.ca_lam_viec == 'chieu':
            self.gio_bat_dau = 13.00
            self.gio_ket_thuc = 17.00
        elif self.ca_lam_viec == 'toi':
            self.gio_bat_dau = 18.00
            self.gio_ket_thuc = 22.00

    @api.onchange('nhan_vien_id')
    def _onchange_nhan_vien(self):
        """Thay đổi chức vụ và phòng ban theo nhân viên"""
        if self.nhan_vien_id:
            self.chuc_vu = self.nhan_vien_id.chuc_vu
            self.phong_ban = self.nhan_vien_id.phong_ban
    
    @api.model
    def auto_duyet_lich_lam_viec(self):
        """Tự động duyệt hoặc từ chối lịch làm việc sau 1 phút"""
        thoi_gian_hien_tai = fields.Datetime.now()
        lich_cho_duyet = self.search([
            ('trang_thai', '=', 'cho_duyet'),
            ('create_date', '!=', False)
        ])

        for lich in lich_cho_duyet:
            if (thoi_gian_hien_tai - lich.create_date) >= timedelta(minutes=1):
                # 80% Được duyệt, 20% bị từ chối
                if random.random() < 0.8:
                    lich.trang_thai = 'da_duyet'
                    self.env['bang_diem_danh'].create_attendance_record(lich)
                else:
                    lich.trang_thai = 'tu_choi'

    @api.model
    def get_thong_ke_lich_lam_viec(self):
        """Lấy thống kê lịch làm việc"""
        return {
            'tong_dang_ky': self.search_count([]),
            'da_duyet': self.search_count([('trang_thai', '=', 'da_duyet')]),
            'tu_choi': self.search_count([('trang_thai', '=', 'tu_choi')]),
        }
    
    @api.depends('nhan_vien_id')
    def _compute_thong_ke(self):
        """Tính số buổi đi muộn và số buổi nghỉ"""
        for record in self:
            if not record.nhan_vien_id:
                record.so_buoi_di_muon = 0
                record.so_buoi_nghi = 0
                continue
            
            record.so_buoi_di_muon = self.env['lich_lam_viec'].search_count([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('gio_bat_dau', '>', 8.5)
            ])

            record.so_buoi_nghi = sum(self.env['don_xin_phep'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('trang_thai', '=', 'da_duyet')
            ]).mapped('so_ngay'))
