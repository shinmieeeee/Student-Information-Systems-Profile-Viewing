#libraries that are used to implement the system
import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import tkinter.font as tkFont
from io import BytesIO

#define get connection allows the system to connect to the database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="informationsystem"
    )

try:
    get_connection().close()
except Exception as e:
    print("Error connecting to MySQL:", e)
    exit()

def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Student(
                SrCode VARCHAR(20) PRIMARY KEY,
                FullName VARCHAR(100),
                Department VARCHAR(100),
                Age VARCHAR(10)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS StudentProfile(
                SrCode VARCHAR(20) PRIMARY KEY,
                Info TEXT,
                Picture LONGBLOB,
                FOREIGN KEY (SrCode) REFERENCES Student(SrCode) ON DELETE CASCADE
            )
        """)
        conn.commit()

# ===== CRUD FUNCTIONS =====
def create_student(sr_code, full_name, department, age):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Student (SrCode, FullName, Department, Age) VALUES (%s,%s,%s,%s)",
                        (sr_code.strip(), full_name.strip(), department.strip(), age.strip()))
            conn.commit()
        return True, "Student added."
    except Exception as e:
        return False, str(e)

def read_students(filter_q=None):
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        if not filter_q:
            cur.execute("SELECT SrCode, FullName, Department, Age FROM Student ORDER BY SrCode")
        else:
            q = f"%{filter_q}%"
            cur.execute("""
                SELECT SrCode, FullName, Department, Age
                FROM Student
                WHERE SrCode LIKE %s OR FullName LIKE %s
                ORDER BY SrCode
            """, (q, q))
        rows = cur.fetchall()
    result = []
    counter = 1
    for r in rows:
        result.append({
            "id": counter,
            "sr_code": r["SrCode"],
            "full_name": r["FullName"],
            "department": r["Department"],
            "age": r["Age"]
        })
        counter += 1
    return result

def update_student(student_id, sr_code, full_name, department, age):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Student
                SET FullName=%s, Department=%s, Age=%s
                WHERE SrCode=%s
            """, (full_name.strip(), department.strip(), age.strip(), sr_code.strip()))
            conn.commit()
        return True, "Student updated."
    except Exception as e:
        return False, str(e)

