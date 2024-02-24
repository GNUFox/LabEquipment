

def ask_user_if_ok():
    print("")
    user_in: str = ""
    try:
        user_in = input("Is this correct? (Y/n)")
    except KeyboardInterrupt:
        return False

    if user_in.upper() == 'Y' or user_in == "":
        return True
    elif user_in.upper() == 'N':
        return False
    else:
        print()
