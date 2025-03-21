from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class DiemDanh(models.Model):
    _name = 'diem_danh'
    _description = 'Bảng Điểm Danh'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên", required=True)
    ngay_lam_viec = fields.Date(related='lich_lam_viec_id.ngay_lam_viec', store=True)
    gio_check_in = fields.Datetime(string="Giờ Check-In")
    gio_check_out = fields.Datetime(string="Giờ Check-Out")
    lich_lam_viec_id = fields.Many2one(
        'lich_lam_viec', string="Lịch Làm Việc",
        domain="[('nhan_vien_id', '=', nhan_vien_id), ('trang_thai', '=', 'da_duyet')]"
    )
    ca_lam_viec = fields.Selection(related='lich_lam_viec_id.ca_lam_viec', string="Ca Làm Việc", store=True)
    trang_thai_diem_danh = fields.Selection(
        [('chua_diem_danh', 'Chưa Điểm Danh'),
         ('som', 'Sớm'),
         ('dung_gio', 'Đúng Giờ'),
         ('muon', 'Muộn')],
        string="Trạng Thái",
        default='chua_diem_danh'
    )

    @api.model
    def get_start_time(self):
        """
        Lấy giờ bắt đầu ca làm việc theo từng loại ca.
        """
        ca_gio_bat_dau = {
            'sang': "08:00:00",
            'chieu': "13:00:00",
            'toi': "18:00:00"
        }
        if self.ca_lam_viec and self.ca_lam_viec in ca_gio_bat_dau:
            ngay_gio_bat_dau = f"{self.ngay_lam_viec} {ca_gio_bat_dau[self.ca_lam_viec]}"
            return datetime.strptime(ngay_gio_bat_dau, "%Y-%m-%d %H:%M:%S")
        return None

    def check_in_out(self):
        """
        - Check-In: Ghi nhận thời gian thực tế và xác định trạng thái (Sớm, Đúng Giờ, Muộn).
        - Check-Out: Ghi nhận thời gian rời đi.
        """
        for rec in self:
            now = fields.Datetime.now()

            if not rec.gio_check_in:
                start_time = rec.get_start_time()
                if start_time:
                    if now < start_time:
                        rec.trang_thai_diem_danh = "som"
                    elif now == start_time:
                        rec.trang_thai_diem_danh = "dung_gio"
                    else:
                        rec.trang_thai_diem_danh = "muon"
                
                rec.gio_check_in = now
            elif not rec.gio_check_out:
                rec.gio_check_out = now
            else:
                raise UserError("Bạn đã hoàn thành điểm danh hôm nay!")

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
