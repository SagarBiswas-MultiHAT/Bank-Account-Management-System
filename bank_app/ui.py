# USER NAME & PASSWORD: In DATABASE

from pathlib import Path
import tkinter as tk
from tkinter import *

from bank_app.config import DB_PATH, MAX_TRANSACTION
from bank_app.errors import BusinessRuleError, ConflictError, NotFoundError, ValidationError
from bank_app.services import BankService
from bank_app.validation import parse_date, validate_mobile

ASSETS_DIR = Path(__file__).resolve().parent.parent / "images"
service = BankService.create_default(DB_PATH)


def asset_path(filename: str) -> str:
    return str(ASSETS_DIR / filename)


def center_window(window, width: int, height: int) -> None:
    """Center a Tk window on the primary display. Falls back to (0,0) on error."""
    try:
        window.update_idletasks()
        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        window.geometry(f"{width}x{height}+0+0")


def _safe_admin_message(message: str) -> None:
    if "Frame1_1_2" in globals():
        try:
            adminMenu.printMessage_outside(message)
        except Exception:
            pass


def _safe_customer_message(message: str) -> None:
    if "Frame1_1_2" in globals():
        try:
            customerMenu.printMessage_outside(message)
        except Exception:
            pass


# Backend python functions code starts:
def is_valid(customer_account_number):
    try:
        return not service.customer_exists(customer_account_number)
    except ValidationError:
        return False


def check_leap(year):
    return ((int(year) % 4 == 0) and (int(year) % 100 != 0)) or (int(year) % 400 == 0)


def check_date(date_value):
    try:
        parse_date(date_value, "Date of birth")
        return True
    except ValidationError:
        return False


def is_valid_mobile(mobile_number):
    try:
        validate_mobile(mobile_number)
        return True
    except ValidationError:
        return False


def display_account_summary(identity, choice):  # choice 1 for full summary; choice 2 for only account balance.
    try:
        summary = service.get_customer_summary(identity)
    except NotFoundError:
        print("\n# No account associated with the entered account number exists! #")
        return ""

    if choice == 1:
        output_message = (
            f"Account number : {summary['account_number']}\n"
            f"Current balance : {summary['balance']}\n"
            f"Date of account creation : {summary['created_at']}\n"
            f"Name of account holder : {summary['name']}\n"
            f"Type of account : {summary['account_type']}\n"
            f"Date of Birth : {summary['date_of_birth']}\n"
            f"Mobile number : {summary['mobile']}\n"
            f"Gender : {summary['gender']}\n"
            f"Nationality : {summary['nationality']}\n"
            f"KYC : {summary['kyc_document']}\n"
        )
    else:
        output_message = f"Current balance : {summary['balance']}\n"

    return output_message


def delete_customer_account(identity, choice):  # choice 1 for admin, choice 2 for customer
    try:
        service.delete_customer(identity)
    except NotFoundError:
        output_message = "Account not found !"
        if choice == 1:
            _safe_admin_message(output_message)
        print(output_message)
        return

    output_message = "Account with account no." + str(identity) + " closed successfully!"
    if choice == 1:
        _safe_admin_message(output_message)
    print(output_message)


def delete_admin_account(identity):
    try:
        service.delete_admin(identity, current_admin_id=admin_idNO)
    except NotFoundError:
        output_message = "Account not found :("
        _safe_admin_message(output_message)
        print(output_message)
        return
    except BusinessRuleError as exc:
        output_message = str(exc)
        _safe_admin_message(output_message)
        print(output_message)
        return

    output_message = "Account with account id " + identity + " closed successfully!"
    print(output_message)
    _safe_admin_message(output_message)


def change_PIN(identity, new_PIN):
    try:
        service.change_pin(identity, new_PIN)
    except (NotFoundError, ValidationError) as exc:
        output_message = str(exc)
        _safe_customer_message(output_message)
        print(output_message)
        return

    output_message = "PIN changed successfully."
    _safe_customer_message(output_message)
    print(output_message)


def _coerce_amount(amount) -> str:
    if isinstance(amount, (int, float)):
        return str(int(amount))
    return str(amount)


def transaction(identity, amount, choice):  # choice 1 for deposit; choice 2 for withdraw
    amount_str = _coerce_amount(amount)
    try:
        if choice == 1:
            return service.deposit(identity, amount_str)
        return service.withdraw(identity, amount_str)
    except BusinessRuleError as exc:
        if "Minimum balance" in str(exc):
            return -1
        print(str(exc))
        return -1
    except (NotFoundError, ValidationError) as exc:
        print(str(exc))
        return -1


def check_credentials(identity, password, choice, admin_access):
    try:
        if choice == 1:
            if password == "DO_NOT_CHECK_ADMIN":
                return service.admin_exists(identity)
            return service.authenticate_admin(identity, password)
        if password == "DO_NOT_CHECK":
            return service.customer_exists(identity)
        return service.authenticate_customer(identity, password)
    except ValidationError:
        return False


def authenticate_customer_identifier(identity, password):
    try:
        return service.authenticate_customer_with_identifier(identity, password)
    except ValidationError:
        return None


# Backend python functions code ends.

