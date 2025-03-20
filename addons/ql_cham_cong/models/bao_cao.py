from odoo import models, fields, api
from datetime import datetime

class BaoCao(models.Model):
    _name = "bao_cao"
    _description = "Báo Cáo Chấm Công"

    name = fields.Char(string="Tên Báo Cáo", required=True)
    nam = fields.Integer(string="Năm")
    thang = fields.Integer(string="Tháng")
    nhan_vien_ids = fields.One2many("bao_cao_line", "bao_cao_id", string="Danh Sách Nhân Viên")

    @api.model
    def create(self, vals):
        """Tự động tạo dữ liệu báo cáo"""
        record = super(BaoCao, self).create(vals)
        record.tinh_toan_du_lieu()
        return record

    def tinh_toan_du_lieu(self):
        """Tính toán dữ liệu từ lịch làm việc, điểm danh, đơn xin phép"""
        nhan_vien_data = {}

        # Lọc dữ liệu lịch làm việc, điểm danh, đơn xin phép
        lich_lam_viec = self.env["lich_lam_viec"].search([
            ("ngay", ">=", f"{self.nam}-{self.thang}-01"),
            ("ngay", "<", f"{self.nam}-{self.thang + 1}-01")
        ])
        diem_danh = self.env["diem_danh"].search([
            ("ngay", ">=", f"{self.nam}-{self.thang}-01"),
            ("ngay", "<", f"{self.nam}-{self.thang + 1}-01")
        ])
        don_xin_phep = self.env["don_xin_phep"].search([
            ("ngay", ">=", f"{self.nam}-{self.thang}-01"),
            ("ngay", "<", f"{self.nam}-{self.thang + 1}-01")
        ])

        # Tổng hợp dữ liệu
        for ca in lich_lam_viec:
            nhan_vien_data.setdefault(ca.nhan_vien_id.id, {"tong_so_ca": 0, "tong_ngay_nghi": 0, "so_don_nghi_phep": 0})
            nhan_vien_data[ca.nhan_vien_id.id]["tong_so_ca"] += 1

        for dd in diem_danh:
            if dd.co_mat:
                nhan_vien_data.setdefault(dd.nhan_vien_id.id, {"tong_so_ca": 0, "tong_ngay_nghi": 0, "so_don_nghi_phep": 0})
            else:
                nhan_vien_data[dd.nhan_vien_id.id]["tong_ngay_nghi"] += 1

        for don in don_xin_phep:
            nhan_vien_data.setdefault(don.nhan_vien_id.id, {"tong_so_ca": 0, "tong_ngay_nghi": 0, "so_don_nghi_phep": 0})
            nhan_vien_data[don.nhan_vien_id.id]["so_don_nghi_phep"] += 1

        # Xóa dữ liệu cũ
        self.nhan_vien_ids.unlink()

        # Tạo bản ghi mới
        bao_cao_lines = []
        for nv_id, data in nhan_vien_data.items():
            bao_cao_lines.append((0, 0, {
                "nhan_vien_id": nv_id,
                "tong_so_ca": data["tong_so_ca"],
                "tong_ngay_nghi": data["tong_ngay_nghi"],
                "so_don_nghi_phep": data["so_don_nghi_phep"]
            }))

        self.write({"nhan_vien_ids": bao_cao_lines})

class BaoCaoLine(models.Model):
    _name = "bao_cao_line"
    _description = "Chi Tiết Báo Cáo Chấm Công"

    bao_cao_id = fields.Many2one("bao_cao", string="Báo Cáo", ondelete="cascade")
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân Viên", required=True)
    tong_so_ca = fields.Integer(string="Tổng Số Ca Làm")
    tong_ngay_nghi = fields.Integer(string="Tổng Ngày Nghỉ")
    so_don_nghi_phep = fields.Integer(string="Số Đơn Nghỉ Phép")
