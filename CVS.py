import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv

load_dotenv()

try:
    db = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'votingsystem')
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Error connecting to database: {err}")
    exit()

# Function to check if tables exist and create them if they do not
def check_and_create_tables():
    # Define the SQL statements to create tables if they do not exist
    tables = {
        "voters":
        """CREATE TABLE IF NOT EXISTS voters (voter_id INT PRIMARY KEY,has_voted BOOLEAN DEFAULT 0);""",
        "head_boy_votes":
        """CREATE TABLE IF NOT EXISTS head_boy_votes (candidate VARCHAR(255) PRIMARY KEY,
                votes INT DEFAULT 0,image_path VARCHAR(255));""",
        "head_girl_votes":
        """CREATE TABLE IF NOT EXISTS head_girl_votes (candidate VARCHAR(255) PRIMARY KEY,
                votes INT DEFAULT 0,image_path VARCHAR(255));"""}

    try:
        # Execute the creation statement for each table
        for table_name, create_statement in tables.items():
            cursor.execute(create_statement)
            db.commit()  # Commit changes to the database
            print(f"Table '{table_name}' checked/created successfully.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error checking/creating tables: {err}")
        db.rollback()  # Rollback in case of error

# Call this function at the start of the program to ensure tables exist
check_and_create_tables()

votes={}

#Fixing the window to the center
def center_window(window, width=800, height=700):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


#Function to make loading image Easier 
def load_image(image_path, size=(100, 100)):
    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image: {e}")
        placeholder_img = Image.new("RGB", size, color="gray")
        return ImageTk.PhotoImage(placeholder_img)

#Function for fade out Transition
def fade_out(window, duration=500, step=5):
    opacity = 1.0
    def reduce_opacity():
        nonlocal opacity
        opacity -= step / duration
        window.attributes("-alpha", opacity)
        if opacity > 0:
            window.after(10, reduce_opacity)
        else:
            window.withdraw()
    reduce_opacity()

#Function for fade in Transition
def fade_in(window, duration=500, step=5):
    opacity = 0.0
    window.deiconify()
    def increase_opacity():
        nonlocal opacity
        opacity += step / duration
        window.attributes("-alpha", opacity)
        if opacity < 1.0:
            window.after(10, increase_opacity)
    increase_opacity()

#Function to verify Voter ID
def verify_voter():
    voter_id = voter_id_entry.get()
    if not voter_id.isdigit():
        messagebox.showerror("Error", "Please enter a valid Voter ID.")
        return
    
    cursor.execute("SELECT has_voted FROM voters WHERE voter_id = %s", (voter_id,))
    result = cursor.fetchone()
    if result is None:
        messagebox.showerror("Error", "Voter ID not found.")
    elif result[0] == 1:
        messagebox.showerror("Error", "You have already voted.")
    else:
        root.withdraw()
        open_head_boy_window()