# Tkinter GUI code starts :  
class welcomeScreen:
    def __init__(self, window=None):
        self.master = window
        # center the main window on the user's display
        width = 600
        height = 450
        try:
            window.update_idletasks()
            screen_w = window.winfo_screenwidth()
            screen_h = window.winfo_screenheight()
            x = (screen_w - width) // 2
            y = (screen_h - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            # fallback to fixed geometry if something goes wrong
            window.geometry("600x450+383+106")
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Welcome to New BANK")
        p1 = PhotoImage(file=asset_path("bank1.png"))
        window.iconphoto(True, p1)
        window.configure(background="#023047")
        window.configure(cursor="arrow")

        self.Canvas1 = tk.Canvas(window, background="#ffff00", borderwidth="0", insertbackground="black",
                                 relief="ridge",
                                 selectbackground="blue", selectforeground="white")
        self.Canvas1.place(relx=0.190, rely=0.228, relheight=0.496, relwidth=0.622)

        self.Button1 = tk.Button(self.Canvas1, command=self.selectEmployee, activebackground="#ececec",
                                 activeforeground="#000000", background="#023047", disabledforeground="#a3a3a3",
                                 foreground="#fbfbfb", borderwidth="0", highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0",
                                 text='''EMPLOYEE''')
        self.Button1.configure(font="-family {Segoe UI} -size 10 -weight bold")
        self.Button1.place(relx=0.161, rely=0.583, height=24, width=87)

        self.Button2 = tk.Button(self.Canvas1, command=self.selectCustomer, activebackground="#ececec",
                                 activeforeground="#000000", background="#023047", disabledforeground="#a3a3a3",
                                 foreground="#f9f9f9", borderwidth="0", highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0",
                                 text='''CUSTOMER''')
        self.Button2.configure(font="-family {Segoe UI} -size 10 -weight bold")
        self.Button2.place(relx=0.617, rely=0.583, height=24, width=87)

        self.Label1 = tk.Label(self.Canvas1, background="#ffff00", disabledforeground="#a3a3a3",
                               font="-family {Segoe UI} -size 13 -weight bold", foreground="#000000",
                               text='''Please select your role''')
        self.Label1.place(relx=0.241, rely=0.224, height=31, width=194)


    def selectCustomer(self):
        self.master.withdraw()
        CustomerLogin(Toplevel(self.master))

    def selectEmployee(self):
        self.master.withdraw()
        adminLogin(Toplevel(self.master))


class Error:
    def __init__(self, window=None):
        global master
        master = window
        center_window(window, 411, 117)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Error")
        window.configure(background="#f2f3f4")

        global Label2

        self.Button1 = tk.Button(window, background="#d3d8dc", borderwidth="1", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 9", foreground="#000000", highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text='''OK''', command=self.goback)
        self.Button1.place(relx=0.779, rely=0.598, height=24, width=67)

        global _img0
        _img0 = tk.PhotoImage(file=asset_path("error_image.png"))
        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               image=_img0, text='''Label''')
        self.Label1.place(relx=0.024, rely=0.0, height=81, width=84)

    def setMessage(self, message_shown):
        # Clear any previous error message widgets we created
        try:
            for w in master.winfo_children():
                if getattr(w, "_is_error_message", False):
                    w.destroy()
        except Exception:
            pass

        # Create a wrapped, left-justified label so long messages display correctly
        Label2 = tk.Label(
            master,
            background="#f2f3f4",
            disabledforeground="#a3a3a3",
            font="-family {Segoe UI} -size 10",
            foreground="#000000",
            text=message_shown,
            wraplength=300,
            justify="left",
            anchor="w",
        )
        # mark widget so we can remove it later if needed
        Label2._is_error_message = True
        # place to occupy most of the dialog to avoid clipping
        Label2.place(relx=0.22, rely=0.12, relwidth=0.72, relheight=0.7)

    def goback(self):
        master.withdraw()


class adminLogin:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 743, 494)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Admin")
        window.configure(background="#ffff00")

        global Canvas1
        Canvas1 = tk.Canvas(window, background="#ffffff", insertbackground="black", relief="ridge",
                    selectbackground="blue", selectforeground="white")
        # increased white box size for better spacing
        Canvas1.place(relx=0.06, rely=0.08, relheight=0.82, relwidth=0.88)

        self.Label1 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3",
                               font="-family {Segoe UI} -size 14 -weight bold", foreground="#00254a",
                               text="Admin Login")
        self.Label1.place(relx=0.135, rely=0.142, height=41, width=154)

        global Label2
        Label2 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        Label2.place(relx=0.067, rely=0.283, height=181, width=233)
        global _img0
        _img0 = tk.PhotoImage(file=asset_path("adminLogin1.png"))
        Label2.configure(image=_img0)

        self.Entry1 = tk.Entry(Canvas1, background="#e2e2e2", borderwidth="2", disabledforeground="#a3a3a3",
                               font="TkFixedFont", foreground="#000000", highlightbackground="#b6b6b6",
                               highlightcolor="#004080", insertbackground="black")
        self.Entry1.place(relx=0.607, rely=0.453, height=20, relwidth=0.26)


        self.Entry1_1 = tk.Entry(Canvas1, show='*', background="#e2e2e2", borderwidth="2",
                                 disabledforeground="#a3a3a3", font="TkFixedFont", foreground="#000000",
                                 highlightbackground="#d9d9d9", highlightcolor="#004080", insertbackground="black",
                                 selectbackground="blue", selectforeground="white")
        self.Entry1_1.place(relx=0.607, rely=0.623, height=20, relwidth=0.26)

        self.Label3 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        self.Label3.place(relx=0.556, rely=0.453, height=21, width=34)
        global _img1
        _img1 = tk.PhotoImage(file=asset_path("user1.png"))
        self.Label3.configure(image=_img1)

        self.Label4 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        self.Label4.place(relx=0.556, rely=0.623, height=21, width=34)
        global _img2
        _img2 = tk.PhotoImage(file=asset_path("lock1.png"))
        self.Label4.configure(image=_img2)

        self.Label5 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        self.Label5.place(relx=0.670, rely=0.142, height=71, width=74)
        global _img3
        _img3 = tk.PhotoImage(file=asset_path("bank1.png"))
        self.Label5.configure(image=_img3)

        self.Button = tk.Button(Canvas1, text="Login", borderwidth="0", width=10, background="#ffff00",
                                foreground="#00254a",
                                font="-family {Segoe UI} -size 10 -weight bold",
                                command=lambda: self.login(self.Entry1.get(), self.Entry1_1.get()))
        self.Button.place(relx=0.765, rely=0.755)

        self.Button_back = tk.Button(Canvas1, text="Back", borderwidth="0", width=10, background="#ffff00",
                                     foreground="#00254a",
                                     font="-family {Segoe UI} -size 10 -weight bold",
                                     command=self.back)
        self.Button_back.place(relx=0.545, rely=0.755)

        global admin_img
        admin_img = tk.PhotoImage(file=asset_path("adminLogin1.png"))

        if not service.admin_exists():
            # small spacer to create ~10px gap before the setup message
            self.SetupSpacer = tk.Label(Canvas1, background="#ffffff", text="")
            self.SetupSpacer.place(relx=0.135, rely=0.86, height=10, width=360)

            self.SetupLabel = tk.Label(
                Canvas1,
                background="#ffffff",
                foreground="#00254a",
                font="-family {Segoe UI} -size 9 -weight bold",
                text="No admin accounts yet. Create the first admin to continue.",
            )
            self.SetupLabel.place(relx=0.135, rely=0.85, height=20, width=360)

            self.SetupButton = tk.Button(
                Canvas1,
                text="Create First Admin",
                borderwidth="0",
                width=18,
                background="#023047",
                foreground="#ffffff",
                font="-family {Segoe UI} -size 9 -weight bold",
                command=self.first_admin_setup,
            )
            # keep the button within the white canvas so the yellow window background doesn't show
            self.SetupButton.place(relx=0.545, rely=0.92, height=24, width=130)

    def back(self):
        self.master.withdraw()
        welcomeScreen(Toplevel(self.master))

    def first_admin_setup(self):
        self.master.withdraw()
        createAdmin(
            Toplevel(self.master),
            return_to=self.master,
            on_return=self._clear_first_admin_notice,
        )

    def _clear_first_admin_notice(self):
        # remove the spacer/label/button that were only needed before the first admin existed
        for attr in ("SetupSpacer", "SetupLabel", "SetupButton"):
            widget = getattr(self, attr, None)
            if widget:
                widget.destroy()
                setattr(self, attr, None)

    @staticmethod
    def setImg():
        Label2 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        Label2.place(relx=0.067, rely=0.283, height=181, width=233)
        Label2.configure(image=admin_img)

    def login(self, admin_id, admin_password):
        global admin_idNO
        admin_idNO = admin_id
        if check_credentials(admin_id, admin_password, 1, True):
            self.master.withdraw()
            adminMenu(Toplevel(self.master))
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Invalid Credentials!")
            self.setImg()


