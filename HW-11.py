import re
from collections import UserDict
from datetime import date

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            print('There isn\'t contact with this name or number.')
        except ValueError:
            print('''Please enter the correct format of name and phone number.
            Correct format:
            1. The length of the nunber must be only 12 digits.
            2. Birthday format: YYYY-MM-DD.
            2. Use a gap between name, number and birthday.''')
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value

class Name(Field):
    def __init__(self, value):
      if not value:
        raise ValueError('Name cannot be empty')
      super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if value:
            if not isinstance(value, str):
                raise TypeError('Phone must be a string')
            if not value.isdigit():
                raise ValueError('Phone must be a combination of digits')
            if len(value) != 12:
                raise ValueError('Phone number must have a 12 digits')
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value and not isinstance(new_value, str):
            raise TypeError('Phone must be a string')
        elif new_value and len(new_value) != 12:
            raise ValueError('Phone must be a string of length 12')
        self._value = new_value

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value and not isinstance(new_value, date):
            raise ValueError('Birthday must have a format yyyy-mm-dd')
        self._value = new_value

    def replace(self, year):
        if self._value:
            self._value = date(self._value.year, self._value.month, self._value.day)

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = []
        if phone:
            self.add_phone(phone)
        if birthday:
            self.birthday = birthday
        else:
            self.birthday = None

    def add_phone(self, phone):
        self.phones.append(phone)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone.value:
                self.phones[i] = new_phone

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        next_birthday = self.birthday.replace(year=today.year)
        if next_birthday and next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
            if next_birthday.year - today.year > 1:
                return None
        if next_birthday:
            days_to_birthday = (next_birthday - today).days
            return days_to_birthday

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False
    
    def find_records_by_name(self, name):
        found_records = []
        for record_name in self.data.keys():
            if record_name.lower() == name.lower():
                found_records.append(self.data[record_name])
        return found_records

    def find_records_by_phone(self, phone):
        found_records = []
        for record in self.data.values():
            for record_phone in record.phones:
                if record_phone.value == phone:
                    found_records.append(record)
        return found_records

    def iterator(self, n=2):
        num_items = len(self.data)
        i = 0
        while i < num_items:
            result = []
            for key, value in list(self.items())[i:i + n]:
                result.append(f"{key}: {', '.join([phone.value for phone in value.phones])}")
            yield result
            i += n
        if len(result) < n:
            yield []

    def change_phone(self, name, old_phone, new_phone):
        if name in self.data:
            record = self.data[name]
            if not isinstance(old_phone, Phone):
                old_phone = Phone(old_phone)
            if not isinstance(new_phone, Phone):
                new_phone = Phone(new_phone)
            if record.edit_phone(old_phone, new_phone):
                print(f'Phone number for contact {name} has been changed from {old_phone} to {new_phone}.')

@input_error
def add_contact(user_input, address_book):
    match = re.match(r'add (\w+) (\d{12}) ?(\d{4}-\d{2}-\d{2})?', user_input)
    if match:
        name = match.group(1)
        phone = match.group(2)
        birthday = match.group(3)
        record_name = Name(name)
        if birthday:
            record_birthday = Birthday(date.fromisoformat(birthday))
        else:
            record_birthday = None
        record = Record(record_name, Phone(phone), record_birthday)
        address_book.add_record(record)
    else:
      raise ValueError

def show_all_contacts(address_book):
    if address_book:
        for name, record in address_book.items():
            phone_numbers = ', '.join([phone.value for phone in record.phones])
            birthday = record.birthday.value.strftime('%Y-%m-%d') if record.birthday else ''
            days_to_birthday = record.days_to_birthday()
            if days_to_birthday:
                print(f'{name}: {phone_numbers}  {birthday}  {days_to_birthday} days until birthday')
            else:
                print(f'{name}: {phone_numbers} {birthday}')
    else:
        print('There are no contacts.')

def remove_contact(user_input, address_book):
    match = re.match(r'remove (\w+)', user_input)
    if match:
        name = match.group(1)
        if address_book.remove_record(name):
            print(f'Contact {name} has been removed.')
        else:
            print(f'There is no contact with name "{name}".')

@input_error
def find_contacts(user_input, address_book):
    match = re.match(r'find (\w+)', user_input)
    if match:
        name_or_phone = match.group(1)
        records_by_name = address_book.find_records_by_name(name_or_phone)
        records_by_phone = address_book.find_records_by_phone(name_or_phone)
        if records_by_name or records_by_phone:
            print('Contacts found:')
            for record in records_by_name + records_by_phone:
                for phone in record.phones:
                    print(f'{record.name.value} - {phone.value}')
        else:
            print('No contacts were found.')
    else:
        raise KeyError
    
def show_contact_book(address_book):
    iterator = address_book.iterator()
    while True:
        result = next(iterator, None)
        if result is None:
            break
        print('\n'.join(result))
        input('Press any key to continue...')

def change_phone(user_input, address_book):
    match = re.match(r'change (\w+) (\d{12}) (\d{12})', user_input)
    if match:
        name = match.group(1)
        old_phone = match.group(2)
        new_phone = match.group(3)
        address_book.change_phone(name, Phone(old_phone), Phone(new_phone))

def main():
    print('''What can this bot do?
    1. Save the contact (name, phone number and birthday). Please, remember: number - only 12 digits. Birthday format: YYYY-MM-DD.
    Use command: add [name] [number] [birthday].
    2. Change the phone number of the recorded contact. Please, remember: number - only 12 digits.
    Use command: change [name] [old_number] [new_number]
    3. Show all previously saved contacts with their names, phones and birthdays.
    Use command: show all.
    4. If your adress book contain a lots of contacts, you can see the parts of your book. 2 contacts at a time.
    Use command: show in parts. And then press 'Enter' to see the next page. 
    5. Remove the contact.
    Use command: remove [name]
    6. Find the contact by name or by phone.
    Use command: find [name] or [phone]''')
    address_book = AddressBook()
    while True:
        user_input = input('Enter a command >>> ')
        if user_input.lower() == 'hello':
            print('How can I help you?')
        elif user_input.lower().startswith('add'):
            add_contact(user_input, address_book)
        elif user_input.lower() == 'show all':
            show_all_contacts(address_book)
        elif user_input.lower().startswith('remove'):
            remove_contact(user_input, address_book)
        elif user_input.lower().startswith('find'):
            find_contacts(user_input, address_book)
        elif user_input.lower() == 'show in parts':
            show_contact_book(address_book)
        elif user_input.lower().startswith('change'):
            change_phone(user_input, address_book)
        elif user_input.lower() in ['exit', 'close', 'good bye']:
            print('Good bye!')
            raise SystemExit
        else:
            print('Sorry, I don\'t understand you. Use the available command.')


if __name__ == '__main__':
    main()