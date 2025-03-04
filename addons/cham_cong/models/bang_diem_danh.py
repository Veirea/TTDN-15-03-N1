from odoo import models, fields, api
from datetime import datetime, timedelta, time

class BangDiemDanh(models.Model):
    _name = 'bang_diem_danh'
    _description = 'Bảng Điểm Danh'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên")
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string="Mã Định Danh", store=True, readonly=True)

    ngay_lam_viec = fields.Date('Ngày Làm Việc', required=True, default=fields.Date.context_today)
    gio_check_in = fields.Datetime('Giờ Check-in')
    gio_check_out = fields.Datetime('Giờ Check-out')
    tong_gio_lam = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio_lam', store=True)

    lich_lam_viec_id = fields.Many2one('lich_lam_viec', string="Lịch Làm Việc", domain="[('nhan_vien_id', '=', nhan_vien_id), ('ngay_lam_viec', '=', ngay_lam_viec)]")
    ca_lam_viec = fields.Selection(related='lich_lam_viec_id.ca_lam_viec', string="Ca Làm Việc", store=True)

    trang_thai_cham_cong = fields.Selection([
        ('dung_gio', 'Đúng Giờ'),
        ('muon', 'Muộn'),
        ('som', 'Sớm'),
    ], string="Trạng Thái Chấm Công", compute='_compute_trang_thai_cham_cong', store=True)

    @api.depends('gio_check_in', 'lich_lam_viec_id.gio_bat_dau')
    def _compute_trang_thai_cham_cong(self):
        for rec in self:
            if rec.gio_check_in and rec.lich_lam_viec_id:
                gio_check_in_thuc_te = rec.gio_check_in.time()

                gio_bat_dau = rec.lich_lam_viec_id.gio_bat_dau
                gio_bat_dau_hours = int(gio_bat_dau)
                gio_bat_dau_minutes = int((gio_bat_dau - gio_bat_dau_hours) * 60)
                gio_bat_dau_ca = time(hour=gio_bat_dau_hours, minute=gio_bat_dau_minutes)

                if gio_check_in_thuc_te < gio_bat_dau_ca:  
                    rec.trang_thai_cham_cong = 'muon'
                elif gio_check_in_thuc_te == gio_bat_dau_ca:  
                    rec.trang_thai_cham_cong = 'dung_gio'
                else:  
                    rec.trang_thai_cham_cong = 'som'
            else:
                rec.trang_thai_cham_cong = False


    @api.depends('nhan_vien_id', 'ngay_lam_viec')
    def _compute_lich_lam_viec_id(self):
        for rec in self:
            if rec.nhan_vien_id and rec.ngay_lam_viec:
                lich_lam = self.env['lich_lam_viec'].search([
                    ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                    ('ngay_lam_viec', '=', rec.ngay_lam_viec),
                    ('trang_thai', '=', 'da_duyet') 
                ], limit=1)
                rec.lich_lam_viec_id = lich_lam.id if lich_lam else False
            else:
                rec.lich_lam_viec_id = False

    @api.depends('gio_check_in', 'gio_check_out')
    def _compute_tong_gio_lam(self):
        for rec in self:
            if rec.gio_check_in and rec.gio_check_out:
                duration = rec.gio_check_out - rec.gio_check_in
                rec.tong_gio_lam = duration.total_seconds() / 3600  
            else:
                rec.tong_gio_lam = 0.0