class CustomerLogin:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 743, 494)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Customer")
        window.configure(background="#00254a")

        global Canvas1
        Canvas1 = tk.Canvas(window, background="#ffffff", insertbackground="black", relief="ridge",
                    selectbackground="blue", selectforeground="white")
        # increase white box size to match admin login layout
        Canvas1.place(relx=0.06, rely=0.08, relheight=0.82, relwidth=0.88)

        Label1 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3",
                          font="-family {Segoe UI} -size 14 -weight bold", foreground="#00254a",
                          text="Customer Login")
        Label1.place(relx=0.135, rely=0.142, height=41, width=154)

        global Label2
        Label2 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        Label2.place(relx=0.067, rely=0.283, height=181, width=233)
        global _img0
        _img0 = tk.PhotoImage(file=asset_path("customer.png"))
        Label2.configure(image=_img0)

        self.Entry1 = tk.Entry(Canvas1, background="#e2e2e2", borderwidth="2", disabledforeground="#a3a3a3",
                               font="TkFixedFont", foreground="#000000", highlightbackground="#b6b6b6",
                               highlightcolor="#004080", insertbackground="black")
        self.Entry1.place(relx=0.607, rely=0.453, height=20, relwidth=0.26)

        self.Entry1HintLabel = tk.Label(
            Canvas1,
            background="#ffffff",
            foreground="#00254a",
            font="-family {Segoe UI} -size 9",
            text="Full name or mobile number",
        )
        self.Entry1HintLabel.place(relx=0.607, rely=0.37, height=16, relwidth=0.26)

        self.Entry1_1 = tk.Entry(Canvas1, show='*', background="#e2e2e2", borderwidth="2",
                                 disabledforeground="#a3a3a3", font="TkFixedFont", foreground="#000000",
                                 highlightbackground="#d9d9d9", highlightcolor="#004080", insertbackground="black",
                                 selectbackground="blue", selectforeground="white")
        self.Entry1_1.place(relx=0.607, rely=0.623, height=20, relwidth=0.26)

        self.Label3 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        self.Label3.place(relx=0.556, rely=0.453, height=21, width=34)

        global _img1
        _img1 = tk.PhotoImage(file=asset_path("user1.png"))
        self.Label3.configure(image=_img1)

        self.Label4 = tk.Label(Canvas1)
        self.Label4.place(relx=0.556, rely=0.623, height=21, width=34)
        global _img2
        _img2 = tk.PhotoImage(file=asset_path("lock1.png"))
        self.Label4.configure(image=_img2, background="#ffffff")

        self.Label5 = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        self.Label5.place(relx=0.670, rely=0.142, height=71, width=74)
        global _img3
        _img3 = tk.PhotoImage(file=asset_path("bank1.png"))
        self.Label5.configure(image=_img3)

        self.Button = tk.Button(Canvas1, text="Login", borderwidth="0", width=10, background="#00254a",
                                foreground="#ffffff",
                                font="-family {Segoe UI} -size 10 -weight bold",
                                command=lambda: self.login(self.Entry1.get(), self.Entry1_1.get()))
        self.Button.place(relx=0.765, rely=0.755)

        self.Button_back = tk.Button(Canvas1, text="Back", borderwidth="0", width=10, background="#00254a",
                                     foreground="#ffffff",
                                     font="-family {Segoe UI} -size 10 -weight bold",
                                     command=self.back)
        self.Button_back.place(relx=0.545, rely=0.755)

        global customer_img
        customer_img = tk.PhotoImage(file=asset_path("customer.png"))

    def back(self):
        self.master.withdraw()
        welcomeScreen(Toplevel(self.master))

    @staticmethod
    def setImg():
        settingIMG = tk.Label(Canvas1, background="#ffffff", disabledforeground="#a3a3a3", foreground="#000000")
        settingIMG.place(relx=0.067, rely=0.283, height=181, width=233)
        settingIMG.configure(image=customer_img)

    def login(self, identifier, customer_PIN):
        account_number = authenticate_customer_identifier(identifier, customer_PIN)
        if account_number:
            global customer_accNO
            customer_accNO = account_number
            self.master.withdraw()
            customerMenu(Toplevel(self.master))
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Invalid Credentials!")
            self.setImg()


