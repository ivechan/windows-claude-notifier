from win11toast import toast
import sys

def main():
    try:
        toast('Test Title', 'Test Body', audio={'src': 'ms-winsoundevent:Notification.Default'})
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