def open_admin_panel():
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin')  # Default fallback
    password = simpledialog.askstring("Admin Panel", "Enter admin password:", show="*")
    if password != admin_password:
        messagebox.showerror("Access Denied", "Incorrect password.")
        return
        
    # Create Admin Panel window
    admin_panel = tk.Toplevel(root)
    admin_panel.title("Admin Panel")
    admin_panel.geometry("700x700")
    admin_panel.configure(bg="#f0f4c3")
    

    tk.Label(admin_panel, text="Admin Panel", font=("Times new roman", 24, "bold"), bg="#f0f4c3",
             fg="#1b5e20").pack(pady=20)

    # Container for Head Boy and Head Girl sections
    candidate_frame = tk.Frame(admin_panel, bg="#e0f7fa")
    candidate_frame.pack(pady=10)

    # Head Boy Section
    head_boy_frame = tk.Frame(candidate_frame, bg="#f0f4c3", padx=20, pady=10)
    head_boy_frame.grid(row=0, column=0, sticky="n")

    tk.Label(head_boy_frame, text="Add Head Boy Candidate", font=("Times new Roman", 16, "bold")
             , bg="#f0f4c3").pack(pady=5)
    head_boy_name_label = tk.Label(head_boy_frame, text="Enter Name:", font=("Times new roman", 12),
                                   bg="#f0f4c3")
    head_boy_name_label.pack(pady=5)
    head_boy_name_entry = tk.Entry(head_boy_frame, font=("Times new Roman", 12))
    head_boy_name_entry.pack(pady=5)

    head_boy_image_label = tk.Label(head_boy_frame, text="Optional: Enter Image Path:",
                                    font=("Times new roman", 12), bg="#f0f4c3")
    head_boy_image_label.pack(pady=5)
    head_boy_image_entry = tk.Entry(head_boy_frame, font=("Times new Roman", 12))
    head_boy_image_entry.pack(pady=5)

    def add_head_boy_candidate():
        name = head_boy_name_entry.get().strip()
        image_path = head_boy_image_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the head boy candidate.")
            return
        add_candidate("head_boy_votes", name, image_path, admin_panel, head_boy_name_entry, head_boy_image_entry)
        messagebox.showinfo("Success", f"Head Boy candidate '{name}' added successfully.")

        head_boy_name_entry.delete(0, tk.END)
        head_boy_image_entry.delete(0, tk.END)

    tk.Button(head_boy_frame,text="Add Head Boy",font=("Times new roman", 12, "bold"),
        bg="#388e3c", fg="white", relief="flat",
        command=add_head_boy_candidate
    ).pack(pady=10)

    # Head Girl Section
    head_girl_frame = tk.Frame(candidate_frame, bg="#f0f4c3", padx=20, pady=10)
    head_girl_frame.grid(row=0, column=1, sticky="n")

    tk.Label(head_girl_frame, text="Add Head Girl Candidate", font=("Times new Roman", 16, "bold"),
             bg="#f0f4c3").pack(pady=5)
    head_girl_name_label = tk.Label(head_girl_frame, text="Enter Name:", font=("Times new roman", 12)
                                    , bg="#f0f4c3")
    head_girl_name_label.pack(pady=5)
    head_girl_name_entry = tk.Entry(head_girl_frame, font=("Times new Roman", 12))
    head_girl_name_entry.pack(pady=5)

    head_girl_image_label = tk.Label(head_girl_frame, text="Optional: Enter Image Path:",
                                     font=("Times new roman", 12), bg="#f0f4c3")
    head_girl_image_label.pack(pady=5)
    head_girl_image_entry = tk.Entry(head_girl_frame, font=("Times new Roman", 12))
    head_girl_image_entry.pack(pady=5)

    def add_head_girl_candidate():
        name = head_girl_name_entry.get().strip()
        image_path = head_girl_image_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the head girl candidate.")
            return
        add_candidate("head_girl_votes", name, image_path, admin_panel)
        messagebox.showinfo("Success", f"Head Girl candidate '{name}' added successfully.")
        head_girl_name_entry.delete(0, tk.END)
        head_girl_image_entry.delete(0, tk.END)

    tk.Button(head_girl_frame,text="Add Head Girl",font=("Times new roman", 12, "bold"),
        bg="#8e24aa", fg="white", relief="flat",
        command=add_head_girl_candidate).pack(pady=10)
    
    # Add a new voter
    tk.Label(admin_panel, text="Add Voter", font=("Times new roman", 16, "bold"), bg="#f0f4c3").pack(pady=20)
    voter_id_label = tk.Label(admin_panel, text="Enter Voter ID:", font=("Times new roman", 12), bg="#f0f4c3")
    voter_id_label.pack(pady=5)
    voter_id_entry = tk.Entry(admin_panel, font=("Times new Roman", 12))
    voter_id_entry.pack(pady=5)

    def add_voter_to_database(voter_id):
        try:
            cursor.execute("INSERT INTO voters (voter_id, has_voted) VALUES (%s, %s)", (voter_id, 0))
            db.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding voter: {err}")
            db.rollback()  # Rollback in case of error


    def add_voter():
        voter_id = voter_id_entry.get().strip()
        if not voter_id:
            messagebox.showerror("Error", "Please enter a voter ID.")
            return
        add_voter_to_database(voter_id)
        messagebox.showinfo("Success", f"Voter ID '{voter_id}' added successfully.")
        voter_id_entry.delete(0, tk.END)

    tk.Button(admin_panel,text="Add Voter",font=("Times new roman", 12, "bold"),
        bg="#1976d2", fg="white", relief="flat",
        command=add_voter).pack(pady=20)

    # View votes button
    tk.Button(admin_panel,text="View Vote Counts",font=("Times new roman", 14),
        bg="#00796b", fg="white", relief="flat",
        command=view_votes).pack(pady=20)