class adminMenu:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 743, 494)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Admin Section")
        window.configure(background="#ffff00")

        self.Labelframe1 = tk.LabelFrame(window, relief='groove', font="-family {Segoe UI} -size 13 -weight bold",
                                         foreground="#001c37", text="Select your option", background="#fffffe")
        self.Labelframe1.place(relx=0.081, rely=0.081, relheight=0.415, relwidth=0.848)

        self.Button1 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#00254a", borderwidth="0", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text="Close bank account", command=self.closeAccount)
        self.Button1.place(relx=0.667, rely=0.195, height=34, width=181, bordermode='ignore')

        self.Button2 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#00254a", borderwidth="0", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text="Create bank account", command=self.createCustaccount)
        self.Button2.place(relx=0.04, rely=0.195, height=34, width=181, bordermode='ignore')

        self.Button3 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#00254a", borderwidth="0", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text="Exit",
                                 command=self.exit)
        self.Button3.place(relx=0.667, rely=0.683, height=34, width=181, bordermode='ignore')

        self.Button4 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#00254a", borderwidth="0", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text="Create admin account", command=self.createAdmin)
        self.Button4.place(relx=0.04, rely=0.439, height=34, width=181, bordermode='ignore')

        self.Button5 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#00254a", borderwidth="0", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text="Close admin account", command=self.deleteAdmin)
        self.Button5.place(relx=0.667, rely=0.439, height=34, width=181, bordermode='ignore')

        self.Button6 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#00254a", foreground="#fffffe", borderwidth="0",
                                 disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 11",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text="Check account summary", command=self.showAccountSummary)
        self.Button6.place(relx=0.04, rely=0.683, height=34, width=181, bordermode='ignore')

        global Frame1
        Frame1 = tk.Frame(window, relief='groove', borderwidth="2", background="#fffffe")
        Frame1.place(relx=0.081, rely=0.547, relheight=0.415, relwidth=0.848)

    def closeAccount(self):
        CloseAccountByAdmin(Toplevel(self.master))

    def createCustaccount(self):
        createCustomerAccount(Toplevel(self.master))

    def createAdmin(self):
        createAdmin(Toplevel(self.master))

    def deleteAdmin(self):
        deleteAdmin(Toplevel(self.master))

    def showAccountSummary(self):
        checkAccountSummary(Toplevel(self.master))

    def printAccountSummary(identity):
        # clearing the frame
        for widget in Frame1.winfo_children():
            widget.destroy()
        # getting output_message and displaying it in the frame
        output = display_account_summary(identity, 1)
        output_message = Label(Frame1, text=output, background="#fffffe")
        output_message.pack(pady=20)

    def printMessage_outside(output):
        # clearing the frame
        for widget in Frame1.winfo_children():
            widget.destroy()
        # getting output_message and displaying it in the frame
        output_message = Label(Frame1, text=output, background="#fffffe")
        output_message.pack(pady=20)

    def exit(self):
        self.master.withdraw()
        adminLogin(Toplevel(self.master))


class CloseAccountByAdmin:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 117)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Close customer account")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3",
                               text='''Enter account number:''')
        self.Label1.place(relx=0.232, rely=0.220, height=20, width=120)

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry1.place(relx=0.536, rely=0.220, height=20, relwidth=0.232)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", borderwidth="0",
                                 background="#004080", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text="Back",
                                 command=self.back)
        self.Button1.place(relx=0.230, rely=0.598, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text="Proceed",
                                 command=lambda: self.submit(self.Entry1.get()))
        self.Button2.place(relx=0.598, rely=0.598, height=24, width=67)

    def back(self):
        self.master.withdraw()

    def submit(self, identity):
        if not is_valid(identity):
            delete_customer_account(identity, 1)
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Account doesn't exist!")
            return
        self.master.withdraw()


