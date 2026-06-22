// src/api/artApi.js
import { mapArtToApi } from './artMappers'

const API_BASE = 'http://127.0.0.1:8081'
const ARTS_ENDPOINT = `${API_BASE}/api/arts/`

// Загрузка списка (если понадобится снаружи)
export async function fetchArts() {
    const resp = await fetch(ARTS_ENDPOINT, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })

    if (!resp.ok) {
        throw new Error(`Ошибка загрузки: ${resp.status} ${resp.statusText}`)
    }

    return await resp.json()
}

// Обновление существующего арта
export async function updateArt(art) {
    if (!art || !art.id) {
        throw new Error('updateArt: нет art или art.id')
    }

    const payload = mapArtToApi(art)

    const resp = await fetch(`${ARTS_ENDPOINT}${art.id}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
    })

    if (!resp.ok) {
        throw new Error(`Ошибка сохранения: ${resp.status} ${resp.statusText}`)
    }

    return await resp.json()
}

// Создание (на будущее)
export async function createArt(art) {
    const payload = mapArtToApi(art)

    const resp = await fetch(ARTS_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
    })

    if (!resp.ok) {
        throw new Error(`Ошибка создания: ${resp.status} ${resp.statusText}`)
    }

    return await resp.json()
}

// Удаление (на будущее)
export async function deleteArt(id) {
    const resp = await fetch(`${ARTS_ENDPOINT}${id}/`, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
        },
    })

    if (!resp.ok) {
        throw new Error(`Ошибка удаления: ${resp.status} ${resp.statusText}`)
    }

    return await resp.json()
}