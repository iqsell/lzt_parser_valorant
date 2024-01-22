from LolzteamApi import LolzteamApi
import json
from aiogram import Bot, Dispatcher, types, Router
import asyncio
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

# Ваши данные для Telegram
TOKEN = ''

# Инициализируем бот и диспетчер
bot: Bot = Bot(token=TOKEN)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())
router: Router = Router()

# Список для хранения ID пользователей
user_ids = []


# Обработчик команды /start
@router.message(Command('start'))
async def start(message: Message):
    user_id = message.from_user.id
    if user_id not in user_ids:
        user_ids.append(user_id)


# Функция для отправки сообщений в Telegram
async def send_message(message):
    for user_id in user_ids:
        await bot.send_message(user_id, message)


# Загрузка предыдущих данных
try:
    with open('filtered_valorant_data.json', 'r') as file:
        if file.read():
            file.seek(0)  # перемещаем указатель обратно в начало файла
            old_data = json.load(file)
        else:
            old_data = []
except FileNotFoundError:
    old_data = []
# lzt token
api = LolzteamApi(token="", language="en")


async def parse_and_send():
    while True:
        data = api.market.list.from_url(url="https://lzt.market/valorant/")
        # Modify the item and include the URL
        for item in data['items']:
            item['parsed_from_url'] = "https://lzt.market/valorant/"

        # Filter data based on the condition 'valorantRegionPhrase': 'North America' and 'valorant_wallet_vp' >= 2751
        filtered_data = [item for item in data['items'] if 'valorantRegionPhrase' in item and item[
            'valorantRegionPhrase'] == 'North America' or item[
                             'valorantRegionPhrase'] == 'Europe' and 'valorant_wallet_vp' in item and item[
                             'valorant_wallet_vp'] >= 2751]

        new_data = []

        for i in filtered_data:
            message = (f"Price: {i['price']} rub\nLink: https://lzt.market/{i['item_id']} {i['valorant_inventory_value']}"
                       f" {i['valorantRegionPhrase']}")
            if message not in old_data:
                new_data.append(message)

        # Запись новых данных в файл
        with open('filtered_valorant_data.json', 'w') as file:
            json.dump(new_data + old_data, file, indent=4)

        # Отправка новых данных
        for message in new_data:
            await bot.send_message(5052126255, message)

        # Обновление старых данных
        old_data.extend(new_data)

        await asyncio.sleep(6)
        print('updated')


async def main():
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(dp.start_polling(bot))
    parsing_task = asyncio.create_task(parse_and_send())

    await asyncio.gather(polling_task, parsing_task)


if __name__ == '__main__':
    asyncio.run(main())
