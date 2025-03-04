from odoo import models, fields, api
from datetime import datetime, time

class BangDiemDanh(models.Model):
    _name = 'bang_diem_danh'
    _description = 'Bảng Điểm Danh'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên")
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string="Mã Định Danh", store=True, readonly=True)

    ngay_lam_viec = fields.Date('Ngày Làm Việc', required=True, default=fields.Date.context_today)
    gio_check_in = fields.Datetime('Giờ Check-in')
    gio_check_out = fields.Datetime('Giờ Check-out')
    tong_gio_lam = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio_lam', store=True)

    lich_lam_viec_id = fields.Many2one('lich_lam_viec', string="Lịch Làm Việc",domain="[('nhan_vien_id', '=', nhan_vien_id), ('ngay_lam_viec', '=', ngay_lam_viec)]")
    ca_lam_viec = fields.Selection(related='lich_lam_viec_id.ca_lam_viec', string="Ca Làm Việc", store=True)
    gio_yeu_cau_check_in = fields.Datetime('Giờ Yêu Cầu Check-in', related='lich_lam_viec_id.gio_yeu_cau_check_in', store=True)
    check_in_status = fields.Selection([('dung_gio', 'Đúng Giờ'), ('muon', 'Muộn')], string="Trạng Thái Check-in", compute='_compute_check_in_status', store=True)

    @api.depends('gio_check_in', 'gio_yeu_cau_check_in')
    def _compute_check_in_status(self):
        for rec in self:
            if rec.gio_check_in and rec.gio_yeu_cau_check_in:
                if rec.gio_check_in <= rec.gio_yeu_cau_check_in:
                    rec.check_in_status = 'dung_gio'
                else:
                    rec.check_in_status = 'muon'
            else:
                rec.check_in_status = False

    @api.depends('gio_check_in', 'gio_check_out')
    def _compute_tong_gio_lam(self):
        for rec in self:
            if rec.gio_check_in and rec.gio_check_out:
                delta = rec.gio_check_out - rec.gio_check_in
                rec.tong_gio_lam = delta.total_seconds() / 3600
            else:
                rec.tong_gio_lam = 0.0

    

