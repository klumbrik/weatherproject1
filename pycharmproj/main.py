from fastapi import FastAPI
import httpx
import sqlite3
#import json

conn = sqlite3.connect("weather.db")
#создание курсора
c = conn.cursor()
app = FastAPI()

c.execute('''CREATE TABLE IF NOT EXISTS previous_requests
            (city text, weather_data text)''')
conn.commit()
@app.get("/")
async def hello():
    return {"message": "Hello World"}


# база sqlite
@app.on_event("shutdown")
def shutdown_event():
    # Очищаем таблицу previous_requests
    c.execute('DELETE FROM previous_requests')
    # Коммитим изменения
    conn.commit()
    # Закрываем соединение с базой данных
    conn.close()


#датаза прошлое ручка
@app.get("/weather/previous_cities")
async def get_previous_weather():
    # Получаем все предыдущие запросы о погоде из базы данных
    c.execute('SELECT city, weather_data FROM previous_requests')
    previous_data = c.fetchall()


    # Формируем ответ в виде списка словарей
    result = [{"city": city, "weather_data": weather_data} for city, weather_data in previous_data]
    # Преобразуем список словарей в формат JSON с отступами для читаемости
    #formatted_result = json.dumps(result, indent=2)
    # Возвращаем отформатированный JSON в HTTP-ответе
    #вернуть ресулт обычный
    return result




@app.get("/weather/{city}")
async def get_weather(city: str):
    # Проверяем, есть ли предыдущий запрос для данного города в базе данных
    c.execute('SELECT weather_data FROM previous_requests WHERE city=?', (city,))
    previous_data = c.fetchone()

    if previous_data:
        # Если есть предыдущий запрос, возвращаем сохраненные данные
        print('yes') #проверка
        return previous_data[0]
    else:
        api_key = "f8f915e1eb20ce5635fd182ae1cd0d64"
        base_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # Метрические единицы (градусы Цельсия)
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            data = response.json()

        # Сохраняем данные в базу данных для последующих запросов
        c.execute('INSERT INTO previous_requests VALUES (?, ?)', (city, response.text))
        conn.commit()

        return data


'''if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)'''