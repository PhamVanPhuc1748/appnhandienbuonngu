import flet as ft
import json
import os

# Đường dẫn file dữ liệu
JSON_FILE = "src/GUI/data/accounts.json"

class QuanLiTaiXe(ft.Column):
    def __init__(self):
        super().__init__(expand=True)
        self.drivers = []
        
        # Bảng dữ liệu
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Driver ID", weight="bold")),
                ft.DataColumn(ft.Text("Username", weight="bold")),
                ft.DataColumn(ft.Text("Họ Tên", weight="bold")),
                ft.DataColumn(ft.Text("Mật khẩu", weight="bold")),
                ft.DataColumn(ft.Text("Hành Động", weight="bold")),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            heading_row_color=ft.Colors.GREY_100,
            column_spacing=20,
        )

        # Giao diện chính (Header + Table)
        self.controls = [
            ft.Row([
                ft.Text("👥 Quản Lý Tài Xế", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "Thêm Tài Xế", 
                        icon=ft.Icons.PERSON_ADD, 
                        bgcolor=ft.Colors.GREEN, 
                        color=ft.Colors.WHITE,
                        on_click=self.open_add_dialog
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([self.data_table], scroll=ft.ScrollMode.AUTO),
                bgcolor=ft.Colors.WHITE, 
                border_radius=10, 
                padding=15, 
                expand=True
            )
        ]

    # --- HÀM HỆ THỐNG (Load/Save Data) ---
    def did_mount(self):
        # Hàm này chạy khi giao diện được load lên màn hình
        self.load_data()

    def load_data(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Lấy danh sách user_accounts, nếu không có thì trả về list rỗng
                    self.drivers = data.get("user_accounts", [])
            except Exception as e:
                print(f"Lỗi đọc file: {e}")
                self.drivers = []
        self.update_table()

    def save_data(self):
        # Đọc dữ liệu cũ để giữ lại admin_accounts (tránh mất tài khoản admin)
        current_data = {"admin_accounts": [], "user_accounts": []}
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except:
                pass
        
        # Cập nhật danh sách tài xế mới vào key user_accounts
        current_data["user_accounts"] = self.drivers
        
        # Tạo thư mục nếu chưa có
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        
        self.update_table()

    def update_table(self):
        self.data_table.rows.clear()
        for driver in self.drivers:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(driver.get("driver_id", "")))),
                        ft.DataCell(ft.Text(driver.get("username", ""))),
                        ft.DataCell(ft.Text(driver.get("name", ""))),
                        ft.DataCell(ft.Text("•" * len(driver.get("password", "")), size=14)), # Ẩn mật khẩu
                        ft.DataCell(
                            ft.Row([
                                # Nút Sửa
                                ft.IconButton(
                                    ft.Icons.EDIT, icon_color=ft.Colors.BLUE, tooltip="Sửa",
                                    on_click=lambda e, d=driver: self.open_edit_dialog(e, d)
                                ),
                                # Nút Thông báo
                                ft.IconButton(
                                    ft.Icons.NOTIFICATIONS, icon_color=ft.Colors.ORANGE, tooltip="Thông báo",
                                    on_click=lambda e, d=driver: self.open_notification_dialog(e, d)
                                ),
                                # Nút Xóa
                                ft.IconButton(
                                    ft.Icons.DELETE, icon_color=ft.Colors.RED, tooltip="Xóa",
                                    on_click=lambda e, d=driver: self.open_delete_dialog(e, d)
                                ),
                            ], spacing=0)
                        ),
                    ]
                )
            )
        self.update()

    # =========================================================================
    # 1. CHỨC NĂNG THÊM MỚI
    # =========================================================================
    def open_add_dialog(self, e):
        # Tạo các ô input mới
        txt_id = ft.TextField(label="Driver ID (Để trống tự sinh)", width=280)
        txt_user = ft.TextField(label="Username", width=280)
        txt_name = ft.TextField(label="Họ Tên", width=280)
        txt_pass = ft.TextField(label="Mật khẩu", password=True, can_reveal_password=True, width=280)

        def save_new(event):
            if not txt_user.value or not txt_name.value or not txt_pass.value:
                e.page.open(ft.SnackBar(ft.Text("Vui lòng điền đủ thông tin!"), bgcolor=ft.Colors.RED))
                return
            
            # Tự sinh ID nếu không nhập
            new_id = txt_id.value if txt_id.value else f"TX{len(self.drivers) + 1:03d}"
            
            new_driver = {
                "driver_id": new_id,
                "username": txt_user.value,
                "name": txt_name.value,
                "password": txt_pass.value
            }
            self.drivers.append(new_driver)
            self.save_data()
            e.page.close(dialog)
            e.page.open(ft.SnackBar(ft.Text("Đã thêm tài xế thành công!"), bgcolor=ft.Colors.GREEN))

        dialog = ft.AlertDialog(
            title=ft.Text("Thêm Tài Xế"),
            content=ft.Column([txt_id, txt_user, txt_name, txt_pass], height=300, tight=True),
            actions=[
                ft.TextButton("Hủy", on_click=lambda _: e.page.close(dialog)),
                ft.ElevatedButton("Lưu", on_click=save_new, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
            ]
        )
        e.page.open(dialog)

    # =========================================================================
    # 2. CHỨC NĂNG SỬA
    # =========================================================================
    def open_edit_dialog(self, e, driver):
        # Tạo input mới và điền dữ liệu cũ vào
        txt_id = ft.TextField(label="Driver ID", value=driver.get("driver_id"), read_only=True, width=280, bgcolor=ft.Colors.GREY_100)
        txt_user = ft.TextField(label="Username", value=driver.get("username"), read_only=True, width=280, bgcolor=ft.Colors.GREY_100)
        txt_name = ft.TextField(label="Họ Tên", value=driver.get("name"), width=280)
        txt_pass = ft.TextField(label="Mật khẩu", value=driver.get("password"), password=True, can_reveal_password=True, width=280)

        def save_edit(event):
            # Tìm và cập nhật trong list
            for d in self.drivers:
                if d["driver_id"] == driver["driver_id"]:
                    d["name"] = txt_name.value
                    d["password"] = txt_pass.value
                    break
            self.save_data()
            e.page.close(dialog)
            e.page.open(ft.SnackBar(ft.Text("Cập nhật thành công!"), bgcolor=ft.Colors.BLUE))

        dialog = ft.AlertDialog(
            title=ft.Text(f"Sửa: {driver.get('name')}"),
            content=ft.Column([txt_id, txt_user, txt_name, txt_pass], height=300, tight=True),
            actions=[
                ft.TextButton("Hủy", on_click=lambda _: e.page.close(dialog)),
                ft.ElevatedButton("Lưu", on_click=save_edit, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ]
        )
        e.page.open(dialog)

    # =========================================================================
    # 3. CHỨC NĂNG THÔNG BÁO (OA/Notification)
    # =========================================================================
    def open_notification_dialog(self, e, driver):
        txt_msg = ft.TextField(label="Nội dung thông báo", multiline=True, min_lines=3, width=400)
        
        # Mẫu tin nhắn có sẵn
        templates = {
            "Cảnh báo vi phạm": "Cảnh báo: Bạn đã vi phạm quy định tốc độ nhiều lần.",
            "Nhắc nhở bảo trì": "Nhắc nhở: Xe của bạn đã đến hạn bảo dưỡng định kỳ.",
            "Thông báo chung": "Thông báo: Hệ thống sẽ bảo trì vào 12h đêm nay."
        }

        # Khi chọn dropdown -> tự điền vào ô text
        def on_template_change(event):
            if dd_template.value:
                txt_msg.value = templates[dd_template.value]
                txt_msg.update()

        dd_template = ft.Dropdown(
            label="Chọn mẫu tin nhắn",
            width=400,
            options=[ft.dropdown.Option(k) for k in templates.keys()],
            on_change=on_template_change
        )

        def send_msg(event):
            if not txt_msg.value:
                txt_msg.error_text = "Vui lòng nhập nội dung!"
                txt_msg.update()
                return
            
            # Logic gửi tin (Ở đây chỉ in ra console, bạn có thể gọi API Zalo/Telegram sau này)
            print(f"--> Gửi tới ID {driver['driver_id']}: {txt_msg.value}")
            
            e.page.close(dialog)
            e.page.open(ft.SnackBar(ft.Text(f"Đã gửi thông báo tới {driver['name']}!"), bgcolor=ft.Colors.ORANGE))

        dialog = ft.AlertDialog(
            title=ft.Text(f"Gửi tin cho {driver.get('name')}"),
            content=ft.Column([
                ft.Text("Chọn mẫu hoặc tự nhập:", size=12, color=ft.Colors.GREY),
                dd_template, 
                ft.Container(height=10), 
                txt_msg
            ], height=280, tight=True),
            actions=[
                ft.TextButton("Hủy", on_click=lambda _: e.page.close(dialog)),
                ft.ElevatedButton("Gửi Ngay", icon=ft.Icons.SEND, on_click=send_msg, bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE)
            ]
        )
        e.page.open(dialog)

    # =========================================================================
    # 4. CHỨC NĂNG XÓA
    # =========================================================================
    def open_delete_dialog(self, e, driver):
        def confirm_delete(event):
            if driver in self.drivers:
                self.drivers.remove(driver)
                self.save_data()
                e.page.close(dialog)
                e.page.open(ft.SnackBar(ft.Text("Đã xóa tài xế thành công!"), bgcolor=ft.Colors.RED))

        dialog = ft.AlertDialog(
            title=ft.Text("Xác nhận xóa"),
            content=ft.Text(f"Bạn có chắc muốn xóa tài xế '{driver.get('name')}' ({driver.get('username')}) không?\nHành động này không thể hoàn tác."),
            actions=[
                ft.TextButton("Hủy", on_click=lambda _: e.page.close(dialog)),
                ft.ElevatedButton("Xóa", on_click=confirm_delete, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
            ]
        )
        e.page.open(dialog)