class createCustomerAccount:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 403)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Create account")
        window.configure(background="#f2f3f4")
        window.configure(highlightbackground="#d9d9d9")
        window.configure(highlightcolor="black")

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                               insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry1.place(relx=0.511, rely=0.027, height=20, relwidth=0.302)

        self.Label1 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", text='''Account number:''')
        self.Label1.place(relx=0.219, rely=0.025, height=26, width=120)

        self.Label2 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", text='''Full name:''')
        self.Label2.place(relx=0.316, rely=0.099, height=27, width=75)

        self.Entry2 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3",
                               font="TkFixedFont", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", insertbackground="black", selectbackground="blue",
                               selectforeground="white")
        self.Entry2.place(relx=0.511, rely=0.099, height=20, relwidth=0.302)

        self.Label3 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", text='''Account type:''')
        self.Label3.place(relx=0.287, rely=0.169, height=26, width=83)

        global acc_type
        acc_type = StringVar()

        self.Radiobutton1 = tk.Radiobutton(window, activebackground="#ececec", activeforeground="#000000",
                                           background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                                           highlightbackground="#d9d9d9", highlightcolor="black", justify='left',
                                           text='''Savings''', variable=acc_type, value="Savings")
        self.Radiobutton1.place(relx=0.511, rely=0.174, relheight=0.057, relwidth=0.151)

        self.Radiobutton1_1 = tk.Radiobutton(window, activebackground="#ececec", activeforeground="#000000",
                                             background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                                             highlightbackground="#d9d9d9", highlightcolor="black", justify='left',
                                             text='''Current''', variable=acc_type, value="Current")
        self.Radiobutton1_1.place(relx=0.706, rely=0.174, relheight=0.057, relwidth=0.175)

        self.Radiobutton1.deselect()
        self.Radiobutton1_1.deselect()

        self.Label5 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000",
                               highlightcolor="black", text='''Mobile number:''')
        self.Label5.place(relx=0.268, rely=0.323, height=22, width=85)

        self.Label4 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000",
                               highlightcolor="black", text='''Birth date (DD/MM/YYYY):''')
        self.Label4.place(relx=0.090, rely=0.238, height=27, width=175)

        self.Entry5 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                               insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry5.place(relx=0.511, rely=0.323, height=20, relwidth=0.302)

        self.Entry4 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                               insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry4.place(relx=0.511, rely=0.248, height=20, relwidth=0.302)

        self.Label6 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000",
                               highlightcolor="black", text='''Gender:''')
        self.Label6.place(relx=0.345, rely=0.402, height=15, width=65)

        global gender
        gender = StringVar()

        self.Radiobutton3 = tk.Radiobutton(window, activebackground="#ececec", activeforeground="#000000",
                                           background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                                           highlightcolor="black", justify='left',
                                           text='''Male''', variable=gender, value="Male")
        self.Radiobutton3.place(relx=0.481, rely=0.397, relheight=0.055, relwidth=0.175)

        self.Radiobutton4 = tk.Radiobutton(window, activebackground="#ececec", activeforeground="#000000",
                                           background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                                           highlightbackground="#d9d9d9", highlightcolor="black", justify='left',
                                           text='''Female''', variable=gender, value="Female")
        self.Radiobutton4.place(relx=0.706, rely=0.397, relheight=0.055, relwidth=0.175)

        self.Radiobutton3.deselect()
        self.Radiobutton4.deselect()

        self.Label7 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", text='''Nationality:''')
        self.Label7.place(relx=0.309, rely=0.471, height=21, width=75)

        self.Entry7 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3",
                               font="TkFixedFont", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", insertbackground="black", selectbackground="blue",
                               selectforeground="white")
        self.Entry7.place(relx=0.511, rely=0.471, height=20, relwidth=0.302)

        self.Entry9 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                               insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry9.place(relx=0.511, rely=0.623, height=20, relwidth=0.302)

        self.Entry10 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3",
                                font="TkFixedFont",
                                foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                                insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry10.place(relx=0.511, rely=0.7, height=20, relwidth=0.302)

        self.Entry11 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                                foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                                insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry11.place(relx=0.511, rely=0.777, height=20, relwidth=0.302)

        self.Label9 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", text='''PIN:''')
        self.Label9.place(relx=0.399, rely=0.62, height=21, width=35)

        self.Label10 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                                disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                                highlightcolor="black", text='''Re-enter PIN:''')
        self.Label10.place(relx=0.292, rely=0.695, height=21, width=75)

        self.Label11 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                                disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                                highlightcolor="black", text='''Initial balance:''')
        self.Label11.place(relx=0.292, rely=0.779, height=21, width=75)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Back''',
                                 command=self.back)
        self.Button1.place(relx=0.243, rely=0.893, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.create_acc(self.Entry1.get(), self.Entry2.get(), acc_type.get(),
                                                                 self.Entry4.get(), self.Entry5.get(), gender.get(),
                                                                 self.Entry7.get(), self.Entry8.get(),
                                                                 self.Entry9.get(), self.Entry10.get(),
                                                                 self.Entry11.get()))
        self.Button2.place(relx=0.633, rely=0.893, height=24, width=67)

        self.Label8 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''KYC document name:''')
        self.Label8.place(relx=0.18, rely=0.546, height=24, width=122)

        self.Entry8 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry8.place(relx=0.511, rely=0.546, height=20, relwidth=0.302)

    def back(self):
        self.master.withdraw()

    def create_acc(self, customer_account_number, name, account_type, date_of_birth, mobile_number, gender, nationality,
                   KYC_document,
                   PIN, confirm_PIN, initial_balance):
        if confirm_PIN != PIN:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="PIN mismatch!")
            return

        try:
            service.create_customer(
                customer_account_number,
                name,
                account_type,
                date_of_birth,
                mobile_number,
                gender,
                nationality,
                KYC_document,
                PIN,
                initial_balance,
            )
        except ConflictError:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Account number already exists!")
            return
        except (ValidationError, BusinessRuleError) as exc:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown=str(exc))
            return

        output_message = "Customer account created successfully!"
        print(output_message)
        adminMenu.printMessage_outside(output_message)
        self.master.withdraw()


