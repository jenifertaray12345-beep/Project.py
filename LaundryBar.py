from datetime import datetime

# para sa staff / admin
USERS = {"owner": ("owner123", "Owner"), "staff": ("staff123", "Staff")}
SHOP_NAME = "LAUNDRY BAR"
# prices of laundry bar service: (name, wash price, dry price) per 7kg
SERVICES = [
    ("Regular Clothes", 60, 50),
    ("Delicates", 80, 60),
    ("Bedsheets & Towels", 90, 70),
    ("Jackets & Denim", 100, 80),
    ("Comforter / Blanket", 150, 120),
]
PROCESSES = ["Wash Only", "Dry Only", "Wash & Dry"]
MAX_KG = 7

# ---- RACKS: A-01 ... A-05, B-01 ... B-05, C-01 ... C-05
# Change "ABC" to "ABCD" or range(1, 6) to range(1, 11) to add more racks.
RACKS = [f"{row}-{num:02d}" for row in "ABC" for num in range(1, 6)]

WIDTH = 40
LINE = "=" * WIDTH
DIVIDER = "-" * WIDTH

customers = []
orders = []


# ---------------------------------------------------------------- helpers
def banner(*titles):
    print(f"\n{LINE}")
    for title in titles:
        print(title.center(WIDTH))
    print(LINE)


def money(value):
    return f"PHP {value:,.2f}"


def timestamp(moment=None):
    moment = moment or datetime.now()
    return moment.strftime("%b %d, %Y %I:%M %p")


def count_items(items):
    count = 0
    for _ in items:
        count += 1
    return count


def pause():
    input("\nPress Enter to continue...")


# ---------------------------------------------------------------- input
def all_digits(text):
    if text == "":
        return False
    for character in text:
        if character < "0" or character > "9":
            return False
    return True


def get_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def get_no_digits(prompt, error):
    while True:
        value = input(prompt).strip()
        if value and not any("0" <= character <= "9" for character in value):
            return value
        print(error)


def get_name(prompt):
    return get_no_digits(prompt, "Invalid. Name cannot be empty or contain numbers.")


def get_items(prompt):
    return get_no_digits(prompt, "Invalid. Items can't be empty or contain numbers.")


def get_contact(prompt):
    while True:
        contact = input(prompt).strip()
        if all_digits(contact):
            return contact
        print("Invalid. Contact number must contain digits only.")


def get_number(prompt):
    while True:
        try:
            number = float(input(prompt).strip())
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if number > 0:
            return number
        print("Please enter a number greater than 0.")


def get_whole_number(prompt):
    while True:
        value = input(prompt).strip()
        if all_digits(value) and int(value) > 0:
            return int(value)
        print("Enter a whole number greater than 0.")


def get_choice(prompt, low, high):
    while True:
        choice = input(prompt).strip()
        if all_digits(choice) and low <= int(choice) <= high:
            return int(choice)
        print(f"Please enter a number between {low} and {high}.")


def get_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter Y or N.")


# ---------------------------------------------------------------- logic
def price_of(service, process):
    _, wash, dry = service
    if process == "Wash Only":
        return wash
    if process == "Dry Only":
        return dry
    return wash + dry


def login():
    for attempt in range(3):
        banner("STAFF / OWNER LOGIN")
        username = input("Username: ").strip().lower()
        password = input("Password: ").strip()
        if username in USERS and USERS[username][0] == password:
            role = USERS[username][1]
            login_time = datetime.now()          
            print(f"\nLogin successful! Welcome, {role}.")
            print(f"Logged in on: {timestamp(login_time)}")
            return role, login_time
        print(f"\nInvalid username or password. Attempts left: {2 - attempt}")
    print("\nToo many failed login attempts.")
    return None, None


# ---------------------------------------------------------------- racks
def get_available_racks():
    occupied = {o["rack"] for o in orders if o["status"] == "On Rack"}
    return [rack for rack in RACKS if rack not in occupied]


def select_rack():
    available = get_available_racks()
    if not available:
        print("\nNO AVAILABLE RACK SLOTS.")
        return None

    print("\n--- SELECT RACK ---")
    for number, rack in enumerate(available, start=1):
        print(f"{number:>2}. {rack}")
    print(" 0. Auto-assign first free rack")
    choice = get_choice(f"Enter choice (0-{count_items(available)}): ", 0, count_items(available))
    if choice == 0:
        return available[0]
    return available[choice - 1]


