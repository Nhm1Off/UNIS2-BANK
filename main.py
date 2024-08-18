import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import telebot

# Введіть ваш токен від Telegram BotFather тут
TOKEN = '7540664220:AAH-8jcEDyYRkGSbTWo9ePoQqrumwFV81X0'
bot = telebot.TeleBot(TOKEN)

# Файл для зберігання даних
DATA_FILE = "user_balances.json"

# Завантажуємо дані з файлу
def load_balances():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}  # Повертаємо порожній словник, якщо файл порожній або некоректний
    return {}

# Зберігаємо дані у файл
def save_balances(balances):
    with open(DATA_FILE, "w") as file:
        json.dump(balances, file)

# Завантажуємо баланс користувачів при запуску
user_balances = load_balances()

class MyTelegramApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.transfer_button = Button(text='Перевести кошти')
        self.transfer_button.bind(on_press=self.open_transfer_popup)
        self.layout.add_widget(self.transfer_button)

        self.add_balance_button = Button(text='Поповнення балансу')
        self.add_balance_button.bind(on_press=self.open_add_balance_popup)
        self.layout.add_widget(self.add_balance_button)

        self.send_balance_button = Button(text='Відправити баланс')
        self.send_balance_button.bind(on_press=self.open_send_balance_popup)
        self.layout.add_widget(self.send_balance_button)
        
        return self.layout

    def open_transfer_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical')
        
        self.sender_input = TextInput(hint_text='Ваш Chat ID')
        popup_layout.add_widget(self.sender_input)
        
        self.recipient_input = TextInput(hint_text='Тег або телефон отримувача')
        popup_layout.add_widget(self.recipient_input)
        
        self.transfer_amount_input = TextInput(hint_text='Сума для переказу')
        popup_layout.add_widget(self.transfer_amount_input)
        
        transfer_confirm_button = Button(text='Перевести')
        transfer_confirm_button.bind(on_press=self.transfer_balance)
        popup_layout.add_widget(transfer_confirm_button)
        
        close_button = Button(text='Закрити')
        close_button.bind(on_press=lambda x: popup.dismiss())
        popup_layout.add_widget(close_button)
        
        popup = Popup(title='Перевести кошти', content=popup_layout, size_hint=(0.8, 0.5))
        popup.open()

    def open_add_balance_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical')

        self.chat_id_input = TextInput(hint_text='Ваш Chat ID')
        popup_layout.add_widget(self.chat_id_input)
        
        self.add_balance_input = TextInput(hint_text='Сума для додавання')
        popup_layout.add_widget(self.add_balance_input)
        
        add_balance_confirm_button = Button(text='Додати')
        add_balance_confirm_button.bind(on_press=self.add_balance)
        popup_layout.add_widget(add_balance_confirm_button)
        
        close_button = Button(text='Закрити')
        close_button.bind(on_press=lambda x: popup.dismiss())
        popup_layout.add_widget(close_button)
        
        popup = Popup(title='Поповнення балансу', content=popup_layout, size_hint=(0.8, 0.4))
        popup.open()

    def open_send_balance_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical')

        self.chat_id_input = TextInput(hint_text='Ваш Chat ID')
        popup_layout.add_widget(self.chat_id_input)

        send_balance_confirm_button = Button(text='Відправити баланс в Telegram')
        send_balance_confirm_button.bind(on_press=self.send_balance_message)
        popup_layout.add_widget(send_balance_confirm_button)

        close_button = Button(text='Закрити')
        close_button.bind(on_press=lambda x: popup.dismiss())
        popup_layout.add_widget(close_button)

        popup = Popup(title='Відправити баланс', content=popup_layout, size_hint=(0.8, 0.3))
        popup.open()

    def add_balance(self, instance):
        chat_id = self.chat_id_input.text
        if chat_id and self.add_balance_input.text.isdigit():
            amount = int(self.add_balance_input.text)
            # Оновлюємо баланс користувача
            if chat_id in user_balances:
                user_balances[chat_id] += amount
            else:
                user_balances[chat_id] = amount
            save_balances(user_balances)  # Зберігаємо баланс після оновлення
            self.add_balance_input.text = ''
        else:
            self.balance_label.text = 'Помилка: введіть правильні дані!'

    def send_balance_message(self, instance):
        chat_id = self.chat_id_input.text
        if chat_id in user_balances:
            balance = user_balances[chat_id]
            bot.send_message(chat_id=chat_id, text=f'Ваш поточний баланс: {balance}')
        else:
            bot.send_message(chat_id=chat_id, text='Вашого аккаунту немає у системі.')

    def transfer_balance(self, instance):
        sender_chat_id = self.sender_input.text
        recipient_info = self.recipient_input.text
        transfer_amount = self.transfer_amount_input.text

        if sender_chat_id and recipient_info and transfer_amount.isdigit():
            transfer_amount = int(transfer_amount)

            if sender_chat_id in user_balances and user_balances[sender_chat_id] >= transfer_amount:
                recipient_chat_id = None

                # Знаходимо отримувача за тегом або телефоном
                for chat_id, balance in user_balances.items():
                    if chat_id == recipient_info:
                        recipient_chat_id = chat_id
                        break

                if recipient_chat_id:
                    # Проводимо переказ коштів
                    user_balances[sender_chat_id] -= transfer_amount
                    user_balances[recipient_chat_id] += transfer_amount
                    save_balances(user_balances)
                    bot.send_message(chat_id=sender_chat_id, text=f'Переказано {transfer_amount} користувачу {recipient_chat_id}')
                else:
                    bot.send_message(chat_id=sender_chat_id, text='Помилка: отримувач не знайдений!')
            else:
                bot.send_message(chat_id=sender_chat_id, text='Помилка: недостатньо коштів або неправильні дані!')
        else:
            bot.send_message(chat_id=sender_chat_id, text='Помилка: введіть правильні дані!')

if __name__ == '__main__':
    MyTelegramApp().run()