# Function to add a candidate to the database (head boy or head girl)
def add_candidate(role, candidate_name, image_path=None, admin_panel=None, name_entry=None, image_entry=None):
    if not candidate_name:
        messagebox.showerror("Error", "Candidate name cannot be empty.")
        return

    try:
        if image_path:
            cursor.execute(f"INSERT INTO {role}(candidate, image_path) VALUES (%s, %s)", (candidate_name, image_path))
        else:
            cursor.execute(f"INSERT INTO {role}(candidate) VALUES (%s)", (candidate_name,))

        db.commit()
        messagebox.showinfo("Success", f"{role.replace('_', ' ').title()} candidate added successfully!")

        # Confirm adding candidate and ask if they want to add another
        if messagebox.askyesno("Add Another Candidate?", "Do you want to add another candidate?"):
            # Clear the entries after success if the window is still open
            if name_entry and admin_panel.winfo_exists():
                name_entry.delete(0, tk.END)
            if image_entry and admin_panel.winfo_exists():
                image_entry.delete(0, tk.END)
        else:
            if admin_panel:
                admin_panel.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding candidate: {err}")
        db.rollback()  # Rollback in case of error


# Function to view the votes of all candidates (Head Boy and Head Girl)
def view_votes():
    try:
        cursor.execute("SELECT candidate, votes FROM head_boy_votes")
        head_boy_candidates = cursor.fetchall()

        cursor.execute("SELECT candidate, votes FROM head_girl_votes")
        head_girl_candidates = cursor.fetchall()

        vote_summary = "Head Boy Votes:\n"
        for candidate, votes in head_boy_candidates:
            vote_summary += f"{candidate}: {votes} votes\n"

        vote_summary += "\nHead Girl Votes:\n"
        for candidate, votes in head_girl_candidates:
            vote_summary += f"{candidate}: {votes} votes\n"

        messagebox.showinfo("Vote Counts", vote_summary)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching vote counts: {err}")


#Function to open and modify Head boy voting Window
def open_head_boy_window():
    global head_boy_window
    head_boy_window = tk.Toplevel(root)
    head_boy_window.title("Vote for Head Boy")
    head_boy_window.configure(bg="#e0f7fa")

    cursor.execute("SELECT candidate, image_path FROM head_boy_votes")
    candidates = cursor.fetchall()

    
    num_candidates = len(candidates)#Calculate the num of columns and rows based on the Num of candidates
    columns_num = 4  #Num of columns for the grid layout(can modify accordingly)
    rows = (num_candidates + columns_num - 1) // columns_num  # Calculate num of rows needed

    #Adjust the window size based on num of rows and columns
    window_width = 200 * columns_num + 50  #Width based on column count
    window_height = 250 * rows + 50  #Height based on row count 
    head_boy_window.geometry(f"{window_width}x{window_height}")

    center_window(head_boy_window)

    tk.Label(head_boy_window, text="Vote for Head Boy", font=("Times new roman", 28, "bold"),
             bg="#e0f7fa", fg="#004d40").pack(pady=70)
    button_frame = tk.Frame(head_boy_window, bg="#e0f7fa")
    button_frame.pack()

    column = 0
    row = 0
    for candidate, image_path in candidates:
        img = load_image(image_path, size=(100, 100))
        if img:
            image_label = tk.Label(button_frame, image=img, bg="#e0f7fa")
            image_label.image = img
            image_label.grid(row=row, column=column, padx=10)

            vote_button = tk.Button(
                button_frame, text=f"Vote for {candidate}", width=17, height=2, font=("Times new roman", 12),
                bg="#00796b", fg="white", relief="flat")
            vote_button.grid(row=row + 1, column=column, pady=5, padx=5)  

            # Adding hover effect
            def on_enter(event, button, og_color):
                button.config(bg="#004d40")  #Darker shade for hover effect
            def on_leave(event, button, og_color):
                button.config(bg=og_color)  # Reset to original color
            og_color = "#00796b"  # Default color
            vote_button.config(command=lambda c=candidate: store_vote("head_boy", c, open_head_girl_window))
            vote_button.bind("<Enter>", lambda e, b=vote_button, o=og_color: on_enter(e, b, o))
            vote_button.bind("<Leave>", lambda e, b=vote_button, o=og_color: on_leave(e, b, o))

            column += 1
            if column >= columns_num:  #Move to the next row after filling all columns
                column = 0
                row += 2  #Move down two rows (one for image and one for button)

    fade_in(head_boy_window)  #Apply fade-in effect


