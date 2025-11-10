import axios from 'axios'

const http = axios.create({
    baseURL: 'http://localhost:8081', // адрес твоего Django-сервера
    withCredentials: true,            // нужно, если используешь сессионную авторизацию
    headers: { 'Accept': 'application/json' }
})

// обработка ошибок
http.interceptors.response.use(
    (res) => res,
    (err) => {
        console.error('Ошибка API:', err?.response || err)
        throw err
    }
)

export default http
