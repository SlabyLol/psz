import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from psz import open_archive, create_archive


class PSZApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PSZ Archive Tool")
        self.root.geometry("520x280")
        self.root.resizable(False, False)

        title = tk.Label(
            root,
            text="PSZ Archive Tool",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            root,
            text="Create or extract .psz archives",
            font=("Arial", 10)
        )
        subtitle.pack(pady=(0, 20))

        # Create archive
        create_frame = tk.LabelFrame(
            root,
            text="Create PSZ archive",
            padx=15,
            pady=15
        )
        create_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(
            create_frame,
            text="Select folder and create .psz",
            command=self.create_psz,
            width=35
        ).pack()

        # Extract archive
        extract_frame = tk.LabelFrame(
            root,
            text="Extract PSZ archive",
            padx=15,
            pady=15
        )
        extract_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(
            extract_frame,
            text="Select .psz and extract",
            command=self.extract_psz,
            width=35
        ).pack()

        self.status = tk.Label(
            root,
            text="Ready",
            anchor="w"
        )
        self.status.pack(fill="x", padx=25, pady=15)

    def create_psz(self):
        folder = filedialog.askdirectory(
            title="Select project folder"
        )

        if not folder:
            return

        folder = Path(folder)

        output = filedialog.asksaveasfilename(
            title="Save PSZ archive",
            defaultextension=".psz",
            filetypes=[
                ("PSZ archive", "*.psz"),
                ("All files", "*.*")
            ],
            initialfile=f"{folder.name}.psz"
        )

        if not output:
            return

        output = Path(output)

        try:
            self.status.config(text="Creating archive...")
            self.root.update_idletasks()

            create_archive(folder, output)

            self.status.config(
                text=f"Created: {output.name}"
            )

            messagebox.showinfo(
                "Success",
                f"Archive created successfully:\n\n{output}"
            )

        except Exception as e:
            self.status.config(text="Error")
            messagebox.showerror(
                "Error",
                f"Could not create archive:\n\n{e}"
            )

    def extract_psz(self):
        archive = filedialog.askopenfilename(
            title="Select PSZ archive",
            filetypes=[
                ("PSZ archive", "*.psz"),
                ("All files", "*.*")
            ]
        )

        if not archive:
            return

        archive = Path(archive)

        output_dir = filedialog.askdirectory(
            title="Select extraction directory"
        )

        if not output_dir:
            return

        output_dir = Path(output_dir)

        # .psz-data.lor wird neben dem Archiv erwartet/erzeugt.
        lor_file = archive.with_name(
            archive.name + "-data.lor"
        )

        try:
            self.status.config(text="Extracting archive...")
            self.root.update_idletasks()

            open_archive(
                archive,
                lor_file,
                output_dir
            )

            self.status.config(
                text=f"Extracted: {archive.name}"
            )

            messagebox.showinfo(
                "Success",
                f"Archive extracted successfully to:\n\n{output_dir}"
            )

        except Exception as e:
            self.status.config(text="Error")
            messagebox.showerror(
                "Error",
                f"Could not extract archive:\n\n{e}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = PSZApp(root)
    root.mainloop()