#Store votes temporarily and proceed to Head Girl voting
def store_vote(role, candidate, next_window_callback):
    global votes
    votes[role] = candidate  # Store the vote for Head Boy or Head Girl
    messagebox.showinfo("Success", f"Your vote for {candidate} has been recorded.")

    # If both votes are stored, proceed with updating the database and finish voting
    if "head_boy" in votes and "head_girl" in votes:
        try:
            # Update the votes for each selected candidate
            cursor.execute("UPDATE head_boy_votes SET votes = votes + 1 WHERE candidate = %s",
                           (votes["head_boy"],))
            cursor.execute("UPDATE head_girl_votes SET votes = votes + 1 WHERE candidate = %s",
                           (votes["head_girl"],))
            # Mark the voter as having voted
            voter_id = voter_id_entry.get()
            cursor.execute("UPDATE voters SET has_voted = 1 WHERE voter_id = %s", (voter_id,))

            db.commit()  # Commit all changes to the database
            print(f"Votes for {votes['head_boy']} and {votes['head_girl']} updated successfully.")
            finish_voting()  # Close the application after both votes are cast
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating the vote: {err}")
            db.rollback()  # Rollback in case of error
            return
    else:
        # Close the Head Boy window and proceed to the next window
        fade_out(head_boy_window, duration=250, step=5)  
        next_window_callback()

#Function to open Head Girl voting window
def open_head_girl_window():
    # Check if Head Boy voting is already done
    if "head_boy" not in votes:
        messagebox.showerror("Error", "You must vote for Head Boy first.")
        return

    head_girl_window = tk.Toplevel(root)
    head_girl_window.title("Vote for Head Girl")
    head_girl_window.configure(bg="#f3e5f5")  # Light pink background

    cursor.execute("SELECT candidate, image_path FROM head_girl_votes")
    candidates = cursor.fetchall()

    num_candidates = len(candidates)#Calculate the num of columns and rows based on the Num of candidates
    cols = 4  #Num of columns for the grid layout(can modify accordingly)
    rows = (num_candidates + cols - 1) // cols  #Calculate number of rows needed

    #Adjusts the window size based on number of rows and columns
    window_width = 200 * cols + 50  #Width based on column count 
    window_height = 250 * rows + 50 #Height based on row count 
    head_girl_window.geometry(f"{window_width}x{window_height}")

    center_window(head_girl_window)

    tk.Label(head_girl_window, text="Vote for Head Girl", font=("Times new roman", 28, "bold"),
             bg="#f3e5f5", fg="#004d40").pack(pady=70)
    button_frame = tk.Frame(head_girl_window, bg="#f3e5f5")
    button_frame.pack()

    column = 0
    row = 0
    for candidate, image_path in candidates:
        img = load_image(image_path, size=(100, 100))
        if img:
            image_label = tk.Label(button_frame, image=img, bg="#f3e5f5")
            image_label.image = img
            image_label.grid(row=row, column=column, padx=10)

            vote_button = tk.Button(
                button_frame, text=f"{candidate}", width=17, height=2, font=("=Times new roman", 12),
                bg="#8e24aa", fg="white", relief="flat")
            vote_button.grid(row=row + 1, column=column, pady=5, padx=5)  

            # Adding hover effect
            def on_enter(event, button, og_color):
                button.config(bg="#6a1b9a")  # Darker shade for hover effect
            def on_leave(event, button, og_color):
                button.config(bg=og_color)  # Reset to original color
            og_color = "#8e24aa"  # Default color
            vote_button.config(command=lambda c=candidate: store_vote("head_girl", c, finish_voting))
            vote_button.bind("<Enter>", lambda e, b=vote_button, o=og_color: on_enter(e, b, o))
            vote_button.bind("<Leave>", lambda e, b=vote_button, o=og_color: on_leave(e, b, o))

            column += 1
            if column >= cols:  # Move to the next row after filling all columns
                column = 0
                row += 2  # Move down two rows (one for image and one for button)

    fade_in(head_girl_window)  
    
# Finish Voting and close application
def finish_voting():
    messagebox.showinfo("Voting Complete", "Thank you for your vote!")
    root.destroy()  # Close the main application after voting is over

# Main Window
root = tk.Tk()
root.title("DIGIVOTE")
center_window(root)
root.configure(bg="#e0f7fa")

tk.Label(root, text="DIGIVOTE", font=("Times new roman", 26, "bold"), bg="#e0f7fa",
         fg="#004d40").pack(pady=50)
tk.Label(root, text="Enter your Voter ID:", font=("Times new roman", 24), bg="#e0f7fa",
         fg="#004d40").pack(pady=40)

voter_id_entry = tk.Entry(root, font=("Times new roman", 24))
voter_id_entry.pack(pady=40)

# Focus the cursor in the voter ID entry field
voter_id_entry.focus()

submit_button = tk.Button(root, text="VOTE", font=("Times new roman", 24), bg="#00796b",
                          fg="white", relief="flat", command=verify_voter)
submit_button.pack(pady=50)

# Add Admin Panel Button
admin_button = tk.Button(root, text="Admin Panel", font=("Times new roman", 18), bg="#00796b",
                         fg="white", command=open_admin_panel)
admin_button.pack(pady=20)

root.mainloop()