def rack_monitor():
    banner("RACK MONITOR")
    free = 0
    for rack in RACKS:
        holder = next((o for o in orders
                       if o["rack"] == rack and o["status"] == "On Rack"), None)
        if holder is None:
            free += 1
            print(f"{rack}  - AVAILABLE")
        else:
            print(f"{rack}  - {holder['receipt']} | {holder['name']}")
    print(DIVIDER)
    print(f"Occupied: {count_items(RACKS) - free} / {count_items(RACKS)}   Available: {free}")
    pause()


def release_order():
    banner("RELEASE LAUNDRY")
    number = get_text("Enter Receipt No. (e.g. RCPT0001): ").upper()
    order = next((o for o in orders if o["receipt"] == number), None)

    if order is None:
        print("\nReceipt not found.")
    elif order["status"] == "Released":
        print(f"\nThis order was already released on {order['released_date']}.")
    else:
        print(f"\nReceipt  : {order['receipt']}")
        print(f"Customer : {order['name']}")
        print(f"Service  : {order['service']} ({order['process']})")
        print(f"Rack     : {order['rack']}")
        if get_yes_no("\nConfirm release? (Y/N): "):
            order["status"] = "Released"
            order["released_date"] = timestamp()
            print(f"\nLaundry released. Rack {order['rack']} is now available.")
        else:
            print("\nRelease cancelled.")
    pause()


# ---------------------------------------------------------------- services
def show_services():
    print(f"{'#':<3}{'Service':<22}{'Wash':>7}{'Dry':>7}")
    print(DIVIDER)
    for number, (name, wash, dry) in enumerate(SERVICES, start=1):
        print(f"{number:<3}{name:<22}{wash:>7.2f}{dry:>7.2f}")


def view_services():
    banner("LAUNDRY SERVICES", f"Prices are per {MAX_KG}kg (PHP)")
    show_services()
    print(LINE)
    pause()


def choose_service():
    while True:
        print("\n--- SELECT LAUNDRY SERVICE ---")
        show_services()
        print("0  Back to Main Menu")
        choice = get_choice(f"\nEnter choice (0-{count_items(SERVICES)}): ", 0, count_items(SERVICES))
        if choice == 0:
            return None
        service = SERVICES[choice - 1]

        print("\n--- SELECT PROCESS ---")
        for number, process in enumerate(PROCESSES, start=1):
            print(f"{number}. {process} - {money(price_of(service, process))} / {MAX_KG}kg")
        print("0. Back")
        choice = get_choice(f"Enter choice (0-{count_items(PROCESSES)}): ", 0, count_items(PROCESSES))
        if choice != 0:
            return service, PROCESSES[choice - 1]


# ---------------------------------------------------------------- customers
def get_customer():
    banner("CUSTOMER INFORMATION FORM")
    name = get_name("Full Name: ")
    for customer in customers:
        if customer["name"].lower() == name.lower():
            print(f"\nReturning customer found: {customer['name']}")
            print(f"Contact: {customer['contact']}")
            print(f"Address: {customer['address']}")
            if get_yes_no("Use this saved information? (Y/N): "):
                return customer
            customer["contact"] = get_contact("Contact Number: ")
            customer["address"] = get_text("Address: ")
            print("\nCustomer information updated.")
            return customer

    customer = {
        "name": name,
        "contact": get_contact("Contact Number: "),
        "address": get_text("Address: "),
    }
    customers.append(customer)
    print("\nNew customer information saved.")
    return customer


# ---------------------------------------------------------------- receipt
def print_receipt(order):
    print(f"\n{LINE}")
    print(SHOP_NAME.center(WIDTH))
    print("OFFICIAL RECEIPT".center(WIDTH))
    print(LINE)
    print(f"Receipt No.  : {order['receipt']}")
    print(f"Date & Time  : {order['date']}")
    print(f"Customer     : {order['name']}")
    print(f"Contact      : {order['contact']}")
    print(f"Address      : {order['address']}")
    print(f"Served by    : {order['served_by']}")
    print(DIVIDER)
    print(f"Items        : {order['items']}")
    print(f"Total Pieces : {order['pieces']}")
    print(DIVIDER)
    print(f"Service      : {order['service']}")
    print(f"Process      : {order['process']}")
    print(f"Weight       : {order['weight']:g} kg (max {MAX_KG}kg)")
    print(f"Rack         : {order['rack']}")
    print(f"Status       : {order['status']}")
    print(DIVIDER)
    print(f"{'TOTAL:':<22}{money(order['total']):>18}")
    print(f"{'Amount Paid:':<22}{money(order['paid']):>18}")
    print(f"{'Change:':<22}{money(order['paid'] - order['total']):>18}")
    print(LINE)
    print("Thank you for choosing us!".center(WIDTH))
    print(LINE)