class createAdmin:
    def __init__(self, window=None, return_to=None, on_return=None):
        self.master = window
        self._return_to = return_to
        self._on_return = on_return
        center_window(window, 411, 150)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Create admin account")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter admin ID:''')
        self.Label1.place(relx=0.219, rely=0.067, height=27, width=104)

        self.Label2 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter password:''')
        self.Label2.place(relx=0.219, rely=0.267, height=27, width=104)

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry1.place(relx=0.487, rely=0.087, height=20, relwidth=0.326)

        self.Entry2 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry2.place(relx=0.487, rely=0.287, height=20, relwidth=0.326)

        self.Label3 = tk.Label(window, activebackground="#f9f9f9", activeforeground="black", background="#f2f3f4",
                               disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
                               highlightcolor="black", text='''Confirm password:''')
        self.Label3.place(relx=0.195, rely=0.467, height=27, width=104)

        self.Entry3 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry3.place(relx=0.487, rely=0.487, height=20, relwidth=0.326)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text="Proceed",
                                 command=lambda: self.create_admin_account(self.Entry1.get(), self.Entry2.get(),
                                                                           self.Entry3.get()))
        self.Button1.place(relx=0.598, rely=0.733, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text="Back",
                                 command=self.back)
        self.Button2.place(relx=0.230, rely=0.733, height=24, width=67)

    def back(self):
        self.master.withdraw()

    def create_admin_account(self, identity, password, confirm_password):
        if password != confirm_password:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Password Mismatch!")
            return

        try:
            service.create_admin(identity, password)
        except ConflictError:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="ID is unavailable!")
            return
        except ValidationError as exc:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown=str(exc))
            return

        output_message = "Admin account created successfully!"
        _safe_admin_message(output_message)
        print(output_message)
        if self._on_return:
            try:
                self._on_return()
            except Exception:
                pass
        if self._return_to:
            self._return_to.deiconify()
            try:
                self._return_to.lift()
            except Exception:
                pass
        self.master.withdraw()


class deleteAdmin:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 117)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Delete admin account")
        window.configure(background="#f2f3f4")

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry1.place(relx=0.487, rely=0.092, height=20, relwidth=0.277)

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter admin ID:''')
        self.Label1.place(relx=0.219, rely=0.092, height=21, width=104)

        self.Label2 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter password:''')
        self.Label2.place(relx=0.209, rely=0.33, height=21, width=109)

        self.Entry1_1 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3",
                                 font="TkFixedFont",
                                 foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
                                 insertbackground="black", selectbackground="blue", selectforeground="white")
        self.Entry1_1.place(relx=0.487, rely=0.33, height=20, relwidth=0.277)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Back''',
                                 command=self.back)
        self.Button1.place(relx=0.243, rely=0.642, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 borderwidth="0", disabledforeground="#a3a3a3", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.delete_admin(self.Entry1.get(), self.Entry1_1.get()))
        self.Button2.place(relx=0.608, rely=0.642, height=24, width=67)

    def delete_admin(self, admin_id, password):
        if check_credentials(admin_id, password, 1, True):
            delete_admin_account(admin_id)
            self.master.withdraw()
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Invalid Credentials!")

    def back(self):
        self.master.withdraw()


