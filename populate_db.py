import csv

from models import Account, db

# generate hashed password using Bcrypt
def hash_password(password, bcrypt_instance):
    hashed_pw = bcrypt_instance.generate_password_hash(password).decode("UTF-8")
    return hashed_pw


def populate_db(filepath, bcrypt_instance):
    try:
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            next(reader)  # skip the header row
            for row in reader:
                hashed_password = hash_password(row[3], bcrypt_instance)
                # skip if the user exists (no updates)
                existing_user = Account.query.filter_by(email=row[2]).first()
                if existing_user:
                    print(f"Skipping as User with email {row[2]} already exists.")
                    continue
                else:
                    user = Account(
                        first_name=row[0],
                        last_name=row[1],
                        email=row[2],
                        password=hashed_password,
                    )
                    # add the account and commit
                    try:
                        db.session.add(user)
                        db.session.commit()
                    except Exception as e:
                        print(f"Error occurred while adding users to DB: \n{e}\n")
                        db.session.rollback()
    except FileNotFoundError:
        print(f"File {filepath} not found!")
    except csv.Error as csv_error:
        print(f"Error occurred while processing CSV: \n{csv_error}\n")
    except Exception as e:
        print(f"An unexpected error occurred: \n{e}\n")