def new_order(role):
    banner("NEW LAUNDRY ORDER")
    if not get_available_racks():
        print("\nNO AVAILABLE RACK SLOTS. Release some laundry first.")
        pause()
        return

    selection = choose_service()
    if selection is None:
        return
    service, process = selection

    customer = get_customer()

    print("\n--- RECORD LAUNDRY ITEMS ---")
    items = get_items("Items (e.g. Shirts, Pants, Towels): ")
    pieces = get_whole_number("Total pieces: ")

    while True:
        weight = get_number(f"Total weight (kg, max {MAX_KG}): ")
        if weight <= MAX_KG:
            break
        print(f"Maximum is {MAX_KG}kg only.")

    rack = select_rack()
    if rack is None:
        pause()
        return

    total = price_of(service, process)
    print(f"\nTotal Amount Due: {money(total)}")
    paid = get_number("Enter Amount Paid: PHP ")
    while paid < total:
        print("Amount paid is less than the total due.")
        paid = get_number("Enter Amount Paid: PHP ")

    order = {
        "receipt": f"RCPT{count_items(orders) + 1:04d}",
        "date": timestamp(),                     
        "name": customer["name"],
        "contact": customer["contact"],
        "address": customer["address"],
        "service": service[0],
        "process": process,
        "items": items,
        "pieces": pieces,
        "weight": weight,
        "rack": rack,
        "status": "On Rack",                     
        "total": total,
        "paid": paid,
        "served_by": role,
    }
    orders.append(order)
    print("\nLaundry order recorded successfully!")
    print_receipt(order)
    pause()


# ---------------------------------------------------------------- records
def view_history():
    banner("TRANSACTION HISTORY")
    if not orders:
        print("No transactions yet.")
        pause()
        return

    for order in reversed(orders):
        print(f"[{order['receipt']}] {order['date']}\n"
              f"   {order['name']} - {order['service']} "
              f"({order['process']}) = {money(order['total'])}\n"
              f"   Rack: {order['rack']} | Status: {order['status']}")
    print(DIVIDER)
    print(f"Total Transactions: {count_items(orders)}")
    print(f"Total Sales: {money(sum(o['total'] for o in orders))}")

    if get_yes_no("\nReprint a receipt? (Y/N): "):
        number = get_text("Enter Receipt No. (e.g. RCPT0001): ").upper()
        for order in orders:
            if order["receipt"] == number:
                print_receipt(order)
                break
        else:
            print("\nReceipt not found.")
    pause()


# ---------------------------------------------------------------- main
def main_menu(role, login_time):
    while True:
        banner(SHOP_NAME, "SERVICE RECEIPT SYSTEM",
               f"Status: {role}",
               f"Logged in: {timestamp(login_time)}",
               f"Current Time: {timestamp()}")
        print("1. Laundry Order (Receipt)")
        print("2. View Laundry Services")
        print("3. History")
        print("4. Rack Monitor")
        print("5. Release Laundry (Pickup)")
        print("6. Logout")
        print(LINE)

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            new_order(role)
        elif choice == "2":
            view_services()
        elif choice == "3":
            view_history()
        elif choice == "4":
            rack_monitor()
        elif choice == "5":
            release_order()
        elif choice == "6":
            print(f"\nLogging out {role}...")
            print(f"Thank you for using {SHOP_NAME}.")
            break
        else:
            print("\nInvalid choice. Please select a number from 1 to 6.")


def main():
    banner(f"WELCOME TO {SHOP_NAME}", "SERVICE RECEIPT SYSTEM")

    role, login_time = login()
    if role:
        main_menu(role, login_time)

    print("\nProgram ended.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram stopped by user.")