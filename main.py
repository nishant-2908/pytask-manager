# Importing the necessary libraries
from cs50 import SQL
from helper import *
from werkzeug.security import check_password_hash, generate_password_hash
from getpass import getpass
import sys
from prettytable import PrettyTable
import datetime
import os


def create_database():
    """Creates the database."""

    # Checking if the file exists
    if not os.path.exists(os.path.join(os.getcwd(), "database.db")):

        # Creating a new file in write mode
        with open("database.db", "w") as file:

            # Pass
            pass


# Running the function
create_database()

# Connecting a database
db = SQL("sqlite:///database.db")


def init_database():
    """Initializes the database with the tables."""
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS "users" (
            "user_id"    INTEGER NOT NULL UNIQUE,
            "username"   TEXT NOT NULL UNIQUE,
            "first_name" TEXT NOT NULL,
            "last_name"  TEXT NOT NULL,
            "password"   TEXT NOT NULL,
            PRIMARY KEY("user_id" AUTOINCREMENT)
        );
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS "tasks"(
            "task_id"      INTEGER NOT NULL UNIQUE,
            "user_id"      INTEGER NOT NULL,
            "title"        TEXT NOT NULL,
            "description"  TEXT NOT NULL,
            "deadline"     DATE,
            "completed"    BOOLEAN NOT NULL,
            "completed_at" DATE,
            PRIMARY KEY("task_id" AUTOINCREMENT)
        );
        """
    )


def validate_date(date_string, date_format="%Y-%m-%d"):
    """Checking if the date is valid."""
    try:
        datetime.datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def main():
    """Main function."""

    # Printing the welcome message
    print("Welcome to Task Manager! \n")

    # Getting if the user wants to register or login
    user_mode = input_in_options(
        "Enter the mode (Login [L] / Register [R]): ",
        ["L", "R"],
    )

    # If the user wants to register
    if user_mode.upper().strip() == "R":

        # Taking the inputs for first name and last name
        username = take_input_as_string("Enter the username: ")
        first_name = take_input_as_string("Enter the first name: ")
        last_name = take_input_as_string("Enter the last name: ")
        password = getpass("Enter the password: ")

        # Inserting the user into the database
        try:
            new_user_id = db.execute(
                """
                INSERT INTO users (username, first_name, last_name, password)
                VALUES (?, ?, ?, ?)
                """,
                username,
                first_name,
                last_name,
                generate_password_hash(password),
            )

        # If the query returns the error
        except ValueError:

            # Print an error message
            print("User already exists!")

            # Return the function
            return

        # Printing the success message
        print(f"\nSuccessfully Registered with User ID: {new_user_id}!")

        # Returning the functipon
        return

    elif user_mode.upper().strip() == "L":

        # Getting the username
        username = take_input_as_string("Enter the username: ")

        # Running a while loop to get the password
        while True:

            # Getting the password using a secure input
            password = getpass("Enter the password: ")

            # If the password is not empty
            if password.strip() == "":

                # Printing an error message
                print("Please enter a valid password.")

                # Continuing the loop
                continue

            # Breaking the loop if the password is not empty
            break

        # Getting the users for the given username
        users = db.execute(
            """
            SELECT * FROM users
            WHERE username = ?
            """,
            username,
        )

        # If the length of the response of the above query is zero
        if len(users) == 0:

            # Print an error message
            print("No such user exists.")

            return

        # Checking if the password is incorrect
        if not check_password_hash(users[0]["password"], password):

            # Printing the error message
            print("\nUnsuccessfully Log In!")

            # Returning the function
            return

        # Printing the success message
        print("\nSuccessfully Log In!\n")

        # Asking the user mode
        logged_user_mode = input_in_options(
            "Enter the option (Add Task [T] / View Tasks [V] / Mark Task Complete [M] / Delete Task [D]): ",
            ["T", "V", "M", "D"],
        )

        # If the user wants to add an task
        if logged_user_mode.upper().strip() == "T":

            # Asking for the task
            task_name = take_input_as_string("Enter the task name: ")

            # Running a while loop
            while True:

                # Asking for the task name
                task_date = input("Date (YYYY-MM-DD [Optional]): ")

                # If the user did enter any date
                if len(task_date) != 0:

                    # Getting off the extra spaces
                    task_date = task_date.strip()

                    # Checking the date
                    if not validate_date(task_date):

                        # Printing the error message
                        print("Please enter a valid date.")

                        # Continuing the loop
                        continue

                    # Checking if the date entered is less than today's date
                    elif (
                        datetime.datetime.strptime(task_date, "%Y-%m-%d").date()
                        < datetime.date.today()
                    ):

                        # Printing the error message
                        print("Please enter a valid date.")

                        # Continuing the loop
                        continue

                    # Breaking the loop
                    break

                # If the user didn't enter any date
                else:

                    # Breaking the loop
                    break

            # Getting the description
            task_description = input("Description (Optional): ")

            # Registering the task in the database
            new_task_id = db.execute(
                """
                INSERT INTO tasks (user_id, title, description, deadline, completed)
                VALUES (?, ?, ?, ?, ?)
                """,
                users[0]["user_id"],
                task_name,
                "-" if task_description is None else task_description,
                "-" if task_date is None else task_date,
                False,
            )

            # Printing the success message
            print("Successfully Added Task with ID: {} !".format(new_task_id))

            # Returning the function
            return

        elif logged_user_mode.upper().strip() == "V":

            # Getting the tasks
            tasks = db.execute(
                """
                SELECT * FROM tasks
                WHERE user_id = ?
                AND completed = ?
                """,
                users[0]["user_id"],
                False,
            )

            # If the length of the list returned is zero
            if len(tasks) == 0:

                # Printing an INFO message
                print("No incomplete tasks found!")

                # Returning the message
                return

            # Printing the tasks
            task_table = PrettyTable()

            # Defining the task's table's row
            task_table.field_names = [
                "ID",
                "Title",
                "Description",
                "Deadline",
                "Completed",
            ]

            # For each task
            for task in tasks:

                # Adding the task to the table
                task_table.add_row(
                    [
                        task["task_id"],
                        task["title"],
                        task["description"],
                        task["deadline"],
                        task["completed"],
                    ]
                )

            # Printing the table
            print(task_table)

            # Returning the table
            return

        # If the user wants to modify the task
        elif logged_user_mode.upper().strip() == "M":

            # Getting the tasks
            user_tasks = db.execute(
                """
                SELECT * FROM tasks
                WHERE user_id = ?
                AND completed = ?
                """,
                users[0]["user_id"],
                False,
            )

            # Checking if the query returned no elements
            if len(user_tasks) == 0:

                # Printing an info message
                print("No tasks found! ")

                # Returning the function
                return

            # Printing the tasks
            task_table = PrettyTable()

            # Defining the task's table's row
            task_table.field_names = [
                "Serial Number",
                "Title",
                "Description",
                "Deadline",
            ]

            # For each task
            for i, task in enumerate(user_tasks):

                # Adding the task to the table
                task_table.add_row(
                    [
                        str(i + 1),
                        task["title"],
                        task["description"],
                        task["deadline"],
                    ]
                )

            # Printing the table
            print(task_table)

            # Taking the input for the task ID
            task_id = input_in_options(
                "Enter the Serial Number of the task you want to mark as complete: ",
                options=[str(i) for i in range(1, len(user_tasks) + 1)],
            )

            # Marking the task as complete
            db.execute(
                """
                UPDATE tasks
                SET completed = ?, completed_at = ?
                WHERE task_id = ?
                """,
                True,
                datetime.datetime.now().strftime("%Y-%m-%d"),
                user_tasks[int(task_id) - 1]["task_id"],
            )

            # Printing a success message
            print("Successfully Marked Task as Complete! ")

            # Returning the function
            return

        elif logged_user_mode.upper().strip() == "D":

            # Getting the tasks for the user
            user_tasks = db.execute(
                """
                SELECT * FROM tasks
                WHERE user_id = ?
                AND completed = ?
                """,
                users[0]["user_id"],
                False,
            )

            # Checking if the query returned no elements
            if len(user_tasks) == 0:

                # Printing an info message
                print("No tasks found! ")

                # Returning the function
                return

            # Printing the tasks
            task_table = PrettyTable()

            # Defining the task's table's row
            task_table.field_names = [
                "Serial Number",
                "Title",
                "Description",
                "Deadline",
            ]

            # For each task
            for i, k in enumerate(task_table):

                # Adding the task to the table
                task_table.add_row(
                    [
                        str(i + 1),
                        k["title"],
                        k["description"],
                        k["deadline"],
                    ]
                )

            # Printing the table
            print(task_table)

            # Getting the Serial Number of the task the user want to delete
            task_id = input_in_options(
                "Enter the Serial Number of the task you want to delete: ",
                options=[str(i) for i in range(1, len(user_tasks) + 1)],
            )

            # Deleting the task
            db.execute(
                "DELETE FROM tasks WHERE task_id = ?",
                user_tasks[int(task_id) - 1]["task_id"],
            )

            # Printing an successful message
            print("Successfully Deleted Task! ")

            # Returning the function
            return


if __name__ == "__main__":
    try:
        init_database()
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(1)