class customerMenu:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 743, 494)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Customer Section")
        window.configure(background="#00254a")

        self.Labelframe1 = tk.LabelFrame(window, relief='groove', font="-family {Segoe UI} -size 13 -weight bold",
                                         foreground="#000000", text='''Select your option''', background="#fffffe")
        self.Labelframe1.place(relx=0.081, rely=0.081, relheight=0.415, relwidth=0.848)

        self.Button1 = tk.Button(self.Labelframe1, command=self.selectWithdraw, activebackground="#ececec",
                                 activeforeground="#000000", background="#39a9fc", borderwidth="0",
                                 disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Withdraw''')
        self.Button1.place(relx=0.667, rely=0.195, height=34, width=181, bordermode='ignore')

        self.Button2 = tk.Button(self.Labelframe1, command=self.selectDeposit, activebackground="#ececec",
                                 activeforeground="#000000", background="#39a9fc", borderwidth="0",
                                 disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Deposit''')
        self.Button2.place(relx=0.04, rely=0.195, height=34, width=181, bordermode='ignore')

        self.Button3 = tk.Button(self.Labelframe1, command=self.exit, activebackground="#ececec",
                                 activeforeground="#000000",
                                 background="#39a9fc",
                                 borderwidth="0", disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 11",
                                 foreground="#fffffe", highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text='''Exit''')
        self.Button3.place(relx=0.667, rely=0.683, height=34, width=181, bordermode='ignore')

        self.Button4 = tk.Button(self.Labelframe1, command=self.selectChangePIN, activebackground="#ececec",
                                 activeforeground="#000000", background="#39a9fc", borderwidth="0",
                                 disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Change PIN''')
        self.Button4.place(relx=0.04, rely=0.439, height=34, width=181, bordermode='ignore')

        self.Button5 = tk.Button(self.Labelframe1, command=self.selectCloseAccount, activebackground="#ececec",
                                 activeforeground="#000000", background="#39a9fc", borderwidth="0",
                                 disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text='''Close account''')
        self.Button5.place(relx=0.667, rely=0.439, height=34, width=181, bordermode='ignore')

        self.Button6 = tk.Button(self.Labelframe1, activebackground="#ececec", activeforeground="#000000",
                                 background="#39a9fc", borderwidth="0", disabledforeground="#a3a3a3",
                                 font="-family {Segoe UI} -size 11", foreground="#fffffe",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0",
                                 text='''Check your balance''', command=self.checkBalance)
        self.Button6.place(relx=0.04, rely=0.683, height=34, width=181, bordermode='ignore')

        global Frame1_1_2
        Frame1_1_2 = tk.Frame(window, relief='groove', borderwidth="2", background="#fffffe")
        Frame1_1_2.place(relx=0.081, rely=0.547, relheight=0.415, relwidth=0.848)

    def selectDeposit(self):
        depositMoney(Toplevel(self.master))

    def selectWithdraw(self):
        withdrawMoney(Toplevel(self.master))

    def selectChangePIN(self):
        changePIN(Toplevel(self.master))

    def selectCloseAccount(self):
        self.master.withdraw()
        closeAccount(Toplevel(self.master))

    def exit(self):
        self.master.withdraw()
        CustomerLogin(Toplevel(self.master))

    def checkBalance(self):
        output = display_account_summary(customer_accNO, 2)
        self.printMessage(output)
        print("check balance function called.")

    def printMessage(self, output):
        # clearing the frame
        for widget in Frame1_1_2.winfo_children():
            widget.destroy()
        # getting output_message and displaying it in the frame
        output_message = Label(Frame1_1_2, text=output, background="#fffffe")
        output_message.pack(pady=20)

    def printMessage_outside(output):
        # clearing the frame
        for widget in Frame1_1_2.winfo_children():
            widget.destroy()
        # getting output_message and displaying it in the frame
        output_message = Label(Frame1_1_2, text=output, background="#fffffe")
        output_message.pack(pady=20)


class depositMoney:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 117)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Deposit money")
        p1 = PhotoImage(file=asset_path("deposit_icon.png"))
        window.iconphoto(True, p1)
        window.configure(borderwidth="2")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3",
                               font="-family {Segoe UI} -size 9", foreground="#000000", borderwidth="0",
                               text='''Enter amount to deposit :''')
        self.Label1.place(relx=0.146, rely=0.171, height=21, width=164)

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black", selectforeground="#ffffffffffff")
        self.Entry1.place(relx=0.535, rely=0.171, height=20, relwidth=0.253)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", borderwidth="0", foreground="#ffffff",
                                 highlightbackground="#000000",
                                 highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.submit(self.Entry1.get()))
        self.Button1.place(relx=0.56, rely=0.598, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", font="-family {Segoe UI} -size 9", foreground="#ffffff",
                                 highlightbackground="#d9d9d9", borderwidth="0", highlightcolor="black", pady="0",
                                 text='''Back''',
                                 command=self.back)
        self.Button2.place(relx=0.268, rely=0.598, height=24, width=67)

    def submit(self, amount):
        if amount.isnumeric():
            if MAX_TRANSACTION >= float(amount) > 0:
                output = transaction(customer_accNO, float(amount), 1)
            else:
                Error(Toplevel(self.master))
                if float(amount) > MAX_TRANSACTION:
                    Error.setMessage(self, message_shown="Limit exceeded!")
                else:
                    Error.setMessage(self, message_shown="Positive value expected!")
                return
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Invalid amount!")
            return
        if output == -1:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Transaction failed!")
            return
        else:
            output = "Amount of rupees " + str(amount) + " deposited successfully.\nUpdated balance : " + str(output)
            customerMenu.printMessage_outside(output)
            self.master.withdraw()

    def back(self):
        self.master.withdraw()


class withdrawMoney:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 117)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Withdraw money")
        p1 = PhotoImage(file=asset_path("withdraw_icon.png"))
        window.iconphoto(True, p1)
        window.configure(borderwidth="2")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3",
                               font="-family {Segoe UI} -size 9", foreground="#000000",
                               text='''Enter amount to withdraw :''')
        self.Label1.place(relx=0.146, rely=0.171, height=21, width=164)

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black", selectforeground="#ffffffffffff")
        self.Entry1.place(relx=0.535, rely=0.171, height=20, relwidth=0.253)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", borderwidth="0", foreground="#ffffff",
                                 highlightbackground="#000000",
                                 highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.submit(self.Entry1.get()))
        self.Button1.place(relx=0.56, rely=0.598, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", borderwidth="0", font="-family {Segoe UI} -size 9",
                                 foreground="#ffffff",
                                 highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Back''',
                                 command=self.back)
        self.Button2.place(relx=0.268, rely=0.598, height=24, width=67)

    def submit(self, amount):
        if amount.isnumeric():
            if MAX_TRANSACTION >= float(amount) > 0:
                output = transaction(customer_accNO, float(amount), 2)
            else:
                Error(Toplevel(self.master))
                if float(amount) > MAX_TRANSACTION:
                    Error.setMessage(self, message_shown="Limit exceeded!")
                else:
                    Error.setMessage(self, message_shown="Positive value expected!")
                return
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Invalid amount!")
            return
        if output == -1:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Transaction failed!")
            return
        else:
            output = "Amount of rupees " + str(amount) + " withdrawn successfully.\nUpdated balance : " + str(output)
            customerMenu.printMessage_outside(output)
            self.master.withdraw()

    def back(self):
        self.master.withdraw()


