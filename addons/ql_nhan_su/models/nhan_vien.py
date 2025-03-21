from odoo import models, fields, api

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten_dem = fields.Char("Họ Tên Đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ Và Tên", compute="_compute_ho_va_ten", store=True )
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    

    gioi_tinh = fields.Selection([
        ('Nam', 'Nam'),
        ('Nu', 'Nữ'),
        ('Khac', 'Khác'),
    ], string="Giới tính", default='Nam')

    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng Ban")
    # lich_lam_viec_ids = fields.One2many('lich_lam_viec', 'nhan_vien_id', string="Lịch làm việc")

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = record.ho_ten_dem + ' ' + record.ten

    @api.depends("hop_dong_id")
    def _compute_hop_dong(self):
        for rec in self:
            hop_dong = self.env["hop_dong"].search([
                ("nhan_vien_id", "=", rec.id),
                ("trang_thai", "=", "hieu_luc")
            ], limit=1, order="ngay_bat_dau desc")

            rec.hop_dong_id = hop_dong.id if hop_dong else False

    @api.onchange("ten", "ho_ten_dem")
    def _default_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                chu_cai_dau = '' . join([tu[0][0] for tu in record.ho_ten_dem.lower().split()])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_dau
    
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã Định Danh Phải Là Duy Nhất')
    ]