def delete_student(student_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM StudentProfile WHERE SrCode=%s", (student_id,))
        cur.execute("DELETE FROM Student WHERE SrCode=%s", (student_id,))
        conn.commit()

# ===== PROFILE FUNCTIONS =====
def save_profile(sr_code, info=None, picture_path=None):
    try:
        pic_data = None
        if picture_path:
            with open(picture_path, "rb") as f:
                pic_data = f.read()

        profile = get_profile(sr_code)
        info_to_save = info if info is not None else (profile["Info"] if profile else "")
        pic_to_save = pic_data if pic_data is not None else (profile["Picture"] if profile else None)

        with get_connection() as conn:
            cur = conn.cursor()
            if profile:
                cur.execute("""
                    UPDATE StudentProfile
                    SET Info=%s, Picture=%s
                    WHERE SrCode=%s
                """, (info_to_save, pic_to_save, sr_code))
            else:
                cur.execute("""
                    INSERT INTO StudentProfile (SrCode, Info, Picture)
                    VALUES (%s, %s, %s)
                """, (sr_code, info_to_save, pic_to_save))
            conn.commit()
        return True, "Profile saved."
    except Exception as e:
        return False, str(e)

def get_profile(sr_code):
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM StudentProfile
            WHERE SrCode=%s
        """, (sr_code,))
        return cur.fetchone()

# ===== GUI CLASS =====
class StudentApp:
    def __init__(self, root):
        self.root = root
        root.title("Information System")
        root.geometry("1000x700")
        self.selected_student_id = None
        self.entry_font = tkFont.Font(family="Times New Roman", size=11)
        self.build_ui()
        self.refresh_list()
        self.clear_profile_display()

    def build_ui(self):
        top_frame = tk.Frame(self.root, bg="#747777")
        top_frame.pack(fill=tk.X)
        try:
            img = Image.open("finalproject.jpg")
            img = img.resize((920,140))
            self.top_img = ImageTk.PhotoImage(img)
            tk.Label(top_frame, image=self.top_img, bg="#747777").pack()
        except:
            tk.Label(top_frame, text="INFORMATION SYSTEMS", bg="#747777", font=("Arial",24,"bold")).pack(pady=10)

        content = tk.Frame(self.root, bg="#747777")
        content.pack(fill=tk.BOTH, expand=True)
        content.grid_columnconfigure(0, weight=0)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = tk.Frame(content, bg="#747777")
        left.grid(row=0, column=0, sticky="ns", padx=(10,5), pady=0)
        lbl_opts = {"bg":"#747777","anchor":"e","font":self.entry_font}

        input_manager_font = ("Times New Roman", 12, "bold")
        style = ttk.Style()
        style.configure("InputManager.TButton", font=input_manager_font)
        ttk.Button(left, text="Input Manager", width=26,
                command=self.input_manager_action, style="InputManager.TButton").grid(row=0, column=0, columnspan=2, pady=(0, 8))

        # Form fields
        tk.Label(left, text="SR Code:", **lbl_opts).grid(row=1,column=0,pady=5,sticky="e")
        self.ent_code = ttk.Entry(left, width=19, font=self.entry_font); self.ent_code.grid(row=1,column=1,pady=5,sticky="w")
        tk.Label(left, text="Full Name:", **lbl_opts).grid(row=2,column=0,pady=5,sticky="e")
        self.ent_name = ttk.Entry(left, width=19, font=self.entry_font); self.ent_name.grid(row=2,column=1,pady=5,sticky="w")
        tk.Label(left, text="Department:", **lbl_opts).grid(row=3,column=0,pady=5,sticky="e")
        self.ent_dept = ttk.Entry(left, width=19, font=self.entry_font); self.ent_dept.grid(row=3,column=1,pady=5,sticky="w")
        tk.Label(left, text="Age:", **lbl_opts).grid(row=4,column=0,pady=5,sticky="e")
        self.ent_age = ttk.Entry(left, width=19, font=self.entry_font); self.ent_age.grid(row=4,column=1,pady=5,sticky="w")

        btn_w = 20
        btn_font = ("Times New Roman", 10)
        style.configure("leftpanel.TButton", font=btn_font)
        ttk.Button(left, text="Add", width=btn_w, command=self.add_student, style="leftpanel.TButton").grid(row=5,column=1,columnspan=2,pady=(0,8))
        ttk.Button(left, text="Update", width=btn_w, command=self.update_student, style="leftpanel.TButton").grid(row=6,column=1,columnspan=2,pady=5)
        ttk.Button(left, text="Delete", width=btn_w, command=self.delete_student, style="leftpanel.TButton").grid(row=7,column=1,columnspan=2,pady=5)
        ttk.Button(left, text="Clear Form", width=btn_w, command=self.clear_form, style="leftpanel.TButton").grid(row=8,column=1,columnspan=2,pady=5)
    
        # Right panel
        self.right_panel = tk.Frame(content, bg="white")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=0)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(1, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1)

        # List frame
        self.list_frame = tk.Frame(self.right_panel, bg="#747777")
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(5,5))
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        search_fr = tk.Frame(self.list_frame, bg="#747777")
        search_fr.grid(row=0, column=0, sticky="ew", pady=(0,8))
        search_fr.grid_columnconfigure(1, weight=1)
        self.ent_search = ttk.Entry(search_fr, textvariable=self.search_var, justify="right", font=self.entry_font)
        self.ent_search.grid(row=0, column=1, sticky="ew", padx=(0,5))
        ttk.Button(search_fr, text="Search", width=10, command=self.search).grid(row=0, column=2, padx=5)
        ttk.Button(search_fr, text="Clear", width=10, command=lambda: (self.search_var.set(""), self.refresh_list())).grid(row=0, column=3, padx=5)

        self.tree_font = tkFont.Font(family="Times New Roman", size=10)
        self.header_font = tkFont.Font(family="Times New Roman", size=11)
        style.configure("Treeview", font=self.tree_font, rowheight=24)
        style.configure("Treeview.Heading", font=self.header_font, weight="bold")

        # Treeview
        cols = ("id","sr_code","full_name","department","age")
        self.tree = ttk.Treeview(self.list_frame, columns=cols, show="headings")
        for c, w, txt in zip(cols, [40,80,150,200,50], ["ID","SR Code","Full Name","Department","Age"]):
            self.tree.heading(c, text=txt, anchor="center")
            self.tree.column(c, width=w, anchor="center")

        self.tree.grid(row=1, column=0, sticky="nsew", padx=(0,0))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

       # Profile frame
        self.profile_frame = tk.Frame(self.right_panel, bg="#747777")
        self.profile_frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(self.profile_frame, text="STUDENT PROFILE", bg="#747777", fg="black",
                font=("Times New Roman", 18, "bold")).pack(pady=5)
        self.pf_img_label = tk.Label(self.profile_frame, bg="#747777")
        self.pf_img_label.pack(pady=10)

# ===== STUDENT INFO PANEL  =====
        self.info_panel = tk.LabelFrame(self.profile_frame, text="Student Information ★", 
                                        font=("Times New Roman", 12, "bold"), fg="black", bg="#747777")
        self.info_panel.pack(fill="x", padx=5, pady=(0,5))  

        lbl_opts = {"bg": "white", "fg": "black", "anchor": "w", "font": ("Times New Roman", 10)}

        self.lbl_sr2 = tk.Label(self.info_panel, text="SR Code: ", **lbl_opts)
        self.lbl_sr2.pack(fill="x", padx=5, pady=1)

        self.lbl_name2 = tk.Label(self.info_panel, text="Full Name: ", **lbl_opts)
        self.lbl_name2.pack(fill="x", padx=5, pady=1)

        self.lbl_dept2 = tk.Label(self.info_panel, text="Department: ", **lbl_opts)
        self.lbl_dept2.pack(fill="x", padx=5, pady=1)

        self.lbl_age2 = tk.Label(self.info_panel, text="Age: ", **lbl_opts)
        self.lbl_age2.pack(fill="x", padx=5, pady=1)

        self.pf_info_text = tk.Text(self.profile_frame, height=3, width=45,
                                    font=("Times New Roman", 10),
                                    bg="white", fg="black")
        self.pf_info_text.pack(fill="x", padx=10, pady=2)

        # Save / Upload buttons
        ttk.Button(self.profile_frame, text="Save Info", command=self.save_profile_info).pack(pady=5)
        ttk.Button(self.profile_frame, text="Upload Picture", command=self.upload_picture).pack(pady=5)

        # Status bar
        self.status = ttk.Label(self.root, text="Ready", anchor="w", font=self.entry_font)
        self.status.pack(fill=tk.X)

    # ===== BUTTON FUNCTIONS =====
    def add_student(self):
        code = self.ent_code.get().strip()
        name = self.ent_name.get().strip()
        dept = self.ent_dept.get().strip()
        age = self.ent_age.get().strip()
        if not (code and name and dept and age):
            messagebox.showwarning("Input error", "Fill all fields.")
            return
        ok, msg = create_student(code, name, dept, age)
        if ok:
            save_profile(code)  
            self.refresh_list()
            self.clear_form()
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    def update_student(self):
        if not self.selected_student_id:
            messagebox.showwarning("Select record", "Select a student to update.")
            return
        code = self.ent_code.get().strip()
        name = self.ent_name.get().strip()
        dept = self.ent_dept.get().strip()
        age = self.ent_age.get().strip()
        if not (code and name and dept and age):
            messagebox.showwarning("Input error", "Fill all fields.")
            return
        ok, msg = update_student(self.selected_student_id, code, name, dept, age)
        if ok:
            self.refresh_list()
            self.clear_form()
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    def delete_student(self):
        if not self.selected_student_id:
            messagebox.showwarning("Select record", "Select a student to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected student?"):
            return
        delete_student(self.selected_student_id)
        self.refresh_list()
        self.clear_form()
        messagebox.showinfo("Deleted", "Student deleted.")

    def clear_form(self):
        self.selected_student_id = None
        for e in (self.ent_code, self.ent_name, self.ent_dept, self.ent_age):
            e.delete(0, tk.END)
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        self.clear_profile_display()

    # final and correct one only
    def clear_profile_display(self):
        self.pf_info_text.delete(1.0, tk.END)
        self.pf_info_text.insert(tk.END, "Select a student from the list to view/edit info.")
        self.pf_img_label.config(image="", text="No Picture")

    def search(self):
        q = self.search_var.get().strip()
        self.refresh_list(filter_q=q)

    def enable_profile_edit(self):
        self.pf_info_text.config(state="normal")
        messagebox.showinfo("Edit Mode", "You can now edit the student information.")

        self.pf_info_text.config(state="disabled")

    def input_manager_action(self):
        messagebox.showinfo("Input Manager", "Input Manager clicked!")

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: 
            return

        vals = self.tree.item(sel[0])["values"]
        self.selected_student_id = vals[1]

        # Update entries on the left
        self.ent_code.delete(0, tk.END); self.ent_code.insert(0, vals[1])
        self.ent_name.delete(0, tk.END); self.ent_name.insert(0, vals[2])
        self.ent_dept.delete(0, tk.END); self.ent_dept.insert(0, vals[3])
        self.ent_age.delete(0, tk.END); self.ent_age.insert(0, vals[4])

        # Update picture + info
        self.update_profile_display(self.selected_student_id)

        # Update info panel
        self.update_info_panel(self.selected_student_id)

    def upload_picture(self):
        if not self.selected_student_id:
            messagebox.showwarning("No student selected", "Select a student first.")
            return

        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Picture",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not file_path:
            return

        ok, msg = save_profile(self.selected_student_id, picture_path=file_path)
        if ok:
            messagebox.showinfo("Success", "Picture updated.")
            self.update_profile_display(self.selected_student_id)
        else:
            messagebox.showerror("Error", msg)

    # ===== PROFILE DISPLAY =====
    def update_profile_display(self, sr_code):
        profile = get_profile(sr_code)

        self.pf_info_text.delete(1.0, tk.END)
        info_text = profile['Info'] if profile and profile['Info'] else ""
        self.pf_info_text.insert(tk.END, info_text)

        if profile and profile["Picture"]:
            img = Image.open(BytesIO(profile["Picture"]))
            img.thumbnail((250,250))
            self.pf_tk_img = ImageTk.PhotoImage(img)
            self.pf_img_label.config(image=self.pf_tk_img, text="")
        else:
            self.pf_img_label.config(image="", text="No Picture")

    def save_profile_info(self):
        if not self.selected_student_id:
            messagebox.showwarning("No student selected", "Select a student first.")
            return

        new_info = self.pf_info_text.get(1.0, tk.END).strip()
        ok, msg = save_profile(self.selected_student_id, info=new_info)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    def update_info_panel(self, sr_code):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT SrCode, FullName, Department, Age FROM Student WHERE SrCode=%s", (sr_code,))
        s = cur.fetchone()
        conn.close()

        if s:
            self.lbl_sr2.config(text=f"SR Code: {s['SrCode']}")
            self.lbl_name2.config(text=f"Full Name: {s['FullName']}")
            self.lbl_dept2.config(text=f"Department: {s['Department']}")
            self.lbl_age2.config(text=f"Age: {s['Age']}")
        else:
            self.lbl_sr2.config(text="SR Code: ")
            self.lbl_name2.config(text="Full Name: ")
            self.lbl_dept2.config(text="Department: ")
            self.lbl_age2.config(text="Age: ")

# ===== UTILITIES =====
    def set_status(self, text):
        self.status.config(text=text)

    def refresh_list(self, filter_q=None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        students = read_students(filter_q)
        for s in students:
            self.tree.insert("", tk.END, values=(s["id"], s["sr_code"], s["full_name"], s["department"], s["age"]))
        self.set_status(f"{len(students)} record(s) loaded.")

# ===== MAIN =====
def main():
    init_db()
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()