class changePIN:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 111)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Change PIN")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter new PIN:''')
        self.Label1.place(relx=0.243, rely=0.144, height=21, width=93)

        self.Label2 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Confirm PIN:''')
        self.Label2.place(relx=0.268, rely=0.414, height=21, width=82)

        self.Entry1 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry1.place(relx=0.528, rely=0.144, height=20, relwidth=0.229)

        self.Entry2 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry2.place(relx=0.528, rely=0.414, height=20, relwidth=0.229)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", foreground="#ffffff", borderwidth="0",
                                 highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.submit(self.Entry1.get(), self.Entry2.get()))
        self.Button1.place(relx=0.614, rely=0.721, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", foreground="#ffffff", borderwidth="0",
                                 highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text="Back", command=self.back)
        self.Button2.place(relx=0.214, rely=0.721, height=24, width=67)

    def submit(self, new_PIN, confirm_new_PIN):
        if new_PIN == confirm_new_PIN and str(new_PIN).__len__() == 4 and new_PIN.isnumeric():
            change_PIN(customer_accNO, new_PIN)
            self.master.withdraw()
        else:
            Error(Toplevel(self.master))
            if new_PIN != confirm_new_PIN:
                Error.setMessage(self, message_shown="PIN mismatch!")
            elif str(new_PIN).__len__() != 4:
                Error.setMessage(self, message_shown="PIN length must be 4!")
            else:
                Error.setMessage(self, message_shown="Invalid PIN!")
            return

    def back(self):
        self.master.withdraw()


class closeAccount:
    def __init__(self, window=None):
        self.master = window
        center_window(window, 411, 117)
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Close Account")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter your PIN:''')
        self.Label1.place(relx=0.268, rely=0.256, height=21, width=94)

        self.Entry1 = tk.Entry(window, show="*", background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry1.place(relx=0.511, rely=0.256, height=20, relwidth=0.229)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", foreground="#ffffff", borderwidth="0",
                                 highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.submit(self.Entry1.get()))
        self.Button1.place(relx=0.614, rely=0.712, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", foreground="#ffffff", borderwidth="0",
                                 highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text="Back", command=self.back)
        self.Button2.place(relx=0.214, rely=0.712, height=24, width=67)

    def submit(self, PIN):
        print("Submit pressed.")
        print(customer_accNO, PIN)
        if check_credentials(customer_accNO, PIN, 2, False):
            print("Correct accepted.")
            delete_customer_account(customer_accNO, 2)
            self.master.withdraw()
            CustomerLogin(Toplevel(self.master))
        else:
            print("Incorrect accepted.")
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Invalid PIN!")

    def back(self):
        self.master.withdraw()
        customerMenu(Toplevel(self.master))


class checkAccountSummary:
    def __init__(self, window=None):
        self.master = window
        window.geometry("411x117+498+261")
        window.minsize(120, 1)
        window.maxsize(1370, 749)
        window.resizable(0, 0)
        window.title("Check Account Summary")
        window.configure(background="#f2f3f4")

        self.Label1 = tk.Label(window, background="#f2f3f4", disabledforeground="#a3a3a3", foreground="#000000",
                               text='''Enter ID :''')
        self.Label1.place(relx=0.268, rely=0.256, height=21, width=94)

        self.Entry1 = tk.Entry(window, background="#cae4ff", disabledforeground="#a3a3a3", font="TkFixedFont",
                               foreground="#000000", insertbackground="black")
        self.Entry1.place(relx=0.511, rely=0.256, height=20, relwidth=0.229)

        self.Button1 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", foreground="#ffffff", borderwidth="0",
                                 highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text='''Proceed''',
                                 command=lambda: self.submit(self.Entry1.get()))
        self.Button1.place(relx=0.614, rely=0.712, height=24, width=67)

        self.Button2 = tk.Button(window, activebackground="#ececec", activeforeground="#000000", background="#004080",
                                 disabledforeground="#a3a3a3", foreground="#ffffff", borderwidth="0",
                                 highlightbackground="#d9d9d9",
                                 highlightcolor="black", pady="0", text="Back", command=self.back)
        self.Button2.place(relx=0.214, rely=0.712, height=24, width=67)

    def back(self):
        self.master.withdraw()

    def submit(self, identity):
        if not is_valid(identity):
            adminMenu.printAccountSummary(identity)
        else:
            Error(Toplevel(self.master))
            Error.setMessage(self, message_shown="Id doesn't exist!")
            return
        self.master.withdraw()


def run_app() -> None:
    root = tk.Tk()
    welcomeScreen(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()

# Tkinter GUI code ends.



