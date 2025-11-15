import { mapArtFromApi, mapArtToApi } from "./artMapper"

const BASE_URL = "http://127.0.0.1:8081/api"  // или куда у тебя сейчас смотрит API

// ======================
// Загрузить список артов
// ======================
export async function fetchArts() {
    const resp = await fetch(`${BASE_URL}/arts/`)
    if (!resp.ok) throw new Error("Failed to load arts")

    const data = await resp.json()
    return data.items.map(mapArtFromApi)
}

// ======================
// Получить один арт
// ======================
export async function fetchArt(id) {
    const resp = await fetch(`${BASE_URL}/arts/${id}/`)
    if (!resp.ok) throw new Error("Art not found")

    return mapArtFromApi(await resp.json())
}

// ======================
// Создать арт
// ======================
export async function createArt(art) {
    const body = mapArtToApi(art)

    const resp = await fetch(`${BASE_URL}/arts/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    })

    if (!resp.ok) throw new Error("Failed to create")

    return mapArtFromApi(await resp.json())
}

// ======================
// Частичное обновление
// ======================
export async function updateArt(id, patch) {
    const resp = await fetch(`${BASE_URL}/arts/${id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mapArtToApi(patch)),
    })

    if (!resp.ok) throw new Error("Failed to update art")

    return mapArtFromApi(await resp.json())
}

// ======================
// Удаление
// ======================
export async function deleteArt(id) {
    const resp = await fetch(`${BASE_URL}/arts/${id}/`, {
        method: "DELETE",
    })

    if (!resp.ok) throw new Error("Failed to delete art")

    return